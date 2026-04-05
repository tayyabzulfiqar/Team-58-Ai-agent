from tools.cleaner_tool import cleaner_tool
from tools.analyzer_tool import analyzer_tool
from tools.reasoning_tool import reasoning_tool


def _infer_analysis_context(analysis):
    summary = analysis.get("insight_summary", "").lower()
    keywords = [keyword.lower() for keyword in analysis.get("keywords", [])]
    tokens = " ".join(keywords) + " " + summary

    top_strategies = []
    top_hooks = []
    market_trends = []

    if any(term in tokens for term in ["conversion", "growth", "lead", "performance"]):
        top_strategies.append("performance marketing")

    if any(term in tokens for term in ["emotion", "emotional", "engagement", "trigger"]):
        top_strategies.append("emotional marketing")

    if any(term in tokens for term in ["brand", "trust", "awareness"]):
        top_strategies.append("brand awareness")

    if any(term in tokens for term in ["urgent", "urgency", "now", "limited"]):
        top_hooks.append("urgency hook")

    if any(term in tokens for term in ["discount", "offer", "sale", "price"]):
        top_hooks.append("discount-based hook")

    if "ai" in tokens:
        market_trends.append("AI-driven marketing")

    if not top_strategies:
        top_strategies.append("performance marketing")

    return {
        **analysis,
        "top_strategies": top_strategies,
        "top_hooks": top_hooks,
        "market_trends": market_trends
    }


class DataAgent:
    def run(self, input_data):
        cleaned = cleaner_tool(input_data)
        analysis = analyzer_tool(cleaned)
        analysis = _infer_analysis_context(analysis)
        reasoning = reasoning_tool(analysis)

        return {
            "analysis": analysis,
            "reasoning": reasoning
        }
