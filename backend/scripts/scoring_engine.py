import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


HIGH_VALUE_THRESHOLD = 70
HIGH_VALUE_OUTPUT_PATH = Path("data/processed/high_value_data.json")

TREND_KEYWORDS = {
    "viral": 28,
    "trending": 26,
    "trend": 18,
    "growth": 18,
    "ai": 16,
    "automation": 16,
}

BUYING_INTENT_KEYWORDS = {
    "buy": 30,
    "service": 18,
    "software": 18,
    "tool": 16,
    "solution": 18,
}

COMPETITION_KEYWORDS = {
    "popular": 24,
    "saturated": 34,
    "crowded": 34,
}

TOPIC_TAGS = {
    "AI": ["ai", "gpt", "llm"],
    "Automation": ["automation", "agent", "workflow"],
    "SaaS": ["saas", "software", "subscription"],
    "BuyingIntent": ["buy", "service", "tool", "solution"],
    "Competition": ["popular", "saturated", "crowded"],
    "Growth": ["growth", "viral", "trending", "trend"],
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def keyword_score(text: str, keyword_weights: Dict[str, int]) -> int:
    lowered = text.lower()
    score = 0

    for keyword, weight in keyword_weights.items():
        matches = len(re.findall(rf"\b{re.escape(keyword)}\b", lowered))
        if matches:
            score += min(matches, 2) * weight

    return clamp_score(score)


def derive_tags(text: str, source: str, existing_tags: Iterable[Any] | None = None) -> List[str]:
    tags: List[str] = []

    for tag in existing_tags or []:
        normalized = normalize_text(tag)
        if normalized and normalized not in tags:
            tags.append(normalized)

    source_tag = normalize_text(source)
    if source_tag and source_tag not in tags:
        tags.append(source_tag)

    lowered = text.lower()
    for tag_name, keywords in TOPIC_TAGS.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords):
            if tag_name not in tags:
                tags.append(tag_name)

    if not tags:
        tags.append("General")

    return tags


def standardize_item(item: Any, default_source: str = "unknown") -> Dict[str, Any] | None:
    if isinstance(item, dict):
        text = normalize_text(item.get("text") or item.get("title") or item.get("content"))
        source = normalize_text(item.get("source")) or default_source
        processed = bool(item.get("processed", False))
        collected_at = normalize_text(item.get("collected_at")) or utc_timestamp()
        tags = derive_tags(text, source, item.get("tags", []))
    else:
        text = normalize_text(item)
        source = default_source
        processed = False
        collected_at = utc_timestamp()
        tags = derive_tags(text, source, [])

    if not text:
        return None

    return {
        "text": text,
        "source": source,
        "processed": processed,
        "tags": tags,
        "collected_at": collected_at,
        "trend_score": 0,
        "buying_intent_score": 0,
        "competition_score": 0,
        "opportunity_score": 0,
    }


def score_item(item: Dict[str, Any]) -> Dict[str, Any]:
    standardized = standardize_item(item, item.get("source", "unknown")) if isinstance(item, dict) else standardize_item(item)
    if not standardized:
        raise ValueError("Cannot score an item without text")

    text = standardized["text"]
    trend_score = keyword_score(text, TREND_KEYWORDS)
    buying_intent_score = keyword_score(text, BUYING_INTENT_KEYWORDS)
    competition_score = keyword_score(text, COMPETITION_KEYWORDS)

    opportunity_score = clamp_score(
        (trend_score * 0.4 + buying_intent_score * 0.4) - (competition_score * 0.2)
    )

    standardized.update(
        {
            "trend_score": trend_score,
            "buying_intent_score": buying_intent_score,
            "competition_score": competition_score,
            "opportunity_score": opportunity_score,
        }
    )
    return standardized


def score_items(items: Iterable[Any], default_source: str = "unknown") -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []

    for item in items:
        try:
            standardized = standardize_item(item, default_source=default_source)
            if not standardized:
                continue
            scored.append(score_item(standardized))
        except Exception as exc:
            print(f"Scoring Error: {exc}")

    return scored


def filter_high_value_items(items: Iterable[Dict[str, Any]], threshold: int = HIGH_VALUE_THRESHOLD) -> List[Dict[str, Any]]:
    return [item for item in items if item.get("opportunity_score", 0) >= threshold]


def sort_by_opportunity(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda item: item.get("opportunity_score", 0), reverse=True)


def save_json(data: Any, path: Path | str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with open(target, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_high_value_data(path: Path | str = HIGH_VALUE_OUTPUT_PATH) -> List[Dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []

    try:
        with open(target, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except Exception as exc:
        print(f"High Value Load Error: {exc}")
        return []
