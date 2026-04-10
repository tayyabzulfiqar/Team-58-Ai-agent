from __future__ import annotations

import re
from difflib import SequenceMatcher
from pathlib import Path

from core.control_layer import run_control_layer
from core.intelligence_layer import build_reasoning
from core.intelligence_layer import build_status_reason
from core.intelligence_layer import calibrate_confidence
from core.intelligence_layer import build_confidence_breakdown
from core.intelligence_layer import compute_intent_weights
from core.conflict_resolver import resolve_signal_conflicts
from core.intelligence_layer import detect_contradiction
from core.intelligence_layer import detect_ambiguity
from core.intelligence_layer import extract_behavior_signals
from core.intelligence_layer import extract_evidence
from core.intelligence_layer import extract_micro_intent
from core.intelligence_layer import interpret_behavior_signals
from core.intelligence_layer import rank_signals
from core.intelligence_layer import resolve_signal_conflicts as resolve_reasoning_conflicts
from core.intelligence_layer import validate_signal_evidence
from core.intelligence_layer import build_confidence_reason
from core.learning_engine import apply_adaptive_updates
from core.learning_engine import log_failure
from core.normalization_layer import normalize_input
from core.thresholds import compute_thresholds


ALLOWED_SIGNALS = (
    "seo",
    "paid ads",
    "content marketing",
    "lead generation",
    "conversion optimization",
    "retention",
)

NOISE_WORDS = {"bro", "idk", "pls", "please", "yaar", "yar", "bhai", "literally"}

BASE_SIGNAL_PATTERNS = {
    "conversion optimization": {
        "no sales",
        "not buying",
        "no purchase",
        "no profit",
        "purchase not",
        "click but no purchase",
        "landing page weak",
        "pricing issue",
        "funnel issue",
    },
    "retention": {
        "do not stay",
        "users leaving",
        "do not return",
        "uninstall",
        "not using",
        "use not",
        "bounce high",
        "churn",
        "retention low",
    },
    "paid ads": {
        "ads",
        "ad spend",
        "money is being spent",
        "no result",
        "no benefit",
        "campaign",
        "cpc high",
    },
    "lead generation": {
        "no users",
        "more users",
        "no traffic",
        "need traffic",
        "no visitors",
        "lead issue",
        "funnel issue",
    },
    "seo": {
        "seo",
        "not ranking",
        "rank on google",
        "search traffic",
        "organic traffic",
    },
    "content marketing": {
        "content",
        "blog",
        "articles",
        "engagement low",
        "reach low",
    },
}

CROSS_LINGUAL_LEXICON = {
    "retention": {
        "wapas nahi aate",
        "uninstall kar dete",
        "use nahi karte",
        "rukte nahi",
        "chod dete",
        "gayab ho jate",
    },
    "conversion optimization": {
        "purchase nahi",
        "buy nahi",
        "click but no purchase",
        "sale nahi",
        "profit nahi",
    },
    "paid ads": {
        "paisa ja raha result nahi",
        "ads chal rahe fayda nahi",
        "ads pe paisa lag raha",
    },
}

ABSTRACT_CONCEPT_MAP = {
    "pricing issue": ("conversion optimization",),
    "funnel issue": ("conversion optimization", "lead generation"),
    "trust issue": ("conversion optimization", "retention"),
    "landing page weak": ("conversion optimization",),
    "engagement low": ("retention",),
}

SEMANTIC_HINTS = {
    "conversion optimization": {"buy", "purchase", "sales", "conversion", "checkout", "profit", "pricing", "landing"},
    "retention": {"stay", "return", "uninstall", "churn", "retention", "inactive", "bounce", "leave", "use"},
    "paid ads": {"ads", "campaign", "spend", "money", "result", "cpc", "roi"},
    "lead generation": {"users", "traffic", "visitors", "lead", "reach", "growth"},
    "seo": {"seo", "ranking", "rank", "google", "search", "organic"},
    "content marketing": {"content", "blog", "article", "engagement", "audience"},
}

BUSINESS_SEMANTIC_SPACE = {
    "users",
    "traffic",
    "sales",
    "conversion",
    "retention",
    "churn",
    "ads",
    "campaign",
    "seo",
    "content",
    "lead",
    "profit",
    "pricing",
    "funnel",
    "website",
    "app",
    "business",
    "growth",
}

GENERAL_SEMANTIC_SPACE = {
    "cricket",
    "study",
    "health",
    "weather",
    "music",
    "movie",
    "travel",
}

STATE_PROBLEM_PATTERN = {
    "description": "Metric or state is abnormal",
    "indicators": [
        r".+\s+(is|are)\s+(low|high|very low|very high)",
        r".+\s+(dropped|declined|decreased|reduced)",
        r".+\s+(stopped|stagnant|not growing)",
        r".+\s+(too high|too low)",
        r".+\s+(poor|weak|bad|slow)",
    ],
    "maps_to_signals": [
        "conversion optimization",
        "retention",
        "lead generation",
        "paid ads",
    ],
    "confidence_boost": 0.35,
}

BUSINESS_METRICS = {
    "conversion",
    "conversions",
    "revenue",
    "profit",
    "ctr",
    "cpc",
    "roi",
    "growth",
    "retention",
    "churn",
    "traffic",
    "sales",
}

BUSINESS_ENTITIES = {
    "users",
    "traffic",
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
    "lead",
    "leads",
    "website",
    "app",
    "business",
}

NEGATIVE_INDICATORS = {
    "no",
    "not",
    "low",
    "high",
    "drop",
    "dropped",
    "declined",
    "decreased",
    "reduced",
    "slow",
    "stagnant",
    "weak",
    "poor",
    "bad",
    "zero",
    "falling",
    "down",
    "decreasing",
    "decrease",
    "decline",
    "dropping",
    "stuck",
    "unstable",
    "inconsistent",
    "off",
    "wrong",
}

