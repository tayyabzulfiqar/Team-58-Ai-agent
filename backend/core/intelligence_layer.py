from __future__ import annotations

import re
from typing import Iterable


NEGATIVE_TERMS = {
    "no",
    "not",
    "low",
    "high",
    "poor",
    "weak",
    "bad",
    "slow",
    "declined",
    "dropped",
    "stagnant",
    "zero",
    "decreasing",
    "drop",
}

METRIC_TO_SIGNALS = {
    "conversion": {"conversion optimization"},
    "conversions": {"conversion optimization"},
    "sales": {"conversion optimization"},
    "revenue": {"conversion optimization", "lead generation"},
    "profit": {"conversion optimization"},
    "ctr": {"paid ads", "conversion optimization"},
    "cpc": {"paid ads"},
    "roi": {"paid ads", "conversion optimization"},
    "growth": {"lead generation", "conversion optimization"},
    "retention": {"retention"},
    "churn": {"retention"},
    "traffic": {"lead generation"},
}

INTENT_BASE_WEIGHTS = {
    "gap_pattern": 0.27,
    "loss_pattern": 0.23,
    "inefficiency_pattern": 0.21,
    "state_problem_pattern": 0.21,
    "implicit_problem_pattern": 0.08,
}

BEHAVIOR_PATTERNS = {
    "leave quickly": ("retention", "retention_loss"),
    "not buying": ("conversion optimization", "conversion_loss"),
    "not returning": ("retention", "retention_loss"),
    "no result": ("paid ads", "inefficiency"),
    "low conversion": ("conversion optimization", "conversion_loss"),
    "high traffic low sales": ("conversion optimization", "funnel_gap"),
    "users leaving": ("retention", "retention_loss"),
    "customers not staying": ("retention", "retention_loss"),
    "people disappear": ("retention", "retention_loss"),
}

BEHAVIOR_SIGNAL_MAP = {
    "leave quickly": "retention",
    "not buying": "conversion optimization",
    "not returning": "retention",
    "no result": "conversion optimization",
    "low conversion": "conversion optimization",
    "high traffic low sales": "conversion optimization",
    "users inactive": "retention",
}

BEHAVIOR_INTENT_MAP = {
    "leave quickly": "early churn",
    "disappear after signup": "onboarding failure",
    "click but not buy": "decision friction",
    "not returning": "retention breakdown",
    "no result from ads": "targeting inefficiency",
}

MICRO_INTENT_SIGNAL_MAP = {
    "early churn": "retention",
    "onboarding failure": "retention",
    "decision friction": "conversion optimization",
    "retention breakdown": "retention",
    "targeting inefficiency": "paid ads",
}

SIGNAL_SCOPE_TERMS = {
    "retention": {"onboarding", "engagement", "churn", "retention", "inactive", "return"},
    "conversion optimization": {"funnel", "decision", "checkout", "conversion", "sales", "purchase"},
    "paid ads": {"targeting", "creative", "roi", "cpc", "ads", "spend"},
    "lead generation": {"traffic", "acquisition", "channel", "reach", "lead", "visibility"},
}

VAGUE_ACTION_TERMS = {"improve", "optimize", "analyze", "enhance", "fix", "better"}
METRIC_CLUE_TERMS = {
    "ctr",
    "cpc",
    "roi",
    "traffic",
    "sales",
    "revenue",
    "profit",
    "conversion",
    "conversions",
    "retention",
    "churn",
}
TEMPORAL_CLUE_TERMS = (
    "today",
    "yesterday",
    "last week",
    "last month",
    "this week",
    "this month",
    "over time",
    "week over week",
    "month over month",
    "daily",
    "weekly",
    "monthly",
    "sudden",
    "suddenly",
    "gradual",
    "slowly",
    "increasing",
    "decreasing",
    "stable",
)

FUNNEL_PRIORITY = {
    "lead generation": 0.30,
    "conversion optimization": 0.24,
    "paid ads": 0.20,
    "retention": 0.12,
}

KNOWN_FAILURE_PATTERNS = {
    "users inactive": "retention",
    "not returning": "retention",
    "users leave": "retention",
    "leave quickly": "retention",
    "traffic but no sales": "conversion optimization",
    "high traffic low sales": "conversion optimization",
    "ad spend no result": "paid ads",
    "no reach": "lead generation",
}

HISTORIC_FALSE_MAPPINGS = {
    "users leave": {"conversion optimization", "lead generation"},
    "not returning": {"conversion optimization", "lead generation"},
    "traffic low": {"retention"},
    "no result from ads": {"retention", "lead generation"},
}

ROOT_CAUSE_MAP = {
    "conversion optimization": [
        "poor landing page",
        "weak offer",
        "pricing mismatch",
        "trust issue",
    ],
    "retention": [
        "bad onboarding",
        "low value delivery",
        "poor UX",
    ],
    "paid ads": [
        "bad targeting",
        "poor creatives",
        "wrong audience",
    ],
    "lead generation": [
        "low reach",
        "weak visibility",
        "poor positioning",
    ],
}

