from core.logging_utils import get_logger


logger = get_logger("team58.execution")


def execution_tool(decision: dict, structured: dict, validated: dict, budget_tier: str) -> dict:
    logger.info("execution:start")
    chosen_strategy = decision.get("selected_strategy", "Performance marketing")
    top_opportunity = (validated.get("validated_opportunities") or [{}])[0]

    if chosen_strategy == "Performance marketing":
        platforms = ["Google Search", "LinkedIn Ads", "Retargeting"]
        timeline = ["Week 1: audit funnel and messaging", "Week 2: launch paid experiments", "Weeks 3-4: optimize conversion paths"]
        budget_split = {"Paid acquisition": 55, "Creative/testing": 20, "Lifecycle nurture": 15, "Analytics": 10}
    elif chosen_strategy == "Emotional marketing":
        platforms = ["LinkedIn", "YouTube", "Email nurture"]
        timeline = ["Week 1: craft narrative pillars", "Week 2: launch proof-led content", "Weeks 3-4: expand audience nurture"]
        budget_split = {"Creative/story assets": 35, "Distribution": 30, "Lifecycle nurture": 20, "Analytics": 15}
    else:
        platforms = ["LinkedIn", "Industry media", "Webinars"]
        timeline = ["Week 1: finalize positioning", "Week 2: publish authority content", "Weeks 3-4: run awareness distribution"]
        budget_split = {"Content and proof": 35, "Awareness distribution": 35, "Events/webinars": 20, "Analytics": 10}

    if budget_tier == "low":
        budget_split = {key: value for key, value in budget_split.items()}
        platforms = platforms[:2]
    elif budget_tier == "high":
        platforms.append("Partner programs")

    result = {
        "campaign_strategy": chosen_strategy,
        "target_audience": structured.get("audience"),
        "priority_opportunity": top_opportunity.get("name"),
        "platform_selection": platforms,
        "timeline": timeline,
        "budget_allocation": budget_split,
        "actions": [
            f"Translate '{top_opportunity.get('name')}' into channel-specific messaging.",
            "Map each supporting source into proof points for copy and landing pages.",
            "Launch the first wave and review source-backed performance signals weekly.",
        ],
    }
    logger.info("execution:done strategy=%s", chosen_strategy)
    return result