METRIC_SIGNAL_MAP = {
    "conversion": {"conversion optimization"},
    "conversions": {"conversion optimization"},
    "sales": {"conversion optimization"},
    "revenue": {"conversion optimization", "lead generation"},
    "profit": {"conversion optimization"},
    "ctr": {"paid ads", "conversion optimization"},
    "cpc": {"paid ads"},
    "roi": {"paid ads", "conversion optimization"},
    "retention": {"retention"},
    "churn": {"retention"},
    "growth": {"lead generation", "conversion optimization"},
    "traffic": {"lead generation"},
}

FAILURE_MEMORY_PATH = Path(__file__).resolve().parents[1] / "data" / "failure_memory.jsonl"


def validate_input_payload(payload) -> bool:
    return isinstance(payload, dict) and isinstance(payload.get("query"), str)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", str(text or "").lower())


def _is_random_text(text: str) -> bool:
    token_list = _tokens(text)
    if not token_list:
        return True
    if len(token_list) == 1:
        token = token_list[0]
        if token.isalpha() and len(token) >= 8 and len(set(token)) >= 7:
            return True
    return False


def validate_input(query: str) -> str:
    token_set = {t for t in _tokens(query) if t not in NOISE_WORDS}
    if not token_set:
        return "low_quality"
    if _is_random_text(query):
        return "low_quality"
    if len(token_set) >= 4:
        return "valid_strong"
    return "valid_weak"


def _segments(text: str) -> list[str]:
    parts = re.split(r"\bbut\b|\band\b|,|;|\bvs\b|\bor\b|\/", text.lower())
    chunks = [part.strip() for part in parts if part and part.strip()]
    return [text.lower()] + chunks


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _infer_metric_signals(text: str, token_set: set[str]) -> list[str]:
    inferred = set()
    for metric, mapped_signals in METRIC_SIGNAL_MAP.items():
        if metric in text or metric in token_set:
            inferred.update(mapped_signals)
    return sorted(inferred)


def _layer1_universal_intent_extraction(canonical_text: str) -> dict:
    text = canonical_text.lower()
    segments = _segments(text)
    token_set = set(_tokens(text))

    intent_patterns = []
    behavior_signals = []
    abstract_terms = []
    mapped_signals = []
    metric_terms = sorted({metric for metric in BUSINESS_METRICS if metric in text or metric in token_set})

    gap_regexes = (
        r"\b(.+?)\bbut\b(.+?)\bnot\b",
        r"\bclick\b.*\bno purchase\b",
        r"\btraffic\b.*\bno sales\b",
    )
    for pattern in gap_regexes:
        if re.search(pattern, text):
            intent_patterns.append("gap_pattern")
            break

    behavior_terms = (
        "leave",
        "leaving",
        "do not stay",
        "not staying",
        "do not return",
        "not returning",
        "never come back",
        "inactive",
        "drop off",
        "dropping off",
        "disappear",
        "stopped using",
        "stop using",
        "uninstall",
        "churn",
        "bounce",
    )
    if any(term in text for term in behavior_terms):
        intent_patterns.append("loss_pattern")
        behavior_signals.append("retention_loss")

    if any(term in text for term in ("money is being spent", "paisa", "ad spend", "time spent", "no result", "no benefit")):
        intent_patterns.append("inefficiency_pattern")
        behavior_signals.append("inefficient_spend")

    state_hits = []
    state_terms = {"low", "high", "dropping", "declining", "stagnant", "slow", "weak", "poor", "decreasing", "reduced"}
    for indicator in STATE_PROBLEM_PATTERN["indicators"]:
        if re.search(indicator, text):
            state_hits.append(indicator)
    if state_hits or (token_set & BUSINESS_ENTITIES and token_set & state_terms):
        intent_patterns.append("state_problem_pattern")
        behavior_signals.append("metric_state_problem")
        metric_inferred_signals = _infer_metric_signals(text, token_set)
        if metric_inferred_signals:
            mapped_signals.extend(metric_inferred_signals)
        else:
            mapped_signals.extend(STATE_PROBLEM_PATTERN["maps_to_signals"][:2])

    has_business_entities = bool(token_set & BUSINESS_ENTITIES)
    has_negative_indicators = bool(token_set & NEGATIVE_INDICATORS)
    if not intent_patterns and has_business_entities and has_negative_indicators:
        intent_patterns.append("implicit_problem_pattern")
        behavior_signals.append("implicit_business_problem")
        mapped_signals.extend(_infer_metric_signals(text, token_set))
        if not mapped_signals:
            mapped_signals.extend(["conversion optimization", "lead generation"])

    for concept in ABSTRACT_CONCEPT_MAP:
        if concept in text:
            abstract_terms.append(concept)
        else:
            for segment in segments:
                if _similarity(concept, segment) >= 0.82:
                    abstract_terms.append(concept)
                    break

    intent_confidence = 0.30
    if intent_patterns:
        intent_confidence += 0.20
    if metric_terms:
        intent_confidence += 0.10 + min(0.15, 0.03 * len(metric_terms))
    if "state_problem_pattern" in intent_patterns:
        intent_confidence += float(STATE_PROBLEM_PATTERN["confidence_boost"])
    elif "implicit_problem_pattern" in intent_patterns:
        intent_confidence += 0.22
    intent_confidence = round(min(1.0, intent_confidence), 3)

    return {
        "intent_patterns": sorted(set(intent_patterns)),
        "behavior_signals": sorted(set(behavior_signals)),
        "abstract_terms": sorted(set(abstract_terms)),
        "metric_terms": metric_terms,
        "mapped_signals": sorted(set(mapped_signals)),
        "state_problem_hits": state_hits,
        "intent_confidence": intent_confidence,
    }