ACTION_MAP = {
    "conversion optimization": [
        "Check landing page clarity",
        "Analyze funnel drop-off",
        "Test new offers",
    ],
    "retention": [
        "Audit onboarding completion path",
        "Identify first-week churn triggers",
        "Improve activation milestones",
    ],
    "paid ads": [
        "Improve targeting precision",
        "Refresh ad creatives and message fit",
        "Rebalance budget from weak segments",
    ],
    "lead generation": [
        "Expand high-intent reach channels",
        "Improve discovery content visibility",
        "Refine top-funnel audience filters",
    ],
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", str(text or "").lower()))


def compute_intent_weights(intent_patterns: Iterable[str]) -> list[dict]:
    matched = [name for name in INTENT_BASE_WEIGHTS if name in set(intent_patterns)]
    if not matched:
        return []
    total = sum(INTENT_BASE_WEIGHTS[name] for name in matched)
    if total <= 0:
        return []
    weighted = []
    for name in matched:
        weighted.append({"type": name, "weight": round(INTENT_BASE_WEIGHTS[name] / total, 3)})
    weighted.sort(key=lambda item: (-item["weight"], item["type"]))
    return weighted


def interpret_behavior_signals(canonical_text: str) -> list[dict]:
    text = canonical_text.lower()
    token_set = _tokens(text)
    entries = []
    inferred_signal_names = extract_behavior_signals(canonical_text)

    normalized_behavior = {
        "users leaving": any(x in text for x in ("users leaving", "customers leaving", "people leaving")),
        "customers not staying": any(x in text for x in ("not staying", "do not stay", "leave quickly")),
        "people disappear": any(x in text for x in ("disappear", "vanish", "not returning", "never come back")),
        "not buying": any(x in text for x in ("not buying", "no sales", "no purchase", "not converting")),
        "no result": any(x in text for x in ("no result", "no results", "zero roi", "roi is zero")),
        "low conversion": any(x in text for x in ("low conversion", "conversion rate is low", "conversions are low")),
        "high traffic low sales": ("traffic" in token_set and ("low sales" in text or "no sales" in text)),
        "not returning": any(x in text for x in ("not returning", "do not return", "never come back")),
        "leave quickly": any(x in text for x in ("leave quickly", "bounce quickly", "exit quickly")),
    }

    for phrase, (signal_name, tag) in BEHAVIOR_PATTERNS.items():
        matched = normalized_behavior.get(phrase, False) or (phrase in text)
        if not matched:
            continue
        entries.append(
            {
                "name": signal_name,
                "confidence": 0.78,
                "score": 78.0,
                "source": "pattern",
                "evidence": [f"behavior:{tag}", phrase],
                "mention_count": 2,
                "relationship_tag": tag,
                "relationship_weight": 0.15 if tag in {"funnel_gap", "retention_loss", "inefficiency"} else 0.0,
            }
        )

    for signal_name in inferred_signal_names:
        entries.append(
            {
                "name": signal_name,
                "confidence": 0.76,
                "score": 76.0,
                "source": "pattern",
                "evidence": ["behavior:inferred", f"inferred_signal:{signal_name}"],
                "mention_count": 1,
                "relationship_tag": "behavior_inference",
                "relationship_weight": 0.12,
            }
        )

    dedup = {}
    for item in entries:
        name = item["name"]
        current = dedup.get(name)
        if not current:
            dedup[name] = dict(item)
            continue
        current["confidence"] = max(current["confidence"], item["confidence"])
        current["score"] = max(current["score"], item["score"])
        current["mention_count"] = current.get("mention_count", 1) + 1
        current["evidence"] = sorted(set(current.get("evidence", []) + item.get("evidence", [])))[:8]
    return list(dedup.values())


def _signal_metric_weight(signal_name: str, metric_terms: set[str]) -> float:
    if not metric_terms:
        return 0.0
    mapped = 0
    for metric in metric_terms:
        if signal_name in METRIC_TO_SIGNALS.get(metric, set()):
            mapped += 1
    if mapped == 0:
        return 0.0
    return min(0.2, 0.08 + (0.04 * mapped))


def _signal_pattern_weight(signal: dict, intent_weight_map: dict[str, float]) -> float:
    source = signal.get("source", "semantic")
    if source in {"pattern", "blended"}:
        return 0.3
    if source in {"abstract", "lexicon"} and intent_weight_map:
        return min(0.3, 0.18 + (0.12 * max(intent_weight_map.values())))
    if source == "semantic":
        return 0.12
    return 0.10


def _overgeneralization_penalty(signal_name: str, text_tokens: set[str]) -> float:
    if signal_name == "conversion optimization":
        required = {"purchase", "checkout", "buy", "sales"}
        return 0.15 if not (required & text_tokens) else 0.0
    if signal_name == "retention":
        required = {"return", "stay", "active", "churn", "leave", "inactive"}
        return 0.15 if not (required & text_tokens) else 0.0
    return 0.0


def _failure_memory_weight(signal_name: str, canonical_text: str) -> float:
    text = canonical_text.lower()
    boost = 0.0
    for pattern, mapped_signal in KNOWN_FAILURE_PATTERNS.items():
        if pattern in text and mapped_signal == signal_name:
            boost = max(boost, 0.1)

    suppression = 0.0
    for pattern, bad_signals in HISTORIC_FALSE_MAPPINGS.items():
        if pattern in text and signal_name in bad_signals:
            suppression = min(-0.07, suppression)

    mismatch = 0.0
    for pattern, mapped_signal in KNOWN_FAILURE_PATTERNS.items():
        if pattern in text and mapped_signal != signal_name:
            mismatch = min(-0.04, mismatch)

    return boost + suppression + mismatch


def extract_micro_intent(text: str) -> dict:
    canonical = str(text or "").lower()
    token_set = _tokens(canonical)

    checks = {
        "leave quickly": any(x in canonical for x in ("leave quickly", "bounce quickly", "exit quickly")),
        "disappear after signup": any(x in canonical for x in ("disappear after signup", "drop after signup", "vanish after signup")),
        "click but not buy": any(x in canonical for x in ("click but not buy", "clicks but no purchase", "click no buy")),
        "not returning": any(x in canonical for x in ("not returning", "do not return", "never come back")),
        "no result from ads": any(x in canonical for x in ("no result from ads", "ad spend no result", "ads no result", "zero roi")),
    }

    best_phrase = ""
    for phrase in BEHAVIOR_INTENT_MAP:
        if checks.get(phrase, False) or phrase in canonical:
            best_phrase = phrase
            break

    if not best_phrase and "traffic" in token_set and ("low" in token_set or "declining" in token_set):
        best_phrase = "no result from ads"

    if not best_phrase:
        return {"micro_intent": "", "signal": "", "evidence": [], "strength": 0.0}

    micro_intent = BEHAVIOR_INTENT_MAP[best_phrase]
    signal = MICRO_INTENT_SIGNAL_MAP.get(micro_intent, "")
    return {
        "micro_intent": micro_intent,
        "signal": signal,
        "evidence": [best_phrase, f"micro_intent:{micro_intent}"],
        "strength": 0.82,
    }


def extract_behavior_signals(text: str) -> list[str]:
    canonical = str(text or "").lower()
    token_set = _tokens(canonical)
    inferred: list[str] = []

    normalized_behavior_checks = {
        "leave quickly": any(x in canonical for x in ("leave quickly", "bounce quickly", "exit quickly")),
        "not buying": any(x in canonical for x in ("not buying", "no sales", "no purchase", "not converting")),
        "not returning": any(x in canonical for x in ("not returning", "do not return", "never come back")),
        "no result": any(x in canonical for x in ("no result", "no results", "zero roi", "roi is zero")),
        "low conversion": any(x in canonical for x in ("low conversion", "conversion rate is low", "conversions are low")),
        "high traffic low sales": ("traffic" in token_set and ("low sales" in canonical or "no sales" in canonical)),
        "users inactive": any(x in canonical for x in ("users inactive", "inactive users", "stopped using")),
    }

    for phrase, mapped_signal in BEHAVIOR_SIGNAL_MAP.items():
        if normalized_behavior_checks.get(phrase, False) or phrase in canonical:
            inferred.append(mapped_signal)

    # Failure-aware boost: explicitly promote retention if leave-pattern appears.
    if any(x in canonical for x in ("users leave", "users leaving", "leave quickly", "not returning")):
        inferred.append("retention")

    return sorted(set(inferred))


def rank_signals(
    signals: list[dict],
    intent_weights: list[dict],
    metric_terms: list[str],
    canonical_text: str,
    intent_patterns: list[str],
) -> list[dict]:
    if not signals:
        return []
    intent_weight_map = {item["type"]: float(item["weight"]) for item in intent_weights}
    text_tokens = _tokens(canonical_text)
    metric_set = set(metric_terms)
    has_strong_pattern = any(name in intent_patterns for name in ("gap_pattern", "loss_pattern", "inefficiency_pattern", "state_problem_pattern"))

    ranked = []
    for signal in signals:
        base_conf = float(signal.get("confidence", 0.0))
        evidence = list(signal.get("evidence") or [])
        mention_count = int(signal.get("mention_count", max(1, len(evidence))))
        relationship_weight = float(signal.get("relationship_weight", 0.0))

        pattern_weight = _signal_pattern_weight(signal, intent_weight_map)
        metric_weight = _signal_metric_weight(signal["name"], metric_set)
        frequency_weight = 0.1 if mention_count > 1 else 0.0
        memory_weight = _failure_memory_weight(signal["name"], canonical_text)

        position_weight = 0.0
        if evidence:
            indexed = [canonical_text.find(str(ev).lower()) for ev in evidence if str(ev).strip()]
            indexed = [idx for idx in indexed if idx >= 0]
            if indexed and min(indexed) <= max(1, len(canonical_text) // 3):
                position_weight = 0.1

        negative_weight = 0.15 if (NEGATIVE_TERMS & text_tokens) else 0.0
        repetition_penalty = 0.15 if mention_count >= 4 else 0.0
        generalization_penalty = _overgeneralization_penalty(signal["name"], text_tokens)
        weak_pattern_penalty = 0.08 if (not has_strong_pattern and base_conf < 0.5) else 0.0

        final_score = base_conf + pattern_weight + metric_weight + relationship_weight + frequency_weight + position_weight + negative_weight + memory_weight
        final_score -= (repetition_penalty + generalization_penalty + weak_pattern_penalty)
        final_score = _clamp(final_score, 0.0, 1.0)
        calibrated_conf = _clamp(base_conf - generalization_penalty - (0.08 if repetition_penalty else 0.0), 0.0, 1.0)

        ranked_item = dict(signal)
        ranked_item["confidence"] = round(calibrated_conf, 3)
        ranked_item["rank_score"] = round(final_score, 3)
        ranked_item["weight"] = round(final_score, 3)
        ranked_item["relationship_tag"] = signal.get("relationship_tag", "")
        ranked_item["mention_count"] = mention_count
        ranked.append(ranked_item)

    ranked.sort(key=lambda item: (-item["rank_score"], -item["confidence"], -float(item.get("score", 0.0)), item["name"]))
    for idx, item in enumerate(ranked, start=1):
        item["rank"] = idx
    return ranked


def validate_signal_evidence(signals: list[dict]) -> list[dict]:
    validated = []
    for signal in signals:
        evidence = list(signal.get("evidence") or [])
        confidence = float(signal.get("confidence", 0.0))
        keyword_match = any(str(ev).lower().startswith(("pattern:", "semantic:", "lexicon:", "metric:", "rule:", "strong_rule:")) for ev in evidence)
        behavior_match = any("behavior:" in str(ev).lower() for ev in evidence)
        if not evidence:
            confidence -= 0.2
        elif not (keyword_match or behavior_match):
            confidence -= 0.12
        if confidence < 0.35:
            continue
        clone = dict(signal)
        clone["confidence"] = round(_clamp(confidence, 0.0, 1.0), 3)
        if not (keyword_match or behavior_match):
            clone["rank_score"] = round(_clamp(float(clone.get("rank_score", confidence)) - 0.08, 0.0, 1.0), 3)
        else:
            clone["rank_score"] = round(_clamp(float(clone.get("rank_score", confidence)), 0.0, 1.0), 3)
        validated.append(clone)
    validated.sort(key=lambda item: (-float(item.get("rank_score", 0.0)), -float(item.get("confidence", 0.0)), item["name"]))
    return validated


def detect_contradiction(canonical_text: str, signals: list[dict] | None = None) -> bool:
    text = canonical_text.lower()
    token_set = _tokens(text)

    low_traffic = ("traffic" in token_set and any(term in token_set for term in {"low", "declining", "dropping"})) or ("traffic low" in text)
    high_conversion = ("conversion" in token_set or "conversions" in token_set) and any(term in token_set for term in {"high", "strong"})
    low_sales = ("sales" in token_set and any(term in token_set for term in {"low", "zero"}))
    high_sales = ("sales" in token_set and any(term in token_set for term in {"high", "strong"})) or ("sales high" in text)
    low_revenue = ("revenue" in token_set and any(term in token_set for term in {"low", "declining", "drop", "dropped"})) or ("revenue low" in text)
    high_conversion_phrase = any(x in text for x in ("conversions high", "conversion high", "high conversions"))
    high_retention = ("retention" in token_set and "high" in token_set)
    leaving_users = any(x in text for x in ("users leaving", "not returning", "churn high", "users inactive"))

    if (low_traffic and (high_conversion or high_conversion_phrase)):
        return True
    if (low_sales and high_conversion_phrase):
        return True
    if high_sales and low_revenue:
        return True
    if (high_retention and leaving_users):
        return True
    if ("low traffic but conversions high" in text):
        return True
    if ("sales high but revenue low" in text):
        return True

    metric_terms = {"traffic", "conversion", "conversions", "sales", "revenue", "profit", "roi", "retention", "ctr", "cpc"}
    high_low_pairs = re.findall(r"high\s+([a-z]+)\s+but\s+low\s+([a-z]+)", text)
    low_high_pairs = re.findall(r"low\s+([a-z]+)\s+but\s+high\s+([a-z]+)", text)
    for left, right in high_low_pairs + low_high_pairs:
        if left != right and left in metric_terms and right in metric_terms:
            return True

    if signals:
        names = {item.get("name", "") for item in signals}
        if "retention" in names and any(x in text for x in ("high retention", "retention high")) and any(
            x in text for x in ("users leaving", "high churn", "not returning")
        ):
            return True
    return False


def detect_ambiguity(signals: list[dict], intent_patterns: list[str]) -> dict:
    if not signals:
        return {
            "is_ambiguous": True,
            "status": "needs_clarification",
            "reason": "Low confidence + vague input",
            "suggestion": "Ask user for more detail",
            "penalty": 0.25,
        }

    top_confidence = max(float(signal.get("rank_score", signal.get("confidence", 0.0))) for signal in signals)
    strong_pattern_present = any(
        pattern in intent_patterns
        for pattern in ("gap_pattern", "loss_pattern", "inefficiency_pattern", "state_problem_pattern")
    )

    if top_confidence < 0.4 and not strong_pattern_present:
        return {
            "is_ambiguous": True,
            "status": "needs_clarification",
            "reason": "Low confidence + vague input",
            "suggestion": "Ask user for more detail",
            "penalty": 0.25,
        }

    if top_confidence < 0.48 and len(signals) >= 3:
        return {
            "is_ambiguous": True,
            "status": "needs_clarification",
            "reason": "Competing low-confidence signals",
            "suggestion": "Ask user for specific business symptom",
            "penalty": 0.18,
        }

    return {
        "is_ambiguous": False,
        "status": "clear",
        "reason": "",
        "suggestion": "",
        "penalty": 0.0,
    }


def generate_dynamic_root_causes(signals: list[dict], text: str) -> list[str]:
    names = [signal["name"] for signal in signals]
    signal_set = set(names)
    canonical_text = str(text or "").lower()
    text_tokens = _tokens(canonical_text)
    causes: list[str] = []

    if "retention" in signal_set and ("leave" in text_tokens or "inactive" in text_tokens or "churn" in text_tokens):
        causes.extend(
            [
                "Users are not reaching repeated-value milestones after activation",
                "Engagement cues are missing in the first sessions, causing silent drop-off",
                "Expectation set before signup does not match in-product experience",
            ]
        )
    if "conversion optimization" in signal_set and ("traffic" in text_tokens and "sales" in text_tokens):
        causes.extend(
            [
                "High-intent traffic is not seeing a clear value-to-action bridge on key pages",
                "Offer framing loses urgency between click and checkout steps",
                "Decision-stage proof elements are too weak for purchase confidence",
            ]
        )
    if "paid ads" in signal_set and ("roi" in text_tokens or "cpc" in text_tokens or "spend" in text_tokens):
        causes.extend(
            [
                "Budget is weighted toward segments with expensive clicks and weak buyer intent",
                "Ad promise and landing narrative mismatch lowers post-click quality",
                "Creative fatigue is reducing qualified engagement efficiency",
            ]
        )
    if "lead generation" in signal_set and ("traffic" in text_tokens or "reach" in text_tokens):
        causes.extend(
            [
                "Top-funnel visibility is low in channels where qualified demand exists",
                "Audience targeting is broad, diluting lead quality at source",
                "Acquisition content does not map tightly to specific problem intent",
            ]
        )

    # If dynamic coverage is weak, fall back to stable map for compatibility.
    if len(causes) < 3:
        for signal_name in names[:3]:
            causes.extend(ROOT_CAUSE_MAP.get(signal_name, []))

    deduped = []
    seen = set()
    for cause in causes:
        key = cause.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cause)
    return deduped[:3]


def _dynamic_root_causes(signals: list[dict], canonical_text: str) -> list[str]:
    names = [signal["name"] for signal in signals]
    strong_pattern_detected = any(
        str(item.get("source", "")).lower() in {"pattern", "blended"}
        or any("behavior:" in str(ev).lower() for ev in list(item.get("evidence") or []))
        for item in signals
    )
    if strong_pattern_detected:
        return generate_dynamic_root_causes(signals, canonical_text)

    # Fallback path retains previous deterministic behavior when patterns are weak.
    causes: list[str] = []
    for signal_name in names[:3]:
        causes.extend(ROOT_CAUSE_MAP.get(signal_name, []))
    deduped = []
    seen = set()
    for cause in causes:
        key = cause.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cause)
    return (deduped or ["weak offer", "poor positioning", "low value delivery"])[:3]


