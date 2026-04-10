from core.logging_utils import get_logger


logger = get_logger("team58.validation")


def _confidence_label(source_count: int) -> str:
    if source_count >= 3:
        return "high"
    if source_count == 2:
        return "medium"
    return "low"


def validation_tool(scored: dict) -> dict:
    logger.info("validation:start")
    validated = []

    for opportunity in scored.get("ranked_opportunities", []):
        source_count = len(opportunity.get("supporting_sources", []))
        confidence = _confidence_label(source_count)
        if confidence == "low":
            continue

        validated.append(
            {
                **opportunity,
                "source_count": source_count,
                "confidence": confidence,
            }
        )

    if not validated:
        raise RuntimeError("Validation filtered all opportunities due to weak source support.")

    logger.info("validation:done kept=%s", len(validated))
    return {"validated_opportunities": validated}
