from typing import Any, Dict, List, Optional


def _as_non_empty_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _as_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        t = item.strip()
        if t:
            out.append(t)
    return out


def format_report(data: Optional[Dict[str, Any]]) -> str:
    """
    Pure formatter: does not invent, rewrite, or replace content.
    It only arranges provided fields into a readable report.
    """
    data = data or {}

    main_problem = _as_non_empty_string(data.get("main_problem"))
    key_insight = _as_non_empty_string(data.get("key_insight"))

    strategy = data.get("strategy") if isinstance(data.get("strategy"), dict) else {}
    strategy_points = _as_string_list(strategy.get("points"))
    strategy_block = "\n".join([f"• {p}" for p in strategy_points])

    action_plan = data.get("action_plan") if isinstance(data.get("action_plan"), list) else []
    steps: List[str] = []
    for item in action_plan:
        if not isinstance(item, dict):
            continue
        title = _as_non_empty_string(item.get("title"))
        timeline = _as_non_empty_string(item.get("timeline"))
        if title and timeline:
            steps.append(f"{title} ({timeline})")
        else:
            combined = title or timeline
            if combined:
                steps.append(combined)
    execution_block = "\n".join([f"{i + 1}. {s}" for i, s in enumerate(steps)])

    campaign = data.get("campaign_plan") if isinstance(data.get("campaign_plan"), dict) else {}
    message = _as_non_empty_string(campaign.get("message"))
    goal = _as_non_empty_string(campaign.get("goal"))
    channels = _as_string_list(campaign.get("channels"))
    channels_text = ", ".join(channels)

    campaign_lines = []
    if message:
        campaign_lines.append(f"Message: {message}")
    if goal:
        campaign_lines.append(f"Goal: {goal}")
    if channels_text:
        campaign_lines.append(f"Channels: {channels_text}")
    campaign_block = "\n".join(campaign_lines)

    return "\n".join(
        [
            "Main Problem:",
            main_problem,
            "",
            "Key Insight:",
            key_insight,
            "",
            "Strategy:",
            strategy_block,
            "",
            "Execution Plan:",
            execution_block,
            "",
            "Campaign Plan:",
            campaign_block,
            "",
        ]
    )

