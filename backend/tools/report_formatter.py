import re
from typing import Any, Dict, List, Optional


def _to_clean_sentence(value: Any, fallback: str) -> str:
    raw = value.strip() if isinstance(value, str) else ""
    text = raw if raw else fallback
    if not text:
        text = fallback
    text = text[0].upper() + text[1:] if text else fallback
    return text if re.search(r"[.!?]\s*$", text) else f"{text}."


def _unique_non_empty(items: Any) -> List[str]:
    if not isinstance(items, list):
        return []
    seen = set()
    out: List[str] = []
    for item in items:
        if not isinstance(item, str):
            continue
        trimmed = item.strip()
        if not trimmed:
            continue
        key = trimmed.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(trimmed)
    return out


_WEEK_PREFIX_RE = re.compile(r"^\s*weeks?\s*\d+(?:\s*-\s*\d+)?\s*:\s*", re.IGNORECASE)


def _strip_week_prefix(text: str) -> str:
    return _WEEK_PREFIX_RE.sub("", text).strip()


def _capitalize_first(text: str) -> str:
    t = text.strip()
    return (t[0].upper() + t[1:]) if t else t


def _to_title_case(word: str) -> str:
    w = word.strip()
    return (w[0].upper() + w[1:].lower()) if w else w


def format_report(data: Optional[Dict[str, Any]]) -> str:
    data = data or {}

    main_problem = _to_clean_sentence(data.get("main_problem"), "No main problem provided")
    key_insight = _to_clean_sentence(data.get("key_insight"), "No key insight provided")

    strategy = data.get("strategy") if isinstance(data.get("strategy"), dict) else {}
    strategy_points = _unique_non_empty(strategy.get("points"))
    strategy_block = (
        "\n".join([f"• {_capitalize_first(_strip_week_prefix(p) or p)}" for p in strategy_points])
        if strategy_points
        else "• No strategy points provided"
    )

    action_plan = data.get("action_plan") if isinstance(data.get("action_plan"), list) else []
    steps: List[str] = []
    for item in action_plan:
        if not isinstance(item, dict):
            continue
        title = item.get("title").strip() if isinstance(item.get("title"), str) else ""
        title = _capitalize_first(_strip_week_prefix(title)) if title else ""
        timeline = item.get("timeline").strip() if isinstance(item.get("timeline"), str) else ""
        combined = title
        if timeline:
            combined = f"{combined} ({timeline})" if combined else f"({timeline})"
        if combined.strip():
            steps.append(combined.strip())
    execution_block = "\n".join([f"{i + 1}. {s}" for i, s in enumerate(steps)]) if steps else "1. No execution steps provided"

    campaign = data.get("campaign_plan") if isinstance(data.get("campaign_plan"), dict) else {}
    message = campaign.get("message").strip() if isinstance(campaign.get("message"), str) else ""
    goal = campaign.get("goal").strip() if isinstance(campaign.get("goal"), str) else ""
    channels_raw = campaign.get("channels") if isinstance(campaign.get("channels"), list) else []
    channels = [_to_title_case(c) for c in channels_raw if isinstance(c, str) and c.strip()]
    channels_text = ", ".join(channels) if channels else ""

    campaign_parts: List[str] = []
    if message:
        campaign_parts.append(f"Message: {_to_clean_sentence(message, '').rstrip('.')}.")
    if goal:
        campaign_parts.append(f"Goal: {_to_clean_sentence(goal, '').rstrip('.')}.")
    if channels_text:
        campaign_parts.append(f"Channels: {_to_clean_sentence(channels_text, '').rstrip('.')}.")
    campaign_block = (
        " ".join(campaign_parts) if campaign_parts else "Message: Not provided. Goal: Not provided. Channels: Not provided."
    )

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

