from __future__ import annotations

import re


ALLOWED_SIGNALS = {
    "conversion optimization",
    "retention",
    "paid ads",
    "lead generation",
}

BUSINESS_HINTS = {
    "traffic",
    "users",
    "sales",
    "revenue",
    "profit",
    "conversion",
    "conversions",
    "ctr",
    "cpc",
    "roi",
    "growth",
    "retention",
    "churn",
    "ads",
    "campaign",
    "checkout",
    "purchase",
}

NEGATIVE_HINTS = {
    "no",
    "not",
    "low",
    "high",
    "slow",
    "weak",
    "poor",
    "drop",
    "dropped",
    "declined",
    "stagnant",
    "zero",
    "off",
    "wrong",
    "inconsistent",
}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", str(text or "").lower()))


def _is_vague_input(input_text: str) -> bool:
    token_set = _tokens(input_text)
    has_business = bool(token_set & BUSINESS_HINTS)
    has_negative = bool(token_set & NEGATIVE_HINTS)
    return not (has_business or has_negative)


def _normalize_signal_objects(signal_items: list[dict]) -> list[dict]:
    normalized = []
    for item in signal_items:
        name = str(item.get("name", "")).strip().lower()
        if not name:
            continue
        confidence = float(item.get("confidence", 0.0))
        normalized.append(
            {
                "name": name,
                "confidence": max(0.0, min(1.0, confidence)),
                "source": item.get("source", "rule"),
                "evidence": list(item.get("evidence", [])),
                "score": float(item.get("score", confidence * 100.0)),
                "mention_count": int(item.get("mention_count", 1)),
            }
        )
    return normalized


def _extract_reasoning_signals(input_text: str) -> list[dict]:
    text = str(input_text or "").lower()
    token_set = _tokens(text)
    inferred = []

    if any(term in text for term in ("purchase", "checkout", "buy", "sales", "conversion", "pricing", "offer", "funnel", "trust")):
        inferred.append(("conversion optimization", 0.72, ["semantic_business_problem"]))
    if any(term in text for term in ("return", "stay", "active", "churn", "leaving", "inactive", "stop using", "never come back")):
        inferred.append(("retention", 0.72, ["semantic_retention_problem"]))
    if any(term in text for term in ("ads", "campaign", "roi", "spend", "budget", "cpc", "cost")):
        inferred.append(("paid ads", 0.70, ["semantic_paid_problem"]))
    if any(term in text for term in ("traffic", "users", "growth", "lead", "visitors", "engagement")):
        inferred.append(("lead generation", 0.68, ["semantic_acquisition_problem"]))

    # implicit business problem fallback
    if not inferred and (token_set & BUSINESS_HINTS) and (token_set & NEGATIVE_HINTS):
        inferred.append(("conversion optimization", 0.55, ["implicit_business_problem"]))

    return [
        {
            "name": name,
            "confidence": confidence,
            "source": "reasoning",
            "evidence": evidence,
            "score": confidence * 100.0,
            "mention_count": 1,
        }
        for name, confidence, evidence in inferred
    ]


def _validate_reasoning_signals(reasoning_signals: list[dict], input_text: str) -> list[dict]:
    token_set = _tokens(input_text)
    validated = []
    for signal in reasoning_signals:
        name = signal["name"]
        if name not in ALLOWED_SIGNALS:
            continue

        confidence = float(signal["confidence"])
        if name == "conversion optimization" and not ({"purchase", "checkout", "buy", "sales", "conversion"} & token_set):
            confidence -= 0.15
        if name == "retention" and not ({"return", "stay", "active", "churn", "leave", "inactive"} & token_set):
            confidence -= 0.15
        signal = dict(signal)
        signal["confidence"] = max(0.0, min(1.0, confidence))
        signal["score"] = max(signal["score"], signal["confidence"] * 100.0)
        validated.append(signal)
    return [s for s in validated if s["confidence"] > 0.0]


