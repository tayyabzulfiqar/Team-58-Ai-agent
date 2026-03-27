from typing import Any, Dict, List

from scripts.intelligence_tools import build_platform_mix, call_model_json


def summarize_insights(insights: Dict[str, Any]) -> str:
    trends = insights.get("trends", [])[:4]
    opportunities = insights.get("opportunities", [])[:4]
    trend_summary = ", ".join(item.get("trend", "general") for item in trends) or "general demand"
    opportunity_summary = ", ".join(item.get("trend", "general") for item in opportunities) or "audience expansion"
    return f"Top trends: {trend_summary}. Opportunities: {opportunity_summary}."


def summarize_strategies(strategies: List[Dict[str, Any]]) -> str:
    top_items = strategies[:4]
    return " | ".join(
        f"{item.get('pattern', 'trend')}: {item.get('marketing_hook', item.get('solution', 'growth angle'))}"
        for item in top_items
    ) or "Use sharp hooks, premium positioning, and conversion-led social storytelling."


def build_30_day_roadmap(name: str, content_type: str) -> List[str]:
    return [
        f"Week 1: Reset positioning for {name} around {content_type} authority and Dubai relevance.",
        "Week 2: Launch high-frequency short-form testing with 5-7 aggressive hook variants.",
        "Week 3: Layer in creator collaborations, paid amplification, and retargeting audiences.",
        "Week 4: Convert momentum into brand partnerships, lead capture, and a flagship content drop.",
    ]


def build_fallback_growth_plan(
    celebrity_data: Dict[str, Any], insights: Dict[str, Any], strategies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    name = celebrity_data.get("name", "the celebrity")
    content_type = celebrity_data.get("top_content", "creator")
    engagement = celebrity_data.get("engagement_level", "Moderate")
    platform_mix = celebrity_data.get("growth_platform_focus") or build_platform_mix(content_type)
    insights_summary = summarize_insights(insights)
    strategy_summary = summarize_strategies(strategies)

    return {
        "growth_plan": (
            f"Push {name} as a high-status Dubai market asset by pairing {content_type} storytelling with luxury, culture, "
            "and conversion-led collaborations. Build authority fast, then monetize attention through brand-safe repeatable formats."
        ),
        "content_strategy": (
            f"Use premium short-form edits, local relevance hooks, social proof, and campaign-native CTAs. "
            f"{insights_summary} Strategic angle: {strategy_summary}"
        ),
        "platform_focus": platform_mix,
        "posting_schedule": {
            "TikTok": "2 posts daily, 1 trend response within 6 hours, 3 creator stitches weekly",
            "Instagram": "1 Reel daily, 5-8 Stories daily, 2 collaboration posts weekly",
            "YouTube": "2 Shorts weekly, 1 long-form or compilation asset weekly",
        },
        "campaign_plan_30_day": build_30_day_roadmap(name, content_type),
    }


def run(celebrity_data: Dict[str, Any], insights: Dict[str, Any], strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        fallback = build_fallback_growth_plan(celebrity_data, insights, strategies)
        prompt = (
            "Create a tactical Dubai celebrity growth plan. Return strict JSON with keys: "
            "growth_plan, content_strategy, platform_focus, posting_schedule, campaign_plan_30_day.\n\n"
            f"Celebrity data: {celebrity_data}\n"
            f"Insights: {summarize_insights(insights)}\n"
            f"Strategies: {summarize_strategies(strategies)}"
        )

        ai_result = call_model_json(
            prompt=prompt,
            required_keys=["growth_plan", "content_strategy", "platform_focus", "posting_schedule", "campaign_plan_30_day"],
            system_prompt="You are a celebrity growth hacker and GCC expansion strategist producing tactical, client-ready plans.",
            timeout=12,
        )
        return ai_result or fallback
    except Exception as exc:
        print("Growth Agent Error:", exc)
        return build_fallback_growth_plan(celebrity_data, insights, strategies)