def _layer2_pattern_signals(text: str, patterns: dict[str, set[str]]) -> dict:
    found = {}
    segments = _segments(text)
    for signal_name, signal_patterns in patterns.items():
        best_conf = 0.0
        evidence = []
        for segment in segments:
            for pattern in signal_patterns:
                if pattern in segment:
                    best_conf = max(best_conf, 0.84)
                    evidence.append(pattern)
                else:
                    ratio = _similarity(pattern, segment)
                    if ratio >= 0.84:
                        best_conf = max(best_conf, 0.72)
                        evidence.append(pattern)
        if evidence:
            found[signal_name] = {
                "confidence": round(min(1.0, best_conf), 3),
                "score": round(min(100.0, best_conf * 100.0), 2),
                "evidence": sorted(set(evidence))[:8],
            }
    return found


def _layer2_semantic_signals(text: str, semantic_hints: dict[str, set[str]]) -> dict:
    tokens = set(_tokens(text))
    found = {}
    for signal_name, hints in semantic_hints.items():
        overlap = sorted(tokens & hints)
        if not overlap:
            continue
        ratio = len(overlap) / max(1, len(hints))
        confidence = min(1.0, 0.46 + ratio * 0.68)
        found[signal_name] = {
            "confidence": round(confidence, 3),
            "score": round(min(100.0, confidence * 100.0), 2),
            "evidence": overlap[:8],
        }
    return found


def _layer2_lexicon_signals(text: str) -> list[dict]:
    signals = []
    lowered = text.lower()
    for signal_name, lexicon_phrases in CROSS_LINGUAL_LEXICON.items():
        matches = [phrase for phrase in lexicon_phrases if phrase in lowered]
        if matches:
            conf = min(1.0, 0.70 + 0.08 * len(matches))
            signals.append(
                {
                    "name": signal_name,
                    "confidence": round(conf, 3),
                    "score": round(conf * 100.0, 2),
                    "source": "lexicon",
                    "evidence": sorted(matches)[:8],
                }
            )
    return signals


def _layer2_abstract_signals(intent_payload: dict) -> list[dict]:
    signals = []
    base_intent_conf = float(intent_payload.get("intent_confidence", 0.60))
    for term in intent_payload["abstract_terms"]:
        mapped = ABSTRACT_CONCEPT_MAP.get(term, ())
        for signal_name in mapped:
            signals.append(
                {
                    "name": signal_name,
                    "confidence": round(max(0.70, base_intent_conf), 3),
                    "score": round(max(70.0, base_intent_conf * 100.0), 2),
                    "source": "abstract",
                    "evidence": [term],
                }
            )
    if "gap_pattern" in intent_payload["intent_patterns"]:
        signals.append(
            {
                "name": "conversion optimization",
                "confidence": 0.72,
                "score": 72.0,
                "source": "abstract",
                "evidence": ["gap_pattern"],
            }
        )
    if "inefficiency_pattern" in intent_payload["intent_patterns"]:
        signals.append(
            {
                "name": "paid ads",
                "confidence": 0.71,
                "score": 71.0,
                "source": "abstract",
                "evidence": ["inefficiency_pattern"],
            }
        )
    if "loss_pattern" in intent_payload["intent_patterns"]:
        signals.append(
            {
                "name": "retention",
                "confidence": 0.76,
                "score": 76.0,
                "source": "abstract",
                "evidence": ["loss_pattern"],
            }
        )

    if "state_problem_pattern" in intent_payload["intent_patterns"] or "implicit_problem_pattern" in intent_payload["intent_patterns"]:
        for signal_name in intent_payload.get("mapped_signals", []):
            signals.append(
                {
                    "name": signal_name,
                    "confidence": round(max(0.66, base_intent_conf), 3),
                    "score": round(max(66.0, base_intent_conf * 100.0), 2),
                    "source": "abstract",
                    "evidence": ["state_problem_pattern"],
                }
            )
    return signals


def _merge_signal_entries(entries: list[dict], signal_threshold: float, max_signals: int = 6) -> list[dict]:
    merged = {}
    for entry in entries:
        name = entry["name"]
        if name not in ALLOWED_SIGNALS:
            continue
        current = merged.get(name)
        if not current:
            merged[name] = {
                "name": name,
                "confidence": float(entry["confidence"]),
                "score": float(entry["score"]),
                "source": entry["source"],
                "evidence": list(entry["evidence"]),
                "mention_count": 1,
            }
            continue
        if entry["confidence"] > current["confidence"]:
            current["confidence"] = float(entry["confidence"])
            current["score"] = float(entry["score"])
            current["source"] = entry["source"]
        current["evidence"] = sorted(set(current["evidence"] + list(entry["evidence"])))[:10]
        current["mention_count"] = int(current.get("mention_count", 1)) + 1

    thresholded = [signal for signal in merged.values() if signal["confidence"] >= signal_threshold]
    thresholded.sort(key=lambda item: (-item["confidence"], -item["score"], item["name"]))
    return thresholded[:max_signals]


def _strong_rule_matches(canonical_text: str) -> list[dict]:
    text = canonical_text.lower()
    token_set = set(_tokens(text))
    matches = []

    if (("traffic" in token_set or "visitors" in token_set) and ("no sales" in text or "sales" in token_set and ("no" in token_set or "not" in token_set or "low" in token_set))):
        matches.append(
            {
                "name": "conversion optimization",
                "confidence": 0.9,
                "score": 90.0,
                "source": "pattern",
                "evidence": ["traffic + no sales"],
                "mention_count": 2,
            }
        )

    if (("users" in token_set or "customers" in token_set or "people" in token_set) and any(term in text for term in ("leaving", "not returning", "never come back", "inactive", "stop using", "disappear"))):
        matches.append(
            {
                "name": "retention",
                "confidence": 0.9,
                "score": 90.0,
                "source": "pattern",
                "evidence": ["users + leaving/not returning"],
                "mention_count": 2,
            }
        )

    if (any(term in text for term in ("spend", "spent", "budget", "cost", "ad spend")) and any(term in text for term in ("no result", "no results", "roi is zero", "not increasing", "negative roi"))):
        matches.append(
            {
                "name": "paid ads",
                "confidence": 0.9,
                "score": 90.0,
                "source": "pattern",
                "evidence": ["spend + no result"],
                "mention_count": 2,
            }
        )

    if (("no traffic" in text or "traffic" in token_set and "no" in token_set) or ("no reach" in text) or ("reach" in token_set and ("no" in token_set or "low" in token_set))):
        matches.append(
            {
                "name": "lead generation",
                "confidence": 0.88,
                "score": 88.0,
                "source": "pattern",
                "evidence": ["no traffic/no reach"],
                "mention_count": 2,
            }
        )

    return matches


