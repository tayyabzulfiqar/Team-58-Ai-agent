BASE_WEIGHTS = {
    "service_relevance": 1.0,
    "intent_match": 1.2,
    "content_depth": 1.0,
    "authority": 1.0,
    "contact": 0.8,
    "commercial_intent": 1.1,
    "url_quality": 0.5,
    "noise_penalty": 1.0,
}

INTENT_WEIGHT_ADJUSTMENTS = {
    "transactional": {
        "contact": 0.4,
        "commercial_intent": 0.5,
        "service_relevance": 0.2,
        "content_depth": -0.1,
    },
    "informational": {
        "content_depth": 0.4,
        "authority": 0.3,
        "commercial_intent": -0.3,
        "contact": -0.1,
    },
    "navigational": {
        "url_quality": 0.6,
        "intent_match": 0.2,
        "authority": 0.1,
    },
}

LABEL_THRESHOLDS = {
    "HIGH_INTENT": 75.0,
    "MEDIUM": 50.0,
}

MAX_WEIGHTED_SCORE = 32.2
MIN_WEIGHTED_SCORE = -3.0


def get_weights(intent_type: str) -> dict[str, float]:
    weights = dict(BASE_WEIGHTS)
    for key, delta in INTENT_WEIGHT_ADJUSTMENTS.get(intent_type, {}).items():
        weights[key] = round(weights[key] + delta, 2)
    return weights
