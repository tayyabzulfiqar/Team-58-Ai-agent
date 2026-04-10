import json

from core.input_utils import detect_budget_tier
from core.logging_utils import get_logger
from memory.store import successful_outcomes


logger = get_logger("team58.decision")


def enforce_policy(original_input, chosen_strategy):
    t = str(original_input).lower()

    brand_signals = [
        "new market",
        "launch",
        "startup",
        "new product",
        "early stage",
        "brand awareness",
        "visibility"
    ]

    for signal in brand_signals:
        if signal in t:
            return "Brand awareness"

    return chosen_strategy


def generate_reason(data, strategy):
    analysis = data.get("analysis", {})
    text = str(analysis).lower()

    if strategy == "Performance marketing":
        if "conversion" in text or "funnel" in text:
            return "Focus is on conversions and measurable ROI"
        return "Best for driving immediate results"

    if strategy == "Emotional marketing":
        if "story" in text or "emotion" in text:
            return "Relies on emotional engagement and storytelling"
        return "Best for building trust and connection"

    if strategy == "Brand awareness":
        if "launch" in text or "startup" in text:
            return "Suitable for new brand or market entry"
        return "Best for long-term visibility and growth"

    return "Decision based on market signals"


def calculate_confidence(data, strategy):
    analysis = str(data.get("analysis", "")).lower()
    score = 50

    if strategy == "Performance marketing":
        if "conversion" in analysis or "roi" in analysis:
            score += 20

    if strategy == "Emotional marketing":
        if "emotion" in analysis or "story" in analysis:
            score += 20

    if strategy == "Brand awareness":
        if "launch" in analysis or "startup" in analysis:
            score += 20

    if len(analysis) > 300:
        score += 10

    return min(score, 95)


def generate_alternatives(best_strategy):
    strategies = [
        "Performance marketing",
        "Emotional marketing",
        "Brand awareness"
    ]
    return [s for s in strategies if s != best_strategy]


def learning_bonus(strategy):
    return min(len(successful_outcomes(strategy)), 10)


def decision_tool(data, original_input=""):
    logger.info("decision:start")
    objective = data.get("objective", "mixed")
    budget_tier = detect_budget_tier(original_input)
    structured = data.get("structured_intelligence", {})
    validated = data.get("validation", {}).get("validated_opportunities", [])
    scored = data.get("scored_opportunities", {}).get("ranked_opportunities", [])
    top_opportunity = validated[0] if validated else (scored[0] if scored else {})
    competition_level = "high" if len(structured.get("competitors", [])) >= 3 else "medium" if len(structured.get("competitors", [])) >= 1 else "low"
    audience_behavior = "research-heavy" if "Thought leadership" in structured.get("trends", []) else "conversion-focused"

    if validated:
        matched_trends = set(top_opportunity.get("matched_trends", []))
        matched_pain_points = set(top_opportunity.get("matched_pain_points", []))

        if objective == "awareness" or "Brand visibility expansion" == top_opportunity.get("name"):
            best_strategy = "Brand awareness"
        elif budget_tier == "low" and competition_level == "high":
            best_strategy = "Emotional marketing"
        elif "Conversion optimization" in matched_trends or "Weak conversion efficiency" in matched_pain_points:
            best_strategy = "Performance marketing"
        elif "Thought leadership" in matched_trends:
            best_strategy = "Brand awareness"
        else:
            best_strategy = data.get("analysis", {}).get("best_strategy", "Performance marketing")

        best_strategy = enforce_policy(original_input, best_strategy)
        confidence = min(max(int(top_opportunity.get("score", 60)), 55) + learning_bonus(best_strategy), 95)
        reason = (
            f"Selected {best_strategy} because top opportunity '{top_opportunity.get('name', 'top opportunity')}' ranked highest, "
            f"confidence is {top_opportunity.get('confidence', 'medium')}, budget is {budget_tier}, "
            f"competition is {competition_level}, and audience behavior is {audience_behavior}."
        )
        result = {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": reason,
            "confidence": confidence,
            "status": "decided",
            "decision_inputs": {
                "budget_tier": budget_tier,
                "competition_level": competition_level,
                "audience_behavior": audience_behavior,
                "top_opportunity": top_opportunity.get("name"),
            },
        }
        logger.info("decision:done strategy=%s", best_strategy)
        return result

    if objective == "conversion":
        best_strategy = "Performance marketing"
        confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)
        result = {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": "Objective is conversion-focused",
            "confidence": confidence,
            "status": "decided"
        }
        logger.info("decision:done strategy=%s", best_strategy)
        return result

    if objective == "emotional":
        best_strategy = "Emotional marketing"
        confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)
        result = {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": "Objective is emotional engagement",
            "confidence": confidence,
            "status": "decided"
        }
        logger.info("decision:done strategy=%s", best_strategy)
        return result

    if objective == "awareness":
        best_strategy = "Brand awareness"
        confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)
        result = {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": "Objective is long-term visibility",
            "confidence": confidence,
            "status": "decided"
        }
        logger.info("decision:done strategy=%s", best_strategy)
        return result

    best_strategy = data["analysis"]["best_strategy"]
    best_strategy = enforce_policy(original_input, best_strategy)
    reason = generate_reason(data, best_strategy)
    confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)

    result = {
        "selected_strategy": best_strategy,
        "alternatives": generate_alternatives(best_strategy),
        "reason": reason if reason else "Decision based on market analysis",
        "confidence": confidence,
        "status": "decided"
    }
    logger.info("decision:done strategy=%s", best_strategy)
    return result
