from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parents[1]
FAILURE_LOG_PATH = BASE_DIR / "data" / "failure_log.json"


def _read_failure_log() -> list[dict]:
    if not FAILURE_LOG_PATH.exists():
        return []
    try:
        payload = json.loads(FAILURE_LOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def _write_failure_log(records: list[dict]) -> None:
    FAILURE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    FAILURE_LOG_PATH.write_text(json.dumps(records, ensure_ascii=True, indent=2), encoding="utf-8")


def log_failure(input_text: str, expected: str, actual: str, broken_layer: str) -> None:
    records = _read_failure_log()
    records.append(
        {
            "input": str(input_text or ""),
            "expected": str(expected or ""),
            "actual": str(actual or ""),
            "broken_layer": str(broken_layer or ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    _write_failure_log(records[-2000:])


def extract_failure_patterns() -> dict:
    records = _read_failure_log()
    phrases = []
    missed_signals = []
    domain_misses = []

    for item in records:
        text = str(item.get("input", "")).lower()
        phrases.extend(re.findall(r"[a-z]{3,}", text))

        expected = str(item.get("expected", "")).lower()
        actual = str(item.get("actual", "")).lower()
        broken = str(item.get("broken_layer", "")).lower()
        if "signal" in broken:
            missed_signals.append({"input": text, "expected": expected, "actual": actual})
        if "domain" in broken:
            domain_misses.append(text)

    frequent_words = [word for word, count in Counter(phrases).items() if count >= 3]
    return {
        "new_patterns": sorted(frequent_words)[:80],
        "new_mappings": missed_signals[-80:],
        "domain_misses": domain_misses[-80:],
    }


def apply_adaptive_updates(base_patterns: dict, base_semantic_hints: dict) -> tuple[dict, dict]:
    extracted = extract_failure_patterns()
    adaptive_patterns = {name: set(values) for name, values in base_patterns.items()}
    adaptive_hints = {name: set(values) for name, values in base_semantic_hints.items()}

    for mapping in extracted["new_mappings"]:
        text = mapping.get("input", "")
        expected = mapping.get("expected", "")
        if "conversion" in expected:
            adaptive_patterns.setdefault("conversion optimization", set()).update({text})
            adaptive_hints.setdefault("conversion optimization", set()).update({"conversion", "sales", "buying"})
        elif "retention" in expected:
            adaptive_patterns.setdefault("retention", set()).update({text})
            adaptive_hints.setdefault("retention", set()).update({"retention", "churn", "leave"})
        elif "lead" in expected or "traffic" in expected:
            adaptive_patterns.setdefault("lead generation", set()).update({text})
            adaptive_hints.setdefault("lead generation", set()).update({"users", "traffic", "visitors"})
        elif "ads" in expected:
            adaptive_patterns.setdefault("paid ads", set()).update({text})
            adaptive_hints.setdefault("paid ads", set()).update({"ads", "spend", "campaign"})
        elif "seo" in expected:
            adaptive_patterns.setdefault("seo", set()).update({text})
            adaptive_hints.setdefault("seo", set()).update({"seo", "rank", "google"})
        elif "content" in expected:
            adaptive_patterns.setdefault("content marketing", set()).update({text})
            adaptive_hints.setdefault("content marketing", set()).update({"content", "blog", "engagement"})

    return adaptive_patterns, adaptive_hints


def feedback_loop(input_text: str, expected: str, actual: str, broken_layer: str, base_patterns: dict, base_semantic_hints: dict) -> tuple[dict, dict]:
    log_failure(input_text=input_text, expected=expected, actual=actual, broken_layer=broken_layer)
    return apply_adaptive_updates(base_patterns=base_patterns, base_semantic_hints=base_semantic_hints)
