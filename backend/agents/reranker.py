from agents.scoring_engine import determine_label


def _decision_from_opportunity(opportunity_score: float) -> str:
    if opportunity_score >= 0.75:
        return "HIGH_VALUE_LEAD"
    if opportunity_score >= 0.55:
        return "MEDIUM_VALUE_LEAD"
    if opportunity_score >= 0.4:
        return "LOW_VALUE"
    return "DISCARD"


def _actionability_label(actionability_score: float) -> str:
    if actionability_score >= 0.75:
        return "HIGH"
    if actionability_score >= 0.45:
        return "MEDIUM"
    return "LOW"


def _build_decision_reason(item: dict, intent_type: str, bonus: float) -> str:
    breakdown = item.get("breakdown", {})
    trust_score = item.get("trust_score", 0.0)
    actionability_score = item.get("actionability_score", 0.0)
    differentiator = "strong authority" if breakdown.get("authority", 0) >= 3 else "service clarity"
    if breakdown.get("contact", 0) >= 2:
        differentiator = "clear contact path"
    elif item.get("content_type") in {"service_page", "landing_page"}:
        differentiator = "service-page fit"

    return (
        f"{intent_type} intent alignment, trust {trust_score:.2f}, actionability {actionability_score:.2f}, "
        f"and {differentiator} drive this lead; contextual bonus {bonus:.2f}."
    )


def rerank_with_context(results: list, intent_analysis: dict) -> list:
    intent_type = intent_analysis["intent_type"]
    reranked = []

    for item in results:
        adjusted = dict(item)
        bonus = 0.0
        content_type = adjusted.get("content_type", "resource")
        breakdown = adjusted.get("breakdown", {})

        if intent_type == "transactional":
            if breakdown.get("contact", 0) >= 2:
                bonus += 0.12
            if breakdown.get("commercial_intent", 0) >= 2:
                bonus += 0.1
            if adjusted.get("content_type") in {"service_page", "landing_page"}:
                bonus += 0.08
        elif intent_type == "informational":
            if breakdown.get("content_depth", 0) >= 4:
                bonus += 0.12
            if breakdown.get("authority", 0) >= 3:
                bonus += 0.08
            if adjusted.get("content_type") in {"blog", "resource"}:
                bonus += 0.05
        else:
            if breakdown.get("url_quality", 0) >= 1:
                bonus += 0.08
            if breakdown.get("intent_match", 0) >= 4:
                bonus += 0.08

        if intent_analysis["urgency"] >= 4 and breakdown.get("contact", 0) >= 1:
            bonus += 0.05

        normalized_score = adjusted.get("normalized_score", adjusted.get("score", 0.0))
        actionability_score = adjusted.get("actionability_score", 0.0)
        trust_score = adjusted.get("trust_score", 0.0)

        if breakdown.get("contact", 0) == 0:
            normalized_score = min(normalized_score, 0.62)
            actionability_score = min(actionability_score, 0.35)
            bonus = min(bonus, 0.03)

        if adjusted.get("content_type") == "blog" and breakdown.get("commercial_intent", 0) == 0:
            normalized_score = min(normalized_score, 0.38)
            actionability_score = min(actionability_score, 0.2)
            trust_score = min(trust_score, 0.75)

        opportunity_score = (normalized_score * 0.4) + (actionability_score * 0.4) + (trust_score * 0.2) + bonus
        opportunity_score = round(max(0.0, min(opportunity_score, 1.0)), 4)

        decision = _decision_from_opportunity(opportunity_score)
        if adjusted.get("actionability_score", actionability_score) < 0.45 and decision == "HIGH_VALUE_LEAD":
            decision = "MEDIUM_VALUE_LEAD"

        adjusted["normalized_score"] = round(max(0.0, min(normalized_score, 1.0)), 4)
        adjusted["score"] = adjusted["normalized_score"]
        adjusted["actionability_score"] = round(max(0.0, min(actionability_score, 1.0)), 4)
        adjusted["opportunity_score"] = opportunity_score
        adjusted["decision"] = decision
        adjusted["actionability"] = _actionability_label(adjusted["actionability_score"])
        adjusted["label"] = determine_label(adjusted["normalized_score"] * 100)
        adjusted["reason"] = _build_decision_reason(adjusted, intent_type, bonus)
        reranked.append(adjusted)

    return sorted(reranked, key=lambda item: item["opportunity_score"], reverse=True)


def select_top_n(results: list, top_n: int = 5) -> list:
    filtered = []
    for item in results:
        breakdown = item.get("breakdown", {})
        if item.get("opportunity_score", 0.0) < 0.4:
            continue
        if breakdown.get("service_relevance", 0) <= 0:
            continue
        if item.get("actionability", "LOW") == "LOW" and item.get("decision") == "HIGH_VALUE_LEAD":
            continue
        if item.get("content_type") == "blog" and (
            breakdown.get("commercial_intent", 0) < 2 or item.get("actionability", "LOW") == "LOW"
        ):
            continue
        if item.get("decision") == "DISCARD":
            continue
        filtered.append(item)

    final_results = []
    for item in filtered[:top_n]:
        entity = item.get("entity", {})
        contact_info = entity.get("contact_info", {})
        contact_available = bool(contact_info.get("email") or contact_info.get("phone") or contact_info.get("form"))
        cleaned = {
            "company_name": entity.get("company_name", ""),
            "url": item.get("url", ""),
            "normalized_score": item.get("normalized_score", 0.0),
            "opportunity_score": item.get("opportunity_score", 0.0),
            "intent": item.get("intent_type", ""),
            "decision": item.get("decision", "DISCARD"),
            "actionability": item.get("actionability", "LOW"),
            "trust_score": item.get("trust_score", 0.0),
            "contact_available": contact_available,
            "key_signals": {
                "service": item.get("breakdown", {}).get("service_relevance", 0) >= 3,
                "authority": item.get("breakdown", {}).get("authority", 0) >= 2,
                "cta": item.get("breakdown", {}).get("contact", 0) >= 2,
            },
            "reason": item.get("reason", ""),
        }
        final_results.append(cleaned)
    return final_results
