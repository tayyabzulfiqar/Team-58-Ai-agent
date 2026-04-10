from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


FAILURE_MEMORY_PATH = Path(__file__).resolve().parents[1] / "data" / "failure_memory.jsonl"


def _append_failure_memory(input_text: str, broken_layer: str, reason: str) -> None:
    try:
        FAILURE_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "input": str(input_text or ""),
            "broken_layer": str(broken_layer or "validator"),
            "reason": str(reason or "unknown validation failure"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with FAILURE_MEMORY_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        return


def validate_output(payload: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a dictionary"]

    expected = {"domain", "validation_type", "signals", "clusters", "top_cluster", "confidence"}
    optional = {
        "primary_signal",
        "secondary_signals",
        "intent_weights",
        "reasoning",
        "reasoning_chain",
        "root_causes",
        "actions",
        "evidence",
        "ambiguity",
        "status",
        "status_reason",
        "status_suggestion",
        "decision_path",
        "final_signals",
        "confidence_breakdown",
        "confidence_reason",
        "contradiction_detected",
        "research_insights",
        "agent_flow",
        "main_problem",
        "research",
        "insights",
        "strategy",
        "campaign",
    }
    allowed = expected | optional
    keys = set(payload.keys())
    if not expected.issubset(keys):
        missing = sorted(expected - keys)
        extra = sorted(keys - allowed)
        if missing:
            errors.append(f"missing keys: {', '.join(missing)}")
        if extra:
            errors.append(f"extra keys: {', '.join(extra)}")
        return errors
    extra = sorted(keys - allowed)
    if extra:
        errors.append(f"extra keys: {', '.join(extra)}")
        return errors

    if payload["domain"] not in {"business", "general"}:
        errors.append("domain must be business/general")
    if payload["validation_type"] not in {"valid_strong", "valid_weak", "low_quality"}:
        errors.append("validation_type invalid")

    signals = payload["signals"]
    if not isinstance(signals, list):
        errors.append("signals must be list")
    else:
        seen = set()
        for signal in signals:
            if not isinstance(signal, dict):
                errors.append("signal must be object")
                continue
            required_signal_keys = {"name", "score", "confidence", "evidence", "source"}
            allowed_signal_keys = required_signal_keys | {"rank", "rank_score", "weight", "relationship_tag", "mention_count", "relationship_weight"}
            if not required_signal_keys.issubset(set(signal.keys())):
                errors.append("signal keys invalid")
                continue
            if set(signal.keys()) - allowed_signal_keys:
                errors.append("signal keys invalid")
                continue
            if not isinstance(signal["name"], str) or not signal["name"]:
                errors.append("signal name invalid")
            if not isinstance(signal["score"], (int, float)):
                errors.append("signal score invalid")
            if not isinstance(signal["confidence"], (int, float)) or not (0.0 <= float(signal["confidence"]) <= 1.0):
                errors.append("signal confidence invalid")
            if not isinstance(signal["evidence"], list):
                errors.append("signal evidence invalid")
            if signal["source"] not in {"pattern", "semantic", "blended", "lexicon", "abstract", "research"}:
                errors.append("signal source invalid")
            if "rank" in signal and (not isinstance(signal["rank"], int) or signal["rank"] < 1):
                errors.append("signal rank invalid")
            if "rank_score" in signal and (not isinstance(signal["rank_score"], (int, float)) or not (0.0 <= float(signal["rank_score"]) <= 1.0)):
                errors.append("signal rank_score invalid")
            if "weight" in signal and (not isinstance(signal["weight"], (int, float)) or not (0.0 <= float(signal["weight"]) <= 1.0)):
                errors.append("signal weight invalid")
            if "relationship_tag" in signal and not isinstance(signal["relationship_tag"], str):
                errors.append("signal relationship_tag invalid")
            if "mention_count" in signal and (not isinstance(signal["mention_count"], int) or signal["mention_count"] < 1):
                errors.append("signal mention_count invalid")
            if "relationship_weight" in signal and (not isinstance(signal["relationship_weight"], (int, float)) or not (0.0 <= float(signal["relationship_weight"]) <= 1.0)):
                errors.append("signal relationship_weight invalid")
            if signal["name"] in seen:
                errors.append("duplicate signal")
            seen.add(signal["name"])

    clusters = payload["clusters"]
    if not isinstance(clusters, list):
        errors.append("clusters must be list")
    else:
        known = {s["name"] for s in signals if isinstance(s, dict) and "name" in s}
        for cluster in clusters:
            if not isinstance(cluster, dict):
                errors.append("cluster must be object")
                continue
            if set(cluster.keys()) != {"name", "signals", "confidence"}:
                errors.append("cluster keys invalid")
                continue
            if not isinstance(cluster["name"], str) or not cluster["name"]:
                errors.append("cluster name invalid")
            if not isinstance(cluster["signals"], list) or len(cluster["signals"]) < 2:
                errors.append("cluster signals invalid")
            else:
                for name in cluster["signals"]:
                    if name not in known:
                        errors.append("cluster includes unknown signal")
            if not isinstance(cluster["confidence"], (int, float)) or not (0.0 <= float(cluster["confidence"]) <= 1.0):
                errors.append("cluster confidence invalid")

    if not isinstance(payload["top_cluster"], str):
        errors.append("top_cluster must be string")
    elif payload["top_cluster"]:
        names = [c["name"] for c in clusters if isinstance(c, dict) and "name" in c]
        if payload["top_cluster"] not in names:
            errors.append("top_cluster not in clusters")

    if not isinstance(payload["confidence"], (int, float)) or not (0.0 <= float(payload["confidence"]) <= 1.0):
        errors.append("confidence invalid")

    if "primary_signal" in payload and not isinstance(payload["primary_signal"], str):
        errors.append("primary_signal must be string")
    if "secondary_signals" in payload:
        if not isinstance(payload["secondary_signals"], list) or not all(isinstance(item, str) for item in payload["secondary_signals"]):
            errors.append("secondary_signals must be string list")
    if "intent_weights" in payload:
        if not isinstance(payload["intent_weights"], list):
            errors.append("intent_weights must be list")
        else:
            for item in payload["intent_weights"]:
                if not isinstance(item, dict):
                    errors.append("intent_weight item invalid")
                    continue
                if set(item.keys()) != {"type", "weight"}:
                    errors.append("intent_weight keys invalid")
                    continue
                if not isinstance(item["type"], str):
                    errors.append("intent_weight type invalid")
                if not isinstance(item["weight"], (int, float)) or not (0.0 <= float(item["weight"]) <= 1.0):
                    errors.append("intent_weight weight invalid")
    if "reasoning" in payload and not isinstance(payload["reasoning"], str):
        errors.append("reasoning must be string")
    if "reasoning_chain" in payload:
        if not isinstance(payload["reasoning_chain"], list) or not all(isinstance(item, str) for item in payload["reasoning_chain"]):
            errors.append("reasoning_chain must be string list")
    if "root_causes" in payload:
        if not isinstance(payload["root_causes"], list) or not all(isinstance(item, str) for item in payload["root_causes"]):
            errors.append("root_causes must be string list")
    if "ambiguity" in payload and not isinstance(payload["ambiguity"], bool):
        errors.append("ambiguity must be boolean")
    if "status" in payload and payload["status"] not in {"clear", "needs_clarification"}:
        errors.append("status invalid")
    if "status_reason" in payload and not isinstance(payload["status_reason"], str):
        errors.append("status_reason must be string")
    if "status_suggestion" in payload and not isinstance(payload["status_suggestion"], str):
        errors.append("status_suggestion must be string")
    if "decision_path" in payload and payload["decision_path"] not in {"rule", "reasoning", "hybrid", "clarification"}:
        errors.append("decision_path invalid")
    if "final_signals" in payload:
        if not isinstance(payload["final_signals"], list) or not all(isinstance(item, str) for item in payload["final_signals"]):
            errors.append("final_signals must be string list")
    if "confidence_reason" in payload and not isinstance(payload["confidence_reason"], str):
        errors.append("confidence_reason must be string")
    if "contradiction_detected" in payload and not isinstance(payload["contradiction_detected"], bool):
        errors.append("contradiction_detected must be boolean")
    if "research_insights" in payload:
        if not isinstance(payload["research_insights"], list) or not all(isinstance(item, str) for item in payload["research_insights"]):
            errors.append("research_insights must be string list")
    if "agent_flow" in payload:
        if not isinstance(payload["agent_flow"], list):
            errors.append("agent_flow must be list")
    if "main_problem" in payload and not isinstance(payload["main_problem"], str):
        errors.append("main_problem must be string")
    if "research" in payload:
        if not isinstance(payload["research"], list) or not all(isinstance(item, str) for item in payload["research"]):
            errors.append("research must be string list")
    if "insights" in payload and not isinstance(payload["insights"], str):
        errors.append("insights must be string")
    if "strategy" in payload and not isinstance(payload["strategy"], dict):
        errors.append("strategy must be object")
    if "campaign" in payload and not isinstance(payload["campaign"], dict):
        errors.append("campaign must be object")

    if payload.get("status") == "FAIL":
        _append_failure_memory(
            input_text=str(payload.get("input", "")),
            broken_layer=str(payload.get("broken_layer", "unknown")),
            reason=str(payload.get("status_reason", "status FAIL")),
        )
    elif errors:
        _append_failure_memory(
            input_text=str(payload.get("input", "")),
            broken_layer="output_validator",
            reason="; ".join(errors[:3]),
        )

    return errors