def _relationship_enrichment(signals: list[dict], canonical_text: str) -> list[dict]:
    text = canonical_text.lower()
    names = {item["name"] for item in signals}
    enriched = []
    for item in signals:
        clone = dict(item)
        clone["relationship_tag"] = ""
        clone["relationship_weight"] = 0.0
        enriched.append(clone)

    def _apply(signal_name: str, tag: str):
        for item in enriched:
            if item["name"] == signal_name:
                item["relationship_tag"] = tag
                item["relationship_weight"] = 0.15

    if ("lead generation" in names and "conversion optimization" in names and "traffic" in text and any(term in text for term in ("low conversion", "conversions are low", "conversion rate is low", "no sales"))):
        _apply("conversion optimization", "funnel_gap")
    if ("lead generation" in names and "retention" in names and ("users" in text or "customers" in text) and any(term in text for term in ("leave", "leaving", "not returning", "inactive", "disappear"))):
        _apply("retention", "churn_pattern")
    if ("paid ads" in names and ("conversion optimization" in names or "lead generation" in names) and any(term in text for term in ("spend", "budget", "cost", "ad spend")) and any(term in text for term in ("revenue low", "revenue is low", "not increasing", "negative roi", "no result"))):
        _apply("paid ads", "inefficiency")

    return enriched


def _anti_hallucination_filter(signals: list[dict]) -> list[dict]:
    kept = []
    for item in signals:
        evidence = list(item.get("evidence") or [])
        confidence = float(item.get("confidence", 0.0))
        if not evidence:
            continue
        if confidence < 0.35:
            continue
        kept.append(item)
    return kept


def _apply_metric_aware_boost(entries: list[dict], canonical_text: str, intent_payload: dict) -> list[dict]:
    text = canonical_text.lower()
    metric_terms = set(intent_payload.get("metric_terms", []))
    if not metric_terms:
        metric_terms = {term for term in BUSINESS_METRICS if term in text}
    if not metric_terms:
        return entries

    boosted = []
    state_problem = "state_problem_pattern" in intent_payload.get("intent_patterns", [])
    for entry in entries:
        confidence = float(entry.get("confidence", 0.0))
        boost = 0.0
        signal_name = entry.get("name", "")

        if signal_name in {"conversion optimization", "retention", "lead generation", "paid ads"}:
            boost += 0.04
        if state_problem:
            boost += 0.07

        if signal_name == "conversion optimization" and metric_terms & {"conversion", "conversions", "sales", "revenue", "profit", "ctr"}:
            boost += 0.08
        elif signal_name == "retention" and metric_terms & {"retention", "churn"}:
            boost += 0.08
        elif signal_name == "lead generation" and metric_terms & {"traffic", "growth", "revenue"}:
            boost += 0.08
        elif signal_name == "paid ads" and metric_terms & {"cpc", "roi", "ctr"}:
            boost += 0.08

        if confidence < 0.56:
            boost += 0.04

        new_confidence = round(min(1.0, confidence + min(0.22, boost)), 3)
        new_score = round(min(100.0, max(float(entry.get("score", confidence * 100.0)), new_confidence * 100.0)), 2)

        boosted.append(
            {
                "name": entry["name"],
                "confidence": new_confidence,
                "score": new_score,
                "source": entry.get("source", "blended"),
                "evidence": list(entry.get("evidence", [])),
            }
        )
    return boosted


def _semantic_domain_fallback(text: str) -> float:
    token_set = set(_tokens(text))
    business_overlap = len(token_set & BUSINESS_SEMANTIC_SPACE)
    general_overlap = len(token_set & GENERAL_SEMANTIC_SPACE)
    total = max(1, len(token_set))
    raw = (business_overlap / total) - (general_overlap / total) + 0.45
    return round(max(0.0, min(1.0, raw)), 3)


def _layer3_domain_inference(signals: list[dict], canonical_text: str) -> tuple[str, float, str]:
    if signals:
        confidence = round(min(1.0, max(signal["confidence"] for signal in signals)), 3)
        return "business", confidence, "signal_derived"

    fallback_score = _semantic_domain_fallback(canonical_text)
    if fallback_score > 0.42:
        return "business", fallback_score, "semantic_fallback"
    return "general", fallback_score, "semantic_fallback"