def build_reasoning_chain(signals: list[dict], canonical_text: str, confidence: float) -> list[str]:
    signal_names = [item.get("name", "") for item in signals if item.get("name")]
    signal_set = set(signal_names)
    text = str(canonical_text or "").lower()
    precision_mode = "high" if confidence > 0.75 else ("low" if confidence < 0.5 else "medium")

    if precision_mode == "low":
        return [
            "Observed behavior is present but signal evidence is limited",
            "Underlying mechanism cannot be isolated with high reliability yet",
            "Root cause explanation remains tentative due to ambiguous context",
            "Business impact is possible; clarify KPI direction before optimization",
        ]

    if "retention" in signal_set:
        observed = "Users are leaving quickly or not returning after initial visits"
        mechanism = "Early product value is not reinforced, so engagement decays across sessions"
        root = "Activation-to-habit transition is weak, likely from onboarding and re-engagement gaps"
        impact = "Retention erosion compounds revenue drag by shrinking repeat usage and lifetime value"
        if precision_mode == "medium":
            return [observed, mechanism, root, impact]
        return [
            observed,
            mechanism,
            root,
            impact,
        ]

    if "conversion optimization" in signal_set:
        observed = "Traffic activity is not translating into expected purchases"
        mechanism = "Decision-stage friction reduces completion from intent to transaction"
        root = "Offer clarity, trust proof, or checkout flow is mismatched to visitor expectations"
        impact = "Revenue efficiency drops because acquisition effort does not convert proportionally"
        if "high traffic low sales" in text:
            root = "High-volume sessions are entering the funnel, but landing-to-checkout continuity is weak"
        return [observed, mechanism, root, impact]

    if "paid ads" in signal_set:
        return [
            "Paid spend is active but results are underperforming",
            "Traffic quality and message alignment are not matching buyer intent",
            "Targeting and creative strategy are emphasizing low-yield segments",
            "Budget efficiency declines, reducing profitable growth velocity",
        ]

    if "lead generation" in signal_set:
        return [
            "Lead volume or reach is below expected pipeline needs",
            "Awareness channels are not consistently pulling qualified demand",
            "Audience positioning is too broad to convert attention into leads",
            "Pipeline coverage weakens, increasing downstream revenue risk",
        ]

    return [
        "Observed behavior indicates a measurable business performance issue",
        "Underlying mechanism suggests stage-level friction in the current journey",
        "Root cause explanation is bounded to the detected signals only",
        "Business impact will persist until the primary signal is resolved",
    ]


