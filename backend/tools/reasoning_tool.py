from backend.services.qwen_service import qwen_generate


def reasoning_tool(analysis_data):
    strategies = analysis_data.get("top_strategies", [])
    hooks = analysis_data.get("top_hooks", [])
    trends = analysis_data.get("market_trends", [])

    explanation = []

    if "emotional marketing" in strategies:
        explanation.append("Emotional triggers are widely used and drive higher engagement")

    if "performance marketing" in strategies:
        explanation.append("Performance-based campaigns focus on measurable conversions")

    if "brand awareness" in strategies:
        explanation.append("Brand awareness builds long-term customer trust")

    if "urgency hook" in hooks:
        explanation.append("Urgency increases immediate action and conversions")

    if "discount-based hook" in hooks:
        explanation.append("Discounts attract price-sensitive customers")

    if "AI-driven marketing" in trends:
        explanation.append("AI is becoming a dominant trend in marketing strategies")

    llm_reasoning = qwen_generate(str(explanation))

    return {
        "reasoning": explanation[:5],
        "llm_reasoning": llm_reasoning,
        "confidence_factor": len(explanation) * 10,
        "status": "reasoned"
    }