def _layer4_intelligence(signals: list[dict]) -> tuple[list[dict], str]:
    signal_names = {signal["name"] for signal in signals}
    signal_lookup = {signal["name"]: signal for signal in signals}
    clusters = []

    recipes = [
        ("funnel problem", ("paid ads", "conversion optimization")),
        ("full funnel issue", ("lead generation", "conversion optimization")),
        ("growth problem", ("retention", "conversion optimization")),
        ("organic growth issue", ("seo", "content marketing")),
        ("bad targeting issue", ("paid ads", "retention")),
    ]

    for cluster_name, needs in recipes:
        if not all(name in signal_names for name in needs):
            continue
        confidence = round(sum(signal_lookup[name]["confidence"] for name in needs) / len(needs), 3)
        clusters.append({"name": cluster_name, "signals": list(needs), "confidence": confidence})

    if not clusters and len(signals) >= 2:
        top_two = sorted(signals, key=lambda s: (-s["confidence"], -s["score"], s["name"]))[:2]
        names = tuple(sorted([top_two[0]["name"], top_two[1]["name"]]))
        confidence = round((top_two[0]["confidence"] + top_two[1]["confidence"]) / 2.0, 3)
        clusters.append({"name": f"{names[0]} + {names[1]} reasoning cluster", "signals": [names[0], names[1]], "confidence": confidence})

    deduped = []
    seen = set()
    for cluster in sorted(clusters, key=lambda c: (-c["confidence"], c["name"])):
        key = (cluster["name"], tuple(cluster["signals"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cluster)

    top_cluster = deduped[0]["name"] if deduped else ""
    return deduped, top_cluster


def _build_reasoning_payload(
    canonical_text: str,
    signals: list[dict],
    intent_payload: dict,
    normalization_confidence: float,
) -> dict:
    intent_patterns = list(intent_payload.get("intent_patterns") or [])
    metric_terms = list(intent_payload.get("metric_terms") or [])
    evidence = extract_evidence(canonical_text)
    intent_weights = compute_intent_weights(intent_patterns)
    ranked_signals = rank_signals(
        signals=signals,
        intent_weights=intent_weights,
        metric_terms=metric_terms,
        canonical_text=canonical_text,
        intent_patterns=intent_patterns,
    )
    ranked_signals = validate_signal_evidence(ranked_signals)
    contradiction_detected = detect_contradiction(canonical_text, ranked_signals)
    ambiguity = detect_ambiguity(ranked_signals, intent_patterns)
    if contradiction_detected:
        ambiguity = {
            "is_ambiguous": True,
            "status": "needs_clarification",
            "reason": "Contradictory KPI directions detected",
            "suggestion": "Clarify KPI timeframe and measurement context",
            "penalty": max(float(ambiguity.get("penalty", 0.0)), 0.2),
        }

    raw_signal_strength = max((float(item.get("rank_score", 0.0)) for item in ranked_signals), default=0.0)
    signal_strength = min(0.45, raw_signal_strength * 0.45)
    intent_strength = min(0.2, float(intent_payload.get("intent_confidence", 0.0)) * 0.2)
    pattern_score = min(0.2, len(intent_patterns) * 0.05)
    relationship_score = min(0.15, max((float(item.get("relationship_weight", 0.0)) for item in ranked_signals), default=0.0))
    calibrated_confidence = calibrate_confidence(
        signal_strength=signal_strength,
        intent_strength=intent_strength,
        pattern_score=pattern_score,
        relationship_score=relationship_score,
        ambiguity_penalty=float(ambiguity.get("penalty", 0.0)),
        normalization_confidence=normalization_confidence,
    )
    if contradiction_detected:
        calibrated_confidence = round(max(0.3, calibrated_confidence - 0.08), 3)

    conflict_resolution = resolve_reasoning_conflicts(
        signals=ranked_signals,
        metrics=metric_terms,
        patterns=intent_patterns,
    )
    ordered_for_reasoning = list(conflict_resolution.get("ordered_signals") or ranked_signals)
    reasoning_payload = build_reasoning(
        signals=ordered_for_reasoning,
        canonical_text=canonical_text,
        calibrated_confidence=calibrated_confidence,
        contradiction_detected=contradiction_detected,
    )
    metric_score = min(0.18, len(metric_terms) * 0.03)
    behavior_score = min(
        0.2,
        0.06
        * sum(
            1
            for item in ranked_signals
            if any("behavior:" in str(ev).lower() for ev in list(item.get("evidence") or []))
        ),
    )
    confidence_breakdown = build_confidence_breakdown(
        pattern_score=pattern_score,
        metric_score=metric_score,
        behavior_score=behavior_score,
        ambiguity_penalty=float(ambiguity.get("penalty", 0.0)),
        final_confidence=calibrated_confidence,
    )
    confidence_reason = build_confidence_reason(
        confidence=calibrated_confidence,
        pattern_strength=pattern_score,
        metric_score=metric_score,
        relationship_score=relationship_score,
        ambiguity_penalty=float(ambiguity.get("penalty", 0.0)),
        contradiction_detected=contradiction_detected,
    )

    primary_signal = str(conflict_resolution.get("primary_signal") or (ranked_signals[0]["name"] if ranked_signals else ""))
    secondary_signals = list(conflict_resolution.get("secondary_signals") or [])
    if not secondary_signals:
        secondary_signals = [item["name"] for item in ranked_signals[1:] if float(item.get("rank_score", 0.0)) > 0.4][:4]

    if calibrated_confidence < 0.5 and ambiguity.get("status") == "clear":
        ambiguity = {
            "is_ambiguous": True,
            "status": "needs_clarification",
            "reason": "Missing dominant KPI evidence to validate the primary bottleneck",
            "suggestion": "Ask user for funnel stage and KPI context",
            "penalty": max(float(ambiguity.get("penalty", 0.0)), 0.15),
        }

    status_reason = build_status_reason(
        canonical_text=canonical_text,
        primary_signal=primary_signal,
        status=str(ambiguity.get("status", "clear")),
        contradiction_detected=contradiction_detected,
        evidence=evidence,
        secondary_signals=secondary_signals,
    )

    return {
        "ranked_signals": ranked_signals,
        "primary_signal": primary_signal,
        "secondary_signals": secondary_signals,
        "intent_weights": intent_weights,
        "reasoning": reasoning_payload["reasoning"],
        "reasoning_chain": list(reasoning_payload.get("reasoning_chain", [])),
        "root_causes": list(reasoning_payload.get("root_causes", [])),
        "actions": list(reasoning_payload.get("actions", [])),
        "evidence": evidence,
        "ambiguity": bool(ambiguity.get("is_ambiguous", False)),
        "status": ambiguity.get("status", "clear"),
        "status_reason": status_reason,
        "status_suggestion": ambiguity.get("suggestion", ""),
        "confidence": calibrated_confidence,
        "confidence_breakdown": confidence_breakdown,
        "confidence_reason": confidence_reason,
        "contradiction_detected": contradiction_detected,
    }


def _run_guarded_pipeline(query: str, research_data: dict | None = None) -> dict:
    layer0 = normalize_input(query)
    canonical_text = layer0.get("canonical_text", "")
    normalization_confidence = float(layer0.get("confidence", 0.0))
    validation_type = validate_input(canonical_text)
    if validation_type == "low_quality":
        return {"validation_type": "low_quality"}

    research_insights: list[str] = []
    if isinstance(research_data, dict) and research_data:
        summary_text, research_insights = _summarize_research(research_data)
        if summary_text:
            canonical_text = f"{canonical_text} {summary_text}".strip()

    layer1 = _layer1_universal_intent_extraction(canonical_text)
    micro_intent_payload = extract_micro_intent(canonical_text)
    behavior_inferred = extract_behavior_signals(canonical_text)
    inferred_from_micro = [micro_intent_payload.get("signal")] if micro_intent_payload.get("signal") else []
    if behavior_inferred or inferred_from_micro:
        existing_mapped = set(layer1.get("mapped_signals") or [])
        layer1["mapped_signals"] = sorted(existing_mapped | set(behavior_inferred) | set(inferred_from_micro))

    adaptive_patterns, adaptive_semantics = apply_adaptive_updates(
        base_patterns=BASE_SIGNAL_PATTERNS,
        base_semantic_hints=SEMANTIC_HINTS,
    )

    pattern_channel = _layer2_pattern_signals(canonical_text, adaptive_patterns)
    semantic_channel = _layer2_semantic_signals(canonical_text, adaptive_semantics)
    conflict_outcome = resolve_signal_conflicts(pattern_channel, semantic_channel)

    thresholds = compute_thresholds(
        normalization_confidence=normalization_confidence,
        validation_type=validation_type,
        segment_count=len(_segments(canonical_text)),
    )
    signal_threshold = thresholds["signal"]
    if normalization_confidence < 0.6:
        signal_threshold *= 0.88
    elif normalization_confidence > 0.8:
        signal_threshold *= 1.06

    resolved_entries = [
        {
            "name": item["name"],
            "confidence": float(item["confidence"]),
            "score": float(item["score"]),
            "source": item["source"],
            "evidence": list(item["evidence"]),
        }
        for item in conflict_outcome["final_signals"]
    ]
    behavior_entries = interpret_behavior_signals(canonical_text)
    lexicon_entries = _layer2_lexicon_signals(canonical_text)
    abstract_entries = _layer2_abstract_signals(layer1)
    all_layer2_entries = behavior_entries + resolved_entries + lexicon_entries + abstract_entries

    research_entries: list[dict] = []
    research_signal_names: set[str] = set()
    existing_signal_names: set[str] = {str(item.get("name", "")) for item in all_layer2_entries if isinstance(item, dict)}
    if isinstance(research_data, dict) and research_data:
        research_entries = extract_signals_from_research(research_data)
        research_signal_names = {str(item.get("name", "")) for item in research_entries if isinstance(item, dict)}
        if research_entries:
            all_layer2_entries = all_layer2_entries + research_entries

    all_layer2_entries = _apply_metric_aware_boost(all_layer2_entries, canonical_text, layer1)
    signals = _merge_signal_entries(all_layer2_entries, signal_threshold=max(0.20, min(0.90, signal_threshold)))

    # If both user input signals and research agree on a signal, boost confidence slightly.
    # This stays deterministic and still flows through control/ranking.
    double_confirmed = existing_signal_names & research_signal_names
    if double_confirmed and signals:
        for item in signals:
            if item.get("name") not in double_confirmed:
                continue
            item["confidence"] = round(min(1.0, float(item.get("confidence", 0.0)) + 0.1), 3)
            item["score"] = round(max(float(item.get("score", 0.0)), item["confidence"] * 100.0), 2)
            item["evidence"] = sorted(set(list(item.get("evidence", [])) + ["research+input_match"]))[:10]

    strong_rule_signals = _strong_rule_matches(canonical_text)
    if strong_rule_signals:
        signals = _merge_signal_entries(signals + strong_rule_signals, signal_threshold=0.2)
        for item in signals:
            if item["name"] in {s["name"] for s in strong_rule_signals}:
                item["confidence"] = max(float(item["confidence"]), 0.85)
                item["score"] = max(float(item["score"]), 85.0)
                item["source"] = "pattern"
                item["evidence"] = sorted(set(list(item.get("evidence", [])) + ["strong_rule_match"]))[:10]

    signals = _relationship_enrichment(signals, canonical_text)
    signals = _anti_hallucination_filter(signals)

    rule_output = {
        "signals": signals,
        "confidence": max((float(item.get("confidence", 0.0)) for item in signals), default=0.0),
        "intent_detected": bool(layer1.get("intent_patterns")),
        "ambiguous": False,
    }
    control_result = run_control_layer(canonical_text, rule_output)
    if strong_rule_signals and control_result.get("decision_path") != "clarification":
        strong_names = [s["name"] for s in strong_rule_signals]
        control_signal_objects = [s for s in signals if s["name"] in strong_names]
        control_result = {
            "signal_objects": control_signal_objects or signals,
            "final_signals": strong_names,
            "primary_signal": strong_names[0] if strong_names else "",
            "confidence": max(0.85, float(control_result.get("confidence", 0.85))),
            "decision_path": "rule",
            "status": "success",
            "status_reason": "Strong rule match override",
        }
    decision_path = control_result.get("decision_path", "rule")
    control_status = control_result.get("status", "success")
    control_reason = control_result.get("status_reason", "")
    controlled_signals = list(control_result.get("signal_objects") or [])

    if control_status == "needs_clarification" and not controlled_signals:
        intent_weights = compute_intent_weights(list(layer1.get("intent_patterns") or []))
        evidence = extract_evidence(canonical_text)
        clarification_reason = build_status_reason(
            canonical_text=canonical_text,
            primary_signal="",
            status="needs_clarification",
            contradiction_detected=False,
            evidence=evidence,
            secondary_signals=[],
        )
        return {
            "domain": "business",
            "validation_type": validation_type,
            "signals": [],
            "clusters": [],
            "top_cluster": "",
            "confidence": float(control_result.get("confidence", 0.3)),
            "primary_signal": "",
            "secondary_signals": [],
            "intent_weights": intent_weights,
            "reasoning": "Low confidence + vague input. Clarification required before reliable business diagnosis.",
            "reasoning_chain": [
                "Input lacks grounded business evidence",
                "Reliable causal inference cannot be established",
                "Clarification is required before diagnosis",
            ],
            "root_causes": [],
            "actions": [
                {
                    "action": "Ask for more detail on KPI impact and funnel stage",
                    "impact": "medium",
                    "difficulty": "low",
                    "priority": 1,
                    "reason": "Required to identify whether the primary bottleneck is acquisition, conversion, or retention",
                }
            ],
            "evidence": evidence,
            "ambiguity": True,
            "status": "needs_clarification",
            "status_reason": clarification_reason,
            "status_suggestion": "Ask for more detail",
            "decision_path": decision_path,
            "final_signals": [],
            "confidence_reason": "Low due to weak evidence and ambiguity",
            "confidence_breakdown": {
                "pattern_score": 0.0,
                "metric_score": 0.0,
                "behavior_score": 0.0,
                "ambiguity_penalty": -0.25,
                "final_confidence": float(control_result.get("confidence", 0.3)),
            },
            "contradiction_detected": False,
            "research_insights": research_insights,
        }

    reasoning_payload = _build_reasoning_payload(
        canonical_text=canonical_text,
        signals=controlled_signals,
        intent_payload=layer1,
        normalization_confidence=normalization_confidence,
    )
    ranked_signals = list(reasoning_payload["ranked_signals"])

    domain, domain_confidence, domain_source = _layer3_domain_inference(ranked_signals, canonical_text)

    clusters, top_cluster = _layer4_intelligence(ranked_signals) if domain == "business" else ([], "")
    final_confidence = float(reasoning_payload["confidence"])
    control_confidence = float(control_result.get("confidence", final_confidence))
    final_confidence = round(min(0.95, (0.7 * final_confidence) + (0.3 * control_confidence)), 3)
    if control_result.get("decision_path") == "reasoning":
        final_confidence = round(max(0.3, final_confidence - 0.05), 3)
    if control_result.get("decision_path") == "rule" and strong_rule_signals:
        final_confidence = max(0.85, final_confidence)
    if domain_confidence > final_confidence:
        final_confidence = round(min(1.0, (0.75 * final_confidence) + (0.25 * domain_confidence)), 3)

    # Light failure memory boost
    try:
        with FAILURE_MEMORY_PATH.open("r", encoding="utf-8") as handle:
            memory_lines = [line.strip() for line in handle.readlines()[-200:] if line.strip()]
        lowered = canonical_text.lower()
        for line in memory_lines:
            if lowered and lowered in line.lower():
                final_confidence = min(0.95, round(final_confidence + 0.03, 3))
                break
    except Exception:
        pass

    if domain == "business" and not ranked_signals:
        log_failure(
            input_text=canonical_text,
            expected="business_signals_present",
            actual=f"no_signals domain_source={domain_source}",
            broken_layer="signals",
        )

    confidence_breakdown = dict(reasoning_payload.get("confidence_breakdown", {}))
    if confidence_breakdown:
        confidence_breakdown["final_confidence"] = round(final_confidence, 3)

    return {
        "domain": domain,
        "validation_type": validation_type,
        "signals": ranked_signals,
        "clusters": clusters,
        "top_cluster": top_cluster,
        "confidence": final_confidence,
        "primary_signal": reasoning_payload["primary_signal"],
        "secondary_signals": reasoning_payload["secondary_signals"],
        "intent_weights": reasoning_payload["intent_weights"],
        "reasoning": reasoning_payload["reasoning"],
        "reasoning_chain": reasoning_payload.get("reasoning_chain", []),
        "root_causes": reasoning_payload["root_causes"],
        "actions": reasoning_payload["actions"],
        "evidence": reasoning_payload.get("evidence", {"behavioral_clues": [], "temporal_clues": [], "metric_clues": []}),
        "ambiguity": reasoning_payload["ambiguity"],
        "status": reasoning_payload["status"],
        "status_reason": reasoning_payload["status_reason"],
        "status_suggestion": reasoning_payload["status_suggestion"],
        "decision_path": decision_path,
        "final_signals": list(control_result.get("final_signals") or [item["name"] for item in ranked_signals]),
        "confidence_breakdown": confidence_breakdown,
        "confidence_reason": reasoning_payload.get("confidence_reason", ""),
        "contradiction_detected": bool(reasoning_payload.get("contradiction_detected", False)),
        "research_insights": research_insights,
    }


def run_guarded_pipeline(query: str, research_data: dict | None = None) -> dict:
    # Backward compatible entrypoint: existing callers can pass only query.
    return _run_guarded_pipeline(query, research_data=research_data)


def _summarize_research(research_data: dict) -> tuple[str, list[str]]:
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9']+", str(text or "").lower())

    stop = {
        "the",
        "and",
        "or",
        "to",
        "of",
        "in",
        "a",
        "is",
        "are",
        "for",
        "on",
        "with",
        "that",
        "this",
        "it",
        "as",
        "be",
        "from",
        "at",
        "an",
        "by",
        "we",
        "you",
        "your",
        "my",
        "our",
        "bro",
        "idk",
    }

    # Collect lightweight text from sources/search/reddit; keep bounded for performance.
    chunks: list[str] = []
    for item in list(research_data.get("sources") or [])[:25]:
        chunks.append(str(item.get("title") or ""))
        chunks.append(str(item.get("snippet") or ""))
        chunks.append(str(item.get("content") or ""))
    for item in list(research_data.get("search_results") or [])[:15]:
        chunks.append(str(item.get("title") or ""))
        chunks.append(str(item.get("snippet") or ""))
    for item in list(research_data.get("reddit") or [])[:10]:
        chunks.append(str(item.get("title") or ""))
        chunks.append(str(item.get("text") or ""))

    corpus = " ".join(chunks)
    token_list = [t for t in _tokens(corpus) if t and t not in stop and len(t) >= 3]

    # Keyword extraction (deterministic frequency).
    freq: dict[str, int] = {}
    for t in token_list:
        freq[t] = freq.get(t, 0) + 1
    top_keywords = [k for k, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]

    complaints_map = [
        ("pricing", {"price", "pricing", "expensive", "cheap"}),
        ("trust", {"trust", "reviews", "testimonials", "credibility"}),
        ("checkout friction", {"checkout", "payment", "cart", "abandon"}),
        ("conversion drop-off", {"conversion", "conversions", "not", "buy", "purchase", "sales", "drop"}),
        ("slow site", {"slow", "loading", "speed"}),
    ]
    insights: list[str] = []
    token_set = set(token_list)
    for label, triggers in complaints_map:
        if triggers & token_set:
            insights.append(f"Research mentions {label} as a recurring theme")

    trends_map = [
        ("paid ads efficiency", {"ads", "cpc", "roi", "roas", "campaign"}),
        ("traffic-to-sales gap", {"traffic", "sales", "revenue", "conversion"}),
        ("retention/churn", {"retention", "churn", "return", "inactive"}),
    ]
    for label, triggers in trends_map:
        if triggers & token_set:
            insights.append(f"Research content discusses {label}")

    if top_keywords:
        insights.insert(0, f"Top keywords: {', '.join(top_keywords[:6])}")

    insights = insights[:5]

    # Summary text is appended to canonical_text; keep short and explicit.
    summary_parts = []
    if top_keywords:
        summary_parts.append("research keywords " + " ".join(top_keywords[:8]))
    if insights:
        summary_parts.append("research insights " + " ; ".join(insights[1:4]))
    summary_text = " ".join(part for part in summary_parts if part).strip()
    if len(summary_text) > 1200:
        summary_text = summary_text[:1200].rstrip()

    return summary_text, insights


def extract_signals_from_research(research_data: dict) -> list[dict]:
    if not isinstance(research_data, dict) or not research_data:
        return []

    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9']+", str(text or "").lower()))

    def _collect_text() -> str:
        chunks: list[str] = []
        for item in list(research_data.get("sources") or [])[:25]:
            chunks.append(str(item.get("title") or ""))
            chunks.append(str(item.get("snippet") or ""))
            chunks.append(str(item.get("content") or ""))
        for item in list(research_data.get("search_results") or [])[:15]:
            chunks.append(str(item.get("title") or ""))
            chunks.append(str(item.get("snippet") or ""))
        for item in list(research_data.get("reddit") or [])[:10]:
            chunks.append(str(item.get("title") or ""))
            chunks.append(str(item.get("text") or ""))
        return " ".join(chunks).lower()

    text = _collect_text()
    token_set = _tokens(text)
    if not token_set:
        return []

    # Lightweight pattern detection (deterministic). Evidence strings are kept short and tagged.
    signal_patterns: dict[str, list[tuple[str, set[str]]]] = {
        "conversion optimization": [
            ("pricing issue", {"pricing", "price", "expensive"}),
            ("not buying / no purchase", {"buy", "buying", "purchase", "sales", "conversion", "conversions"}),
            ("checkout friction", {"checkout", "payment", "cart", "abandon", "abandoned"}),
            ("low conversion", {"low", "zero", "conversion", "conversions"}),
        ],
        "retention": [
            ("users leaving", {"leave", "leaving"}),
            ("not returning", {"return", "returning"}),
            ("churn/inactive", {"churn", "inactive"}),
        ],
        "paid ads": [
            ("ads not working", {"ads", "ad", "campaign", "spend", "budget"}),
            ("high cpc / low roi", {"cpc", "roi", "roas", "cost"}),
            ("no result from ads", {"no", "result", "results", "zero", "roi"}),
        ],
        "lead generation": [
            ("low traffic / no visibility", {"traffic", "reach", "visibility", "visitors"}),
            ("no traffic", {"no", "traffic"}),
        ],
    }

    extracted: list[dict] = []
    for signal_name, patterns in signal_patterns.items():
        matched: list[str] = []
        match_count = 0
        for label, triggers in patterns:
            if triggers.issubset(token_set) or (triggers & token_set and label in text):
                matched.append(f"research:{label}")
                match_count += 1

        # Phrase-based catches for common complaints.
        if signal_name == "conversion optimization" and any(p in text for p in ("not converting", "no conversion", "conversion zero")):
            matched.append("research:not converting")
            match_count += 1
        if signal_name == "retention" and any(p in text for p in ("not coming back", "never come back", "repeat customer")):
            matched.append("research:repeat/returning issue")
            match_count += 1
        if signal_name == "paid ads" and any(p in text for p in ("ads running", "ad spend", "burning money")):
            matched.append("research:ads running/spend")
            match_count += 1
        if signal_name == "lead generation" and any(p in text for p in ("no traffic", "low traffic", "not much traffic", "no visibility")):
            matched.append("research:low/no traffic")
            match_count += 1

        if match_count <= 0:
            continue

        # Confidence is intentionally conservative; control/ranking still governs final selection.
        base = 0.52 + (0.08 * min(match_count, 4))
        confidence = round(min(0.85, base), 3)
        extracted.append(
            {
                "name": signal_name,
                "confidence": confidence,
                "score": round(confidence * 100.0, 2),
                "source": "research",
                "evidence": sorted(set(matched))[:8],
            }
        )

    return extracted
