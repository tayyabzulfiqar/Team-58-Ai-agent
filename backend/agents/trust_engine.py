from agents.scoring_utils import (
    classify_content_type,
    compute_unique_word_ratio,
    detect_keyword_stuffing,
    detect_noise,
    extract_domain,
)
from agents.scoring_engine import determine_label


PENALTY_CAP = 0.15
SCORE_MULTIPLIER = 1.04


def normalize_score(score):
    safe_score = max(0.0, min(score, 1.0))
    return round(safe_score ** 1.3, 4)


def compute_real_trust(item):
    breakdown = item.get("breakdown", {})
    url = item.get("url", "")
    domain = extract_domain(url)
    content = item.get("_content", "")

    authority_signal = breakdown.get("authority", 0) / 4 if breakdown.get("authority", 0) else 0.0
    contact_signal = 1.0 if breakdown.get("contact", 0) >= 2 else 0.45 if breakdown.get("contact", 0) == 1 else 0.05
    url_signal = 1.0 if breakdown.get("url_quality", 0) >= 2 else 0.55 if breakdown.get("url_quality", 0) == 1 else 0.15

    domain_signal = 0.6
    if domain.endswith(".org") or domain.endswith(".edu") or domain.endswith(".gov"):
        domain_signal = 0.9
    elif any(token in domain for token in ("sandler", "kaplan", "zurich", "marshberry", "richardson")):
        domain_signal = 0.82

    unique_ratio = compute_unique_word_ratio(content)
    stuffing_ratio = detect_keyword_stuffing(item.get("query", ""), content) if item.get("query") else 0.0
    uniqueness_adjustment = 0.05 if unique_ratio >= 0.5 else -0.08 if unique_ratio <= 0.32 else 0.0
    stuffing_penalty = -0.12 if stuffing_ratio >= 0.08 else -0.06 if stuffing_ratio >= 0.05 else 0.0

    trust_score = (
        authority_signal * 0.35
        + contact_signal * 0.25
        + url_signal * 0.15
        + domain_signal * 0.25
    )
    trust_score += uniqueness_adjustment + stuffing_penalty
    if breakdown.get("contact", 0) == 0:
        trust_score -= 0.08

    return round(max(0.0, min(trust_score, 1.0)), 4)


def apply_penalties(item):
    adjusted = dict(item)
    score = max(0.0, min(adjusted.get("score", 0.0), 1.0))
    breakdown = adjusted.get("breakdown", {})
    penalty = 0.0

    if breakdown.get("contact", 0) == 0:
        penalty += 0.08
    if breakdown.get("commercial_intent", 0) == 0:
        penalty += 0.08
    if breakdown.get("noise_penalty", 0) <= -1:
        penalty += 0.06
    if adjusted.get("trust_signal", 0.0) < 0.3:
        penalty += 0.05

    penalty = max(0.0, min(penalty, PENALTY_CAP))
    adjusted["score"] = round(max(0.0, min(score - penalty, 1.0)), 4)
    adjusted["penalty_applied"] = round(penalty, 4)
    return adjusted


def adjust_by_content_type(item):
    adjusted = dict(item)
    content_type = adjusted.get("content_type") or classify_content_type(adjusted.get("url", ""), adjusted.get("_content", ""))
    score = max(0.0, min(adjusted.get("score", 0.0), 1.0))

    if content_type == "service_page":
        score += 0.16
    elif content_type == "landing_page":
        score += 0.08
    elif content_type == "aggregator":
        score -= 0.15
    elif content_type == "blog":
        score -= 0.10
    elif content_type == "directory":
        score -= 0.12
    else:
        score -= 0.08

    adjusted["content_type"] = content_type
    adjusted["score"] = round(max(0.0, min(score, 1.0)), 4)
    return adjusted


def classify_lead(item):
    score = item.get("score", 0.0)
    breakdown = item.get("breakdown", {})
    has_contact = breakdown.get("contact", 0) > 0
    has_commercial = breakdown.get("commercial_intent", 0) > 0

    if item.get("discarded") or item.get("intent_score", 0.0) < 0.35:
        return "DISCARD"
    if score >= 0.75 and has_contact and has_commercial:
        return "HIGH"
    if 0.45 <= score < 0.75:
        return "MEDIUM"
    if 0.25 <= score < 0.45:
        return "LOW"
    return "DISCARD"


def apply_trust_layer(results: list, query: str) -> list:
    adjusted = []

    for item in results:
        trusted_item = dict(item)
        trusted_item["score"] = max(0.0, min(trusted_item.get("score", 0.0), 1.0))
        trusted_item["query"] = query
        trusted_item["content_type"] = trusted_item.get("content_type") or classify_content_type(
            trusted_item.get("url", ""), trusted_item.get("_content", "")
        )
        trusted_item = apply_penalties(trusted_item)
        trusted_item = adjust_by_content_type(trusted_item)
        base_score = trusted_item.get("score", 0.0)
        trust_score = compute_real_trust(trusted_item)
        multiplier = 0.88 + (trust_score * 0.22)
        multiplier = max(0.85, min(multiplier, 1.15))

        trusted_item["trust_score"] = round(trust_score, 2)
        adjusted_score = base_score * multiplier
        breakdown = trusted_item.get("breakdown", {})
        post_boost = 0.0
        if trusted_item["content_type"] == "service_page":
            if breakdown.get("service_relevance", 0) >= 4:
                post_boost += 0.15
            if breakdown.get("authority", 0) >= 3:
                post_boost += 0.10
            if breakdown.get("contact", 0) >= 1:
                post_boost += 0.06
        elif trusted_item["content_type"] == "landing_page":
            post_boost += 0.12
        elif trusted_item["content_type"] == "blog":
            post_boost -= 0.06
        elif trusted_item["content_type"] == "directory":
            post_boost -= 0.08

        # --- SIGNAL INTERACTION LOGIC ---
        intent = trusted_item.get('intent_score', 0)
        actionability = trusted_item.get('actionability_score', 0)
        trust = trusted_item.get('trust_signal', 0)
        # Penalize: high intent + actionability + low trust
        if intent > 0.7 and actionability > 0.7 and trust < 0.3:
            post_boost -= 0.15
            trusted_item['reason'] = trusted_item.get('reason', '') + ' [Penalty: high intent/actionability but low trust]'
        # Boost: high trust + intent
        if trust > 0.7 and intent > 0.7:
            post_boost += 0.10
            trusted_item['reason'] = trusted_item.get('reason', '') + ' [Boost: high trust+intent]'

        trusted_item["score"] = round(max(0.0, min((adjusted_score + post_boost) * SCORE_MULTIPLIER, 1.0)), 4)
        trusted_item["score"] = normalize_score(trusted_item["score"])
        # Clamp final score
        trusted_item["score"] = max(0.0, min(trusted_item["score"], 1.0))
        trusted_item["normalized_score"] = trusted_item["score"]
        trusted_item["label"] = determine_label(trusted_item["score"] * 100)
        trusted_item["lead_quality"] = classify_lead(trusted_item)
        trusted_item["reason"] = (
            f"{trusted_item['content_type']} adjusted to {trusted_item['score']:.2f}. "
            f"Trust {trusted_item['trust_score']:.2f}, penalty {trusted_item.get('penalty_applied', 0.0):.2f}, boost {post_boost:.2f}."
        )
        adjusted.append(trusted_item)

    return adjusted
