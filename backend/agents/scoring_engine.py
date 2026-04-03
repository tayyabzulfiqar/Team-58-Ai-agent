def should_stop_early(lead):
    # Early stopping if confidence > 0.90
    return lead.get('confidence', 0) > 0.90
from scripts.intelligence.learning_optimizer import LearningOptimizer
from agents.scoring_utils import clamp01
def resolve_dynamic_weights(intent_type: str) -> dict:
    # Get default weights
    from config.scoring_weights import BASE_WEIGHTS, INTENT_WEIGHT_ADJUSTMENTS
    weights = dict(BASE_WEIGHTS)
    # Apply intent adjustments
    for key, delta in INTENT_WEIGHT_ADJUSTMENTS.get(intent_type, {}).items():
        weights[key] = round(weights[key] + delta, 2)
    # Merge with dynamic weights from learning_optimizer
    try:
        lo = LearningOptimizer()
        dyn = lo.get_current_config().get('weights', {})
        # Map dynamic keys to scoring keys if needed
        mapping = {
            'service_fit': 'service_relevance',
            'ads_presence': 'commercial_intent',
            'pain_clarity': 'intent_match',
            'icp_match': 'authority',
            'urgency_signals': 'noise_penalty',
            'decision_maker': 'contact',
            'business_size': 'url_quality',
        }
        for k, v in mapping.items():
            if k in dyn and v in weights:
                # Normalize to [0,1]
                weights[v] = clamp01(float(dyn[k]) / 35.0)
    except Exception:
        pass
    # Clamp all weights
    for k in weights:
        weights[k] = clamp01(weights[k])
    return weights
from agents.scoring_components import (
    score_authority,
    score_commercial_intent,
    score_contact,
    score_content_depth,
    score_intent_match,
    score_noise_penalty,
    score_service_relevance,
    score_url_quality,
)
from agents.scoring_utils import (
    classify_content_type,
    clean_text,
    compute_final_score,
    extract_entity_profile,
    normalize_url,
)
from config.scoring_weights import LABEL_THRESHOLDS, MAX_WEIGHTED_SCORE, MIN_WEIGHTED_SCORE, get_weights
from models.score_schema import ScoreResult


COMPONENT_ORDER = (
    "service_relevance",
    "intent_match",
    "content_depth",
    "authority",
    "contact",
    "commercial_intent",
    "url_quality",
    "noise_penalty",
)


def _build_reason(explanations: dict, trust_score: float, content_type: str) -> str:
    strongest = []
    for key in ("service_relevance", "intent_match", "authority", "contact", "commercial_intent"):
        strongest.append(explanations[key])
        if len(strongest) == 2:
            break
    return f"{content_type} with trust {trust_score:.2f}. " + " ".join(strongest[:2])


def determine_label(score: float) -> str:
    if score >= LABEL_THRESHOLDS["HIGH_INTENT"]:
        return "HIGH_INTENT"
    if score >= LABEL_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    return "LOW"


def score_result(url: str, content: str, query: str, intent_analysis: dict) -> ScoreResult:
    normalized_url = normalize_url(url)
    cleaned_content = clean_text(content)
    features = compute_final_score(cleaned_content, cleaned_content)
    intent_signal = features["intent"]
    actionability_signal = features["actionability"]
    content_signal = features["content"]
    trust_signal = features["trust"]
    weights = resolve_dynamic_weights(intent_analysis["intent_type"])

    component_results = {
        "service_relevance": score_service_relevance(cleaned_content, query),
        "intent_match": score_intent_match(cleaned_content, query),
        "content_depth": score_content_depth(cleaned_content),
        "authority": score_authority(normalized_url, cleaned_content),
        "contact": score_contact(cleaned_content),
        "commercial_intent": score_commercial_intent(cleaned_content),
        "url_quality": score_url_quality(normalized_url, query),
        "noise_penalty": score_noise_penalty(cleaned_content),
    }

    breakdown = {name: component_results[name][0] for name in COMPONENT_ORDER}
    weighted_breakdown = {
        name: round(component_results[name][0] * weights[name], 2) for name in COMPONENT_ORDER
    }
    explanations = {name: component_results[name][1] for name in COMPONENT_ORDER}
    service_relevance_signal = breakdown["service_relevance"] / 5
    intent_match_signal = breakdown["intent_match"] / 5
    authority_signal = breakdown["authority"] / 4 if breakdown["authority"] else 0.0

    final_score = (
        intent_signal * 0.30
        + actionability_signal * 0.25
        + content_signal * 0.20
        + trust_signal * 0.15
        + service_relevance_signal * 0.15
        + intent_match_signal * 0.10
        + authority_signal * 0.10
    )

    if breakdown["contact"] == 0:
        final_score -= 0.05

    normalized_score = round(max(0.0, min(final_score, 1.0)), 4)

    label = determine_label(normalized_score * 100)

    content_type = classify_content_type(normalized_url, cleaned_content)
    entity = extract_entity_profile(normalized_url, cleaned_content)
    trust_score = 1.0

    return {
        "url": normalized_url,
        "score": normalized_score,
        "normalized_score": normalized_score,
        "label": label,
        "intent_type": intent_analysis["intent_type"],
        "trust_score": trust_score,
        "content_type": content_type,
        "breakdown": breakdown,
        "weighted_breakdown": weighted_breakdown,
        "explanations": explanations,
        "entity": entity,
        "intent_score": intent_signal,
        "actionability_score": actionability_signal,
        "trust_signal": trust_signal,
        "content_signal": content_signal,
        "reason": _build_reason(explanations, trust_score, content_type),
        "_content": cleaned_content,
    }


def score_results(data: list, query: str, intent_analysis: dict) -> list[ScoreResult]:
    items = data if isinstance(data, list) else []
    print(f"📊 SCORING ITEMS: {len(items)}")

    results = []
    for item in items:
        if not isinstance(item, dict):
            continue
        results.append(score_result(item.get("url", ""), item.get("content", ""), query, intent_analysis))

    return results