def detect_temporal_context(text: str) -> dict:
    canonical = str(text or "").lower()
    token_set = _tokens(canonical)
    trend = "unknown"
    certainty = "low"
    change_type = "unknown"

    increasing_terms = {"increasing", "up", "growing", "improving", "rising"}
    decreasing_terms = {"decreasing", "down", "dropping", "declining", "falling"}
    stable_terms = {"stable", "flat", "unchanged", "same"}

    if increasing_terms & token_set:
        trend = "increasing"
        certainty = "medium"
    elif decreasing_terms & token_set:
        trend = "decreasing"
        certainty = "medium"
    elif stable_terms & token_set:
        trend = "stable"
        certainty = "medium"

    sudden_terms = {"sudden", "suddenly", "overnight", "abrupt", "spike"}
    gradual_terms = {"gradual", "slowly", "over time", "month by month", "week by week"}
    if sudden_terms & token_set:
        change_type = "sudden"
        certainty = "high" if trend != "unknown" else "medium"
    elif any(x in canonical for x in gradual_terms):
        change_type = "gradual"
        certainty = "high" if trend != "unknown" else "medium"

    return {"trend": trend, "certainty": certainty, "change": change_type}


def detect_business_stage(text: str, signals: list[dict], metrics: list[str] | None = None) -> str:
    canonical = str(text or "").lower()
    metric_set = set(metrics or [])
    signal_names = {str(item.get("name", "")) for item in signals}

    if any(x in canonical for x in ("new product", "just launched", "mvp", "finding fit", "validation")):
        return "early / validation"
    if any(x in canonical for x in ("scale", "growth", "acquisition", "expanding", "ramp")):
        return "growth / scaling"
    if any(x in canonical for x in ("optimize", "efficiency", "mature", "saturation", "incremental")):
        return "mature / optimization"

    if "retention" in signal_names and (metric_set & {"retention", "churn"}):
        return "mature / optimization"
    if "lead generation" in signal_names and (metric_set & {"traffic", "growth"}):
        return "growth / scaling"
    return "early / validation"


