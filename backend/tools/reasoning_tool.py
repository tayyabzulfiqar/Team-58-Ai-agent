from core.logging_utils import get_logger
from services.qwen_service import qwen_generate


logger = get_logger("team58.reasoning")


def reasoning_tool(analysis_data):
    logger.info("reasoning:start")
    structured_intelligence = analysis_data.get("structured_intelligence", {})
    scored_opportunities = analysis_data.get("scored_opportunities", {}).get("ranked_opportunities", [])
    validated_opportunities = analysis_data.get("validation", {}).get("validated_opportunities", [])
    analysis = analysis_data.get("analysis", {})

    explanation = [
        f"Audience identified: {structured_intelligence.get('audience', 'unknown')}",
        f"Top trends: {', '.join(structured_intelligence.get('trends', [])[:3]) or 'none'}",
        f"Top pain points: {', '.join(structured_intelligence.get('pain_points', [])[:3]) or 'none'}",
    ]

    if scored_opportunities:
        top_scored = scored_opportunities[0]
        explanation.append(
            f"Highest scored opportunity is {top_scored.get('name')} with score {top_scored.get('score')}."
        )

    if validated_opportunities:
        top_validated = validated_opportunities[0]
        explanation.append(
            f"Best validated opportunity is {top_validated.get('name')} with {top_validated.get('confidence')} confidence from {top_validated.get('source_count')} sources."
        )

    if analysis.get("best_strategy"):
        explanation.append(f"Current strategy evidence favors {analysis.get('best_strategy')}.")

    reasoning_prompt = f"""
Generate grounded strategic reasoning using only the structured, scored, validated evidence below.

STRUCTURED DATA:
{structured_intelligence}

SCORED OPPORTUNITIES:
{scored_opportunities[:5]}

VALIDATED OPPORTUNITIES:
{validated_opportunities[:5]}
"""
    llm_reasoning = qwen_generate(
        reasoning_prompt,
        system_prompt="You are a senior analyst turning validated marketing evidence into concise reasoning.",
    )

    result = {
        "reasoning": explanation[:5],
        "llm_reasoning": llm_reasoning,
        "confidence_factor": len(explanation) * 10,
        "status": "reasoned"
    }
    logger.info("reasoning:done points=%s", len(explanation))
    return result