def _merge_signals(rule_signals: list[dict], reasoning_signals: list[dict]) -> list[dict]:
    merged = {}
    for item in rule_signals + reasoning_signals:
        name = item["name"]
        if name not in ALLOWED_SIGNALS:
            continue
        current = merged.get(name)
        if not current:
            merged[name] = dict(item)
            continue
        if item["confidence"] > current["confidence"]:
            current["confidence"] = item["confidence"]
            current["score"] = max(current["score"], item["score"])
            current["source"] = item.get("source", current["source"])
        current["mention_count"] = int(current.get("mention_count", 1)) + int(item.get("mention_count", 1))
        current["evidence"] = sorted(set(list(current.get("evidence", [])) + list(item.get("evidence", []))))[:10]

    merged_list = list(merged.values())
    merged_list.sort(key=lambda item: (-item["confidence"], -item["score"], item["name"]))
    return [item for item in merged_list if item["confidence"] > 0.4]


def _calibrate_confidence(
    rule_confidence: float,
    reasoning_confidence: float,
    ambiguity: bool,
    weak_input: bool,
    signal_count: int,
) -> float:
    base = max(rule_confidence, reasoning_confidence)
    adjusted = base
    if ambiguity:
        adjusted -= 0.2
    if weak_input:
        adjusted -= 0.2
    if signal_count >= 2:
        adjusted += 0.1
    return max(0.3, min(0.95, round(adjusted, 3)))


def run_control_layer(input_text: str, rule_output: dict) -> dict:
    rule_signals = _normalize_signal_objects(list(rule_output.get("signals") or []))
    rule_signals = [item for item in rule_signals if item["name"] in ALLOWED_SIGNALS]
    rule_conf = float(rule_output.get("confidence", 0.0))
    intent_detected = bool(rule_output.get("intent_detected", False))
    ambiguous = bool(rule_output.get("ambiguous", False))
    weak_input = _is_vague_input(input_text)

    if rule_signals and rule_conf >= 0.75 and intent_detected and not ambiguous:
        merged_signals = _merge_signals(rule_signals, [])
        confidence = _calibrate_confidence(rule_conf, 0.0, ambiguous, weak_input, len(merged_signals))
        primary = merged_signals[0]["name"] if merged_signals else ""
        return {
            "signal_objects": merged_signals,
            "final_signals": [item["name"] for item in merged_signals],
            "primary_signal": primary,
            "confidence": confidence,
            "decision_path": "rule",
            "status": "success",
            "status_reason": "Strong deterministic rule output accepted",
        }

    if not rule_signals and weak_input:
        return {
            "signal_objects": [],
            "final_signals": [],
            "primary_signal": "",
            "confidence": 0.3,
            "decision_path": "clarification",
            "status": "needs_clarification",
            "status_reason": "No signals and vague input",
        }

    reasoning_candidates = _extract_reasoning_signals(input_text)
    reasoning_valid = _validate_reasoning_signals(reasoning_candidates, input_text)
    if weak_input:
        for item in reasoning_valid:
            item["confidence"] = min(item["confidence"], 0.5)
            item["score"] = min(item["score"], 50.0)

    if not reasoning_valid and not rule_signals:
        return {
            "signal_objects": [],
            "final_signals": [],
            "primary_signal": "",
            "confidence": 0.3,
            "decision_path": "clarification",
            "status": "needs_clarification",
            "status_reason": "Reasoning could not extract grounded business signals",
        }

    merged = _merge_signals(rule_signals, reasoning_valid)
    if not merged:
        return {
            "signal_objects": [],
            "final_signals": [],
            "primary_signal": "",
            "confidence": 0.3,
            "decision_path": "clarification",
            "status": "needs_clarification",
            "status_reason": "No valid merged signals after control validation",
        }

    reasoning_conf = max((item["confidence"] for item in reasoning_valid), default=0.0)
    confidence = _calibrate_confidence(rule_conf, reasoning_conf, ambiguous, weak_input, len(merged))
    path = "hybrid" if rule_signals and reasoning_valid else "reasoning"
    return {
        "signal_objects": merged,
        "final_signals": [item["name"] for item in merged],
        "primary_signal": merged[0]["name"],
        "confidence": confidence,
        "decision_path": path,
        "status": "success",
        "status_reason": "Signals validated and merged by control layer",
    }