def extract_evidence(canonical_text: str) -> dict:
    text = str(canonical_text or "").lower()
    token_set = _tokens(text)

    behavioral = []
    temporal = []
    metric = []

    behavior_phrases = list(BEHAVIOR_PATTERNS.keys()) + list(BEHAVIOR_INTENT_MAP.keys())
    for phrase in behavior_phrases:
        if phrase in text:
            behavioral.append(phrase)

    behavior_markers = (
        "users leaving",
        "not returning",
        "not buying",
        "click but",
        "drop after signup",
        "no result",
        "low sales",
        "high traffic low sales",
    )
    for marker in behavior_markers:
        if marker in text:
            behavioral.append(marker)

    for phrase in TEMPORAL_CLUE_TERMS:
        if phrase in text:
            temporal.append(phrase)

    for term in sorted(METRIC_CLUE_TERMS):
        if term in token_set:
            metric.append(term)

    def _dedup_keep_order(items: list[str]) -> list[str]:
        out = []
        seen = set()
        for item in items:
            key = item.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out

    return {
        "behavioral_clues": _dedup_keep_order(behavioral)[:8],
        "temporal_clues": _dedup_keep_order(temporal)[:8],
        "metric_clues": _dedup_keep_order(metric)[:8],
    }


def build_signal_specific_reasoning(
    signal: str,
    text: str,
    confidence: float,
    micro_intent: str = "",
    temporal_context: dict | None = None,
    business_stage: str = "",
) -> list[str]:
    signal_name = str(signal or "")
    canonical = str(text or "").lower()
    precision_mode = "high" if confidence > 0.75 else ("low" if confidence < 0.5 else "medium")
    micro_clause = f" with micro-intent '{micro_intent}'" if micro_intent else ""
    temporal = temporal_context or {"trend": "unknown", "certainty": "low", "change": "unknown"}
    trend_clause = f"trend={temporal.get('trend', 'unknown')} certainty={temporal.get('certainty', 'low')}"
    stage_clause = f"stage={business_stage}" if business_stage else "stage=unknown"

    if signal_name == "retention":
        chain = [
            f"Observation: Users are not sustaining activity{micro_clause}; {trend_clause}",
            f"User Behavior: Post-signup engagement decays before habit formation ({stage_clause})",
            "System Weakness: Onboarding and lifecycle triggers fail to reinforce recurring value",
            "Business Impact: Churn pressure reduces repeat revenue and compresses lifetime value",
        ]
    elif signal_name == "conversion optimization":
        checkout_hint = "Checkout-stage friction is visible" if any(x in canonical for x in ("checkout", "cart", "payment")) else "Decision-stage friction is visible"
        chain = [
            f"Observation: Funnel traffic is present but purchase completion is weak{micro_clause}; {trend_clause}",
            f"User Behavior: Prospects click and evaluate but abandon before conversion ({stage_clause})",
            f"System Weakness: {checkout_hint.lower()} due to weak value-to-proof continuity",
            "Business Impact: Conversion leakage lowers revenue yield per visitor and per campaign",
        ]
    elif signal_name == "paid ads":
        chain = [
            f"Observation: Paid performance underdelivers against spend{micro_clause}; {trend_clause}",
            f"User Behavior: Ad responders show weak purchase intent quality ({stage_clause})",
            "System Weakness: Targeting and creative-message fit are misaligned with conversion intent",
            "Business Impact: ROI compression increases CAC pressure and slows profitable growth",
        ]
    elif signal_name == "lead generation":
        chain = [
            f"Observation: Qualified demand intake is below pipeline need{micro_clause}; {trend_clause}",
            f"User Behavior: Discovery volume is insufficient or poorly qualified ({stage_clause})",
            "System Weakness: Acquisition channel mix and message positioning underperform on intent quality",
            "Business Impact: Pipeline shortfall limits downstream conversion and revenue potential",
        ]
    else:
        chain = [
            f"Observation: Measurable performance issue detected; {trend_clause}",
            "User Behavior: Behavior shift is visible but not sufficiently attributable",
            "System Weakness: Mechanism cannot be isolated without stronger evidence",
            "Business Impact: Outcome risk persists until causal clarity improves",
        ]

    if precision_mode == "low":
        chain[0] = f"{chain[0]} with limited evidence"
        chain[2] = "Root cause remains tentative; more context is required for reliable diagnosis"
        chain[3] = f"{chain[3]}; needs_clarification"
    return chain


