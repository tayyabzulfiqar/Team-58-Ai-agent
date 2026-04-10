from core.logging_utils import get_logger
from tools.learning_tool import learning_state


logger = get_logger("team58.scoring")


def _normalize(score: float) -> float:
    return round(max(0.0, min(100.0, score)), 2)


def scoring_tool(structured: dict) -> dict:
    logger.info("scoring:start")
    state = learning_state()
    weights = state["weights"]
    competitor_penalty = min(len(structured.get("competitors", [])) * 10, 40)
    scored = []

    for opportunity in structured.get("opportunities", []):
        trend_strength = _normalize(len(opportunity.get("matched_trends", [])) * 35 + len(opportunity.get("supporting_sources", [])) * 5)
        competition_gap = _normalize(70 - competitor_penalty + len(opportunity.get("matched_pain_points", [])) * 10)
        demand_signal = _normalize(len(opportunity.get("matched_pain_points", [])) * 30 + len(opportunity.get("supporting_sources", [])) * 8)
        score = _normalize(
            (trend_strength * weights["trend_strength"])
            + (competition_gap * weights["competition_gap"])
            + (demand_signal * weights["demand_signal"])
        )

        if score < 45:
            continue

        scored.append(
            {
                **opportunity,
                "trend_strength": trend_strength,
                "competition_gap": competition_gap,
                "demand_signal": demand_signal,
                "score": score,
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)

    if not scored:
        raise RuntimeError("Scoring removed all opportunities as weak signals.")

    logger.info("scoring:done kept=%s", len(scored))
    return {"ranked_opportunities": scored, "learning_state": state}
