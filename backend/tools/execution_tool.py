from core.logging_utils import get_logger


logger = get_logger("team58.execution")


def execution_tool(decision: dict, structured: dict, validated: dict, budget_tier: str) -> dict:
    logger.info("execution:start")
    chosen_strategy = decision.get("selected_strategy", "Performance marketing")
    top_opportunity = (validated.get("validated_opportunities") or [{}])[0]
    opportunity_name = str(
        top_opportunity.get("name") or top_opportunity.get("title") or top_opportunity.get("opportunity") or ""
    ).strip()
    audience = str(structured.get("audience") or "").strip()

    if chosen_strategy == "Performance marketing":
        platforms = ["Google Search", "LinkedIn Ads", "Retargeting"]
        budget_split = {"Paid acquisition": 55, "Creative/testing": 20, "Lifecycle nurture": 15, "Analytics": 10}
    elif chosen_strategy == "Emotional marketing":
        platforms = ["LinkedIn", "YouTube", "Email nurture"]
        budget_split = {"Creative/story assets": 35, "Distribution": 30, "Lifecycle nurture": 20, "Analytics": 15}
    else:
        platforms = ["LinkedIn", "Industry media", "Webinars"]
        budget_split = {"Content and proof": 35, "Awareness distribution": 35, "Events/webinars": 20, "Analytics": 10}

    if budget_tier == "low":
        budget_split = {key: value for key, value in budget_split.items()}
        platforms = platforms[:2]
    elif budget_tier == "high":
        platforms.append("Partner programs")

    # Use a dynamic, non-week-based timeline (avoid static template output).
    headline = opportunity_name or "the top opportunity"
    who = audience or "your target audience"
    primary_platform = platforms[0] if platforms else "a priority channel"
    timeline = [
        f"Day 1: Review the current customer journey and identify the main blocker for {headline}.",
        f"Days 2-3: Draft messaging and proof points that speak directly to {who}.",
        f"Days 4-7: Run a controlled experiment on {primary_platform} and compare results to a baseline.",
    ]

    result = {
        "campaign_strategy": chosen_strategy,
        "target_audience": structured.get("audience"),
        "priority_opportunity": top_opportunity.get("name"),
        "platform_selection": platforms,
        "timeline": timeline,
        "budget_allocation": budget_split,
        "actions": [
            f"Translate '{headline}' into channel-specific messaging for {primary_platform}.",
            "Map each supporting source into proof points for copy and landing pages.",
            "Review performance signals and adjust based on observed blockers (not assumptions).",
        ],
    }
    logger.info("execution:done strategy=%s", chosen_strategy)
    return result