def _enforce_reasoning_guardrail(primary_signal: str, reasoning_chain: list[str], text: str, confidence: float, micro_intent: str = "") -> list[str]:
    if not primary_signal:
        return reasoning_chain
    allowed = SIGNAL_SCOPE_TERMS.get(primary_signal, set())
    if not allowed:
        return reasoning_chain
    joined = " ".join(reasoning_chain).lower()
    if allowed & _tokens(joined):
        return reasoning_chain
    return build_signal_specific_reasoning(primary_signal, text, confidence, micro_intent=micro_intent)


def build_adaptive_reasoning(signals: list[dict], text: str, confidence: float) -> list[str]:
    if not signals:
        return [
            "Observed behavior is not sufficiently grounded",
            "Mechanism cannot be established from current evidence",
            "Root cause explanation would be speculative",
            "Business impact assessment requires clarification first",
        ]
    primary_signal = str(signals[0].get("name", ""))
    micro = extract_micro_intent(text)
    temporal = detect_temporal_context(text)
    stage = detect_business_stage(text, signals, metrics=[])
    chain = build_signal_specific_reasoning(
        primary_signal,
        text,
        confidence,
        micro_intent=micro.get("micro_intent", ""),
        temporal_context=temporal,
        business_stage=stage,
    )
    return _enforce_reasoning_guardrail(primary_signal, chain, text, confidence, micro_intent=micro.get("micro_intent", ""))


def resolve_signal_conflicts(signals: list[dict], metrics: list[str], patterns: list[str]) -> dict:
    if not signals:
        return {"primary_signal": "", "secondary_signals": [], "ordered_signals": [], "conflict_scores": {}}

    metric_set = set(metrics or [])
    pattern_set = set(patterns or [])
    scored: list[tuple[float, dict]] = []
    score_map: dict[str, float] = {}
    for signal in signals:
        name = str(signal.get("name", ""))
        metric_alignment = _signal_metric_weight(name, metric_set)
        source = str(signal.get("source", ""))
        evidence = list(signal.get("evidence") or [])
        behavior_strength = 0.14 if any("behavior:" in str(ev).lower() for ev in evidence) else 0.0
        source_strength = 0.12 if source in {"pattern", "blended"} else (0.08 if source in {"abstract", "lexicon"} else 0.04)
        pattern_strength = min(0.25, source_strength + behavior_strength + min(0.04, 0.01 * len(pattern_set)))
        funnel_priority = FUNNEL_PRIORITY.get(name, 0.0)
        confidence_score = float(signal.get("rank_score", signal.get("confidence", 0.0)))
        final_score = round((metric_alignment * 0.45) + (pattern_strength * 0.25) + (funnel_priority * 0.15) + (confidence_score * 0.15), 4)
        scored.append((final_score, signal))
        if name:
            score_map[name] = final_score

    scored.sort(key=lambda item: (-item[0], -float(item[1].get("rank_score", item[1].get("confidence", 0.0))), item[1].get("name", "")))
    ordered_signals = [item[1] for item in scored]
    primary = ordered_signals[0].get("name", "")
    secondaries = [item.get("name", "") for item in ordered_signals[1:] if item.get("name")]
    return {
        "primary_signal": primary,
        "secondary_signals": secondaries[:4],
        "ordered_signals": ordered_signals,
        "conflict_scores": score_map,
    }


def build_confidence_breakdown(
    pattern_score: float,
    metric_score: float,
    behavior_score: float,
    ambiguity_penalty: float,
    final_confidence: float,
) -> dict:
    return {
        "pattern_score": round(_clamp(pattern_score, 0.0, 1.0), 3),
        "metric_score": round(_clamp(metric_score, 0.0, 1.0), 3),
        "behavior_score": round(_clamp(behavior_score, 0.0, 1.0), 3),
        "ambiguity_penalty": round(-abs(float(ambiguity_penalty)), 3),
        "final_confidence": round(_clamp(final_confidence, 0.0, 1.0), 3),
    }


def build_status_reason(
    canonical_text: str,
    primary_signal: str,
    status: str,
    contradiction_detected: bool,
    evidence: dict,
    secondary_signals: list[str] | None = None,
) -> str:
    if contradiction_detected:
        return "Conflicting metric directions detected; align timeframe and KPI definitions before committing a strategy"

    if status == "needs_clarification":
        missing_parts = []
        if not list(evidence.get("metric_clues") or []):
            missing_parts.append("Missing KPI metrics (conversion, sales, traffic, or ROI) needed to validate bottleneck depth")
        if not list(evidence.get("temporal_clues") or []):
            missing_parts.append("No temporal data available to confirm trend direction")
        if primary_signal and secondary_signals and len([s for s in secondary_signals if s]) >= 2:
            missing_parts.append(
                f"Ambiguous dominance between {primary_signal} and {', '.join([s for s in secondary_signals[:2] if s])}"
            )
        if not list(evidence.get("behavioral_clues") or []):
            missing_parts.append("Missing behavior-level clues to confirm user journey breakdown")
        if missing_parts:
            return "; ".join(missing_parts)
        return "Signal evidence is mixed across funnel stages and needs one dominant metric anchor"

    if not primary_signal:
        return "No dominant signal selected because metric and behavior evidence are not aligned to one bottleneck"

    behavior_count = len(list(evidence.get("behavioral_clues") or []))
    metric_count = len(list(evidence.get("metric_clues") or []))
    return f"Primary signal '{primary_signal}' selected with {behavior_count} behavioral clue(s) and {metric_count} metric clue(s)"


def _build_reasoning_chain(canonical_text: str, signals: list[dict], contradiction_detected: bool, precision_mode: str) -> list[str]:
    names = {item["name"] for item in signals}
    text = canonical_text.lower()

    if contradiction_detected:
        return [
            "Input contains conflicting performance directions",
            "This indicates inconsistent measurement context or timeframe",
            "Which makes direct optimization decisions unreliable",
            "Clarification is needed before committing strategy",
        ]

    if "lead generation" in names and "conversion optimization" in names:
        return [
            "Traffic/users are arriving but purchases are weak",
            "This indicates top-funnel activity without bottom-funnel conversion efficiency",
            "Which suggests landing page, offer, or trust-stage mismatch",
            "This leads to conversion loss despite acquisition effort",
        ]

    if "retention" in names:
        return [
            "Users are arriving but not staying active",
            "This indicates failure to deliver early recurring value",
            "Which suggests onboarding or expectation mismatch",
            "This leads to retention drop and compounding growth drag",
        ] if precision_mode == "high" else [
            "Users are not staying active",
            "Early value delivery appears weak",
            "Retention performance is likely at risk",
        ]

    if "paid ads" in names:
        return [
            "Spend is active but outcome efficiency is weak",
            "This indicates targeting or creative-message mismatch",
            "Which concentrates budget on low-conversion segments",
            "This leads to ROI inefficiency and slower growth",
        ] if precision_mode == "high" else [
            "Paid channels are inefficient",
            "Targeting or message alignment appears weak",
            "ROI performance is being constrained",
        ]

    return [
        "Detected business signals indicate a measurable problem",
        "Signal evidence suggests mechanism-level performance friction",
        "Outcome risk will persist until primary signal is addressed",
    ]


def _to_action_object(action: str, impact: str, difficulty: str, priority: int, reason: str) -> dict:
    return {
        "action": action.strip(),
        "impact": impact if impact in {"high", "medium", "low"} else "medium",
        "difficulty": difficulty if difficulty in {"high", "medium", "low"} else "medium",
        "priority": int(priority),
        "reason": reason.strip(),
    }


def _is_action_valid(action_item: dict, business_stage: str) -> bool:
    action_text = str(action_item.get("action", "")).strip()
    reason_text = str(action_item.get("reason", "")).strip()
    if not action_text:
        return False
    if not reason_text:
        return False
    tokens = action_text.lower().split()
    if len(tokens) < 3:
        return False
    if len(tokens) <= 4 and (set(tokens) & VAGUE_ACTION_TERMS):
        return False

    stage = str(business_stage or "")
    if stage == "early / validation" and "rebalance budget from weak segments" in action_text.lower():
        return False
    return True


def _token_overlap_score(a: str, b: str) -> float:
    ta = _tokens(a)
    tb = _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / float(len(ta | tb))


def _build_action_intelligence(signals: list[dict], canonical_text: str, root_causes: list[str] | None = None) -> list[dict]:
    if not signals:
        return [
            _to_action_object(
                "Provide KPI trend and funnel-stage detail before optimization",
                "medium",
                "low",
                1,
                "Prioritized because causal diagnosis cannot be validated without trend and stage evidence",
            ),
        ]

    stage = detect_business_stage(canonical_text, signals, metrics=[])
    primary_signal = str(signals[0].get("name", ""))
    action_pool: list[dict] = []

    signal_templates = {
        "retention": [
            _to_action_object(
                "Instrument onboarding completion drop-offs by step and cohort",
                "high",
                "medium",
                1,
                "Targets onboarding breakdown directly to isolate the churn mechanism driving retention loss",
            ),
            _to_action_object(
                "Launch first-week reactivation triggers for inactive users",
                "high",
                "medium",
                2,
                "Addresses early disengagement root cause by recovering users before churn hardens",
            ),
            _to_action_object(
                "Run activation message test for value realization in first session",
                "medium",
                "low",
                3,
                "Improves early value clarity to reduce drop-off caused by weak habit formation",
            ),
        ],
        "conversion optimization": [
            _to_action_object(
                "Audit checkout step abandonment and remove top friction point",
                "high",
                "medium",
                1,
                "Directly removes decision-stage bottleneck causing conversion leakage",
            ),
            _to_action_object(
                "Strengthen offer-proof block on high-traffic landing pages",
                "high",
                "low",
                2,
                "Improves trust and value proof where users currently abandon before purchase",
            ),
            _to_action_object(
                "Deploy one controlled funnel experiment on decision-stage copy",
                "medium",
                "medium",
                3,
                "Validates which message friction is depressing completion rate",
            ),
        ],
        "paid ads": [
            _to_action_object(
                "Cut low-intent segments and shift spend to top ROI cohorts",
                "high",
                "medium",
                1,
                "Removes budget drain from segments that cause ROI inefficiency",
            ),
            _to_action_object(
                "Refresh creative-to-landing message match for top campaigns",
                "high",
                "medium",
                2,
                "Corrects targeting-message mismatch that weakens post-click conversion quality",
            ),
            _to_action_object(
                "Set guardrail bids on high-CPC low-conversion ad groups",
                "medium",
                "low",
                3,
                "Rapidly limits spend on poor-performing units tied to acquisition inefficiency",
            ),
        ],
        "lead generation": [
            _to_action_object(
                "Prioritize channels with highest qualified traffic share",
                "high",
                "medium",
                1,
                "Focuses effort on acquisition sources that most directly close top-funnel quality gaps",
            ),
            _to_action_object(
                "Tighten acquisition messaging around problem-intent keywords",
                "high",
                "low",
                2,
                "Improves fit between audience intent and inbound lead quality",
            ),
            _to_action_object(
                "Create one high-intent lead magnet for weak top-funnel segments",
                "medium",
                "medium",
                3,
                "Adds a targeted capture asset to address lead-volume shortfall",
            ),
        ],
    }

    action_pool.extend(signal_templates.get(primary_signal, []))
    for secondary in [str(item.get("name", "")) for item in signals[1:3]]:
        action_pool.extend(signal_templates.get(secondary, [])[:1])

    validated = [item for item in action_pool if _is_action_valid(item, stage)]
    if not validated:
        validated = [
            _to_action_object(
                "Collect clearer metric and behavior context before prescribing strategy",
                "medium",
                "low",
                1,
                "Required because current evidence cannot tie one bottleneck to a validated mechanism",
            ),
        ]

    root_bundle = " ".join(root_causes or [])
    stage = detect_business_stage(canonical_text, signals, metrics=[])
    deduped: list[dict] = []
    seen = set()
    def _prio_score(item: dict) -> float:
        impact_weight = {"high": 3.0, "medium": 2.0, "low": 1.0}.get(str(item.get("impact", "medium")), 2.0)
        speed_weight = {"low": 2.0, "medium": 1.0, "high": 0.2}.get(str(item.get("difficulty", "medium")), 1.0)
        root_alignment = 3.0 * _token_overlap_score(str(item.get("action", "")), root_bundle)
        if root_alignment < 0.25:
            root_alignment += 2.0 * _token_overlap_score(str(item.get("reason", "")), root_bundle)
        stage_alignment = 1.0
        text = str(item.get("action", "")).lower()
        if stage == "early / validation" and any(x in text for x in ("rebalance budget", "guardrail bids")):
            stage_alignment = 0.5
        return impact_weight + speed_weight + root_alignment + stage_alignment

    for item in sorted(validated, key=lambda x: (-_prio_score(x), int(x.get("priority", 99)))):
        key = str(item.get("action", "")).lower().strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    for idx, item in enumerate(deduped, start=1):
        item["priority"] = idx
    return deduped[:3]


def build_confidence_reason(
    confidence: float = 0.0,
    patterns: float | list | None = None,
    metrics: float | list | None = None,
    ambiguity: float | dict | None = None,
    **kwargs,
) -> str:
    # Backward compatibility for older callers using named arguments.
    pattern_strength = float(kwargs.get("pattern_strength", patterns if isinstance(patterns, (float, int)) else 0.0))
    metric_score = float(kwargs.get("metric_score", metrics if isinstance(metrics, (float, int)) else 0.0))
    relationship_score = float(kwargs.get("relationship_score", 0.0))
    contradiction_detected = bool(kwargs.get("contradiction_detected", False))
    ambiguity_penalty = float(kwargs.get("ambiguity_penalty", ambiguity if isinstance(ambiguity, (float, int)) else 0.0))

    if contradiction_detected:
        return "Reduced due to contradiction in input signals despite detected patterns"
    pattern_label = "strong pattern" if pattern_strength >= 0.2 else ("moderate pattern" if pattern_strength >= 0.12 else "weak pattern")
    metric_label = "metric match present" if metric_score >= 0.1 else "limited metric match"
    ambiguity_label = "low ambiguity" if ambiguity_penalty <= 0.08 else ("moderate ambiguity penalty" if ambiguity_penalty <= 0.15 else "high ambiguity penalty")
    if confidence >= 0.75 and ambiguity_penalty <= 0.12:
        return f"High confidence due to {pattern_label} + {metric_label} + {ambiguity_label}"
    if confidence >= 0.5:
        return f"Moderate confidence due to {pattern_label} + {metric_label} with {ambiguity_label}"
    return f"Low confidence due to {pattern_label} + {metric_label} with {ambiguity_label}"


def build_reasoning(signals: list[dict], canonical_text: str, calibrated_confidence: float, contradiction_detected: bool) -> dict:
    if not signals:
        return {
            "reasoning": "Reasoning cannot be grounded from current evidence.",
            "reasoning_chain": [
                "Input does not provide grounded business behavior signals",
                "This prevents reliable mechanism-level diagnosis",
                "Clarification is required before causal inference",
            ],
            "root_causes": [],
            "actions": [
                _to_action_object(
                    "Ask for clearer KPI impact and channel context",
                    "medium",
                    "low",
                    1,
                    "Needed to link observed behavior to a measurable bottleneck before actioning",
                ),
                _to_action_object(
                    "Request the exact stage where results are dropping",
                    "medium",
                    "low",
                    2,
                    "Needed to isolate whether the primary failure is acquisition, conversion, or retention",
                ),
            ],
        }

    precision_mode = "high" if calibrated_confidence > 0.75 else ("low" if calibrated_confidence < 0.5 else "medium")
    if contradiction_detected:
        reasoning_chain = _build_reasoning_chain(canonical_text, signals, contradiction_detected, precision_mode)
    else:
        reasoning_chain = build_adaptive_reasoning(signals, canonical_text, calibrated_confidence)
    root_causes = generate_dynamic_root_causes(signals, canonical_text) if precision_mode != "low" else _dynamic_root_causes(signals, canonical_text)
    actions = _build_action_intelligence(signals, canonical_text, root_causes=root_causes)

    if precision_mode == "high":
        reasoning = "Causal chain indicates a grounded mechanism from observed behavior to business impact."
    elif precision_mode == "low":
        reasoning = "Signals are weak; reasoning is bounded and conservative. needs_clarification"
    else:
        reasoning = "Signals indicate a likely causal mechanism affecting business outcomes."

    return {
        "reasoning": reasoning,
        "reasoning_chain": reasoning_chain,
        "root_causes": root_causes[:3],
        "actions": actions[:3],
    }


def calibrate_confidence(
    signal_strength: float,
    intent_strength: float,
    pattern_score: float,
    relationship_score: float,
    ambiguity_penalty: float,
    normalization_confidence: float,
) -> float:
    base = signal_strength + intent_strength + pattern_score + relationship_score + (0.1 * normalization_confidence)
    final = base - ambiguity_penalty
    return round(_clamp(final, 0.3, 0.95), 3)
