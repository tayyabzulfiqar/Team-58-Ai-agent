import re
from typing import Any, Dict, List

from scripts.intelligence_tools import (
    best_content_type,
    build_platform_mix,
    call_model_json,
    estimate_roi,
    fallback_discovery_candidates,
    gather_search_context,
    summarize_search_text,
)


DEFAULT_BREAKDOWN = {
    "geo": "Global audience with strong GCC, Europe, and South Asia spillover.",
    "age": "18-34",
    "interests": ["lifestyle", "entertainment", "fashion", "social trends"],
}


def get_fallback_profile(celebrity_name: str) -> Dict[str, Any]:
    for candidate in fallback_discovery_candidates():
        if candidate["name"].lower() == celebrity_name.lower():
            return candidate
    fallback = fallback_discovery_candidates()[0]
    fallback["name"] = celebrity_name or fallback["name"]
    return fallback


def extract_follower_data(text: str, fallback_profile: Dict[str, Any]) -> str:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(million|m)\s+followers",
        r"(\d+(?:\.\d+)?)\s*(million|m)\s+subscribers",
        r"(\d+(?:\.\d+)?)\s*(thousand|k)\s+followers",
        r"(\d[\d,]{3,})\s+followers",
    ]

    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return match.group(0)

    size = fallback_profile.get("audience_size", 80)
    return f"Estimated audience strength score {size}/100"


def infer_geography(text: str, fallback_profile: Dict[str, Any]) -> str:
    geographies = {
        "Dubai / UAE": ["dubai", "uae", "united arab emirates", "middle east", "gulf"],
        "South Asia": ["india", "pakistan", "bangladesh", "south asia"],
        "North America": ["usa", "united states", "canada", "north america"],
        "UK / Europe": ["uk", "england", "europe", "london"],
    }

    lowered = text.lower()
    scores = {label: sum(1 for keyword in keywords if keyword in lowered) for label, keywords in geographies.items()}
    best_label = max(scores, key=scores.get)
    if scores[best_label] == 0:
        return fallback_profile.get("primary_geo", DEFAULT_BREAKDOWN["geo"])
    return best_label


def infer_engagement_level(text: str, fallback_profile: Dict[str, Any]) -> str:
    lowered = text.lower()
    high_signals = ["viral", "high engagement", "sold out", "trending", "millions of views"]
    medium_signals = ["engagement", "active audience", "fan base", "consistent views"]

    high_score = sum(1 for term in high_signals if term in lowered)
    medium_score = sum(1 for term in medium_signals if term in lowered)
    fallback_score = fallback_profile.get("engagement_potential", 80)

    if high_score >= 2 or fallback_score >= 90:
        return "High"
    if high_score >= 1 or medium_score >= 2 or fallback_score >= 80:
        return "Moderate to High"
    return "Moderate"


def build_market_fit(content_type: str, geography: str, engagement_level: str, fallback_profile: Dict[str, Any]) -> str:
    fit_map = {
        "fashion": "Strong fit for Dubai luxury, retail, beauty, and hospitality campaigns.",
        "music": "Strong fit for Dubai entertainment, events, nightlife, and premium consumer activations.",
        "film": "Strong fit for Dubai tourism, cinema launches, entertainment partnerships, and premium brand campaigns.",
        "sports": "Strong fit for Dubai wellness, sportswear, automotive, and performance-led partnerships.",
        "comedy": "Good fit for Dubai entertainment, youth campaigns, and short-form branded storytelling.",
        "creator": "Good fit for Dubai lifestyle, creator commerce, food delivery, fintech, and social-first partnerships.",
    }

    base = fit_map.get(content_type, fit_map["creator"])
    if "Dubai" in geography or "UAE" in geography:
        return f"{base} Existing regional relevance increases conversion potential."
    if engagement_level == "High":
        return f"{base} High engagement improves awareness velocity and sponsorship upside."
    return f"{base} {fallback_profile.get('summary', '')}".strip()


def build_audience_breakdown(fallback_profile: Dict[str, Any], geography: str) -> Dict[str, Any]:
    return {
        "geo": geography,
        "age": fallback_profile.get("age_band", DEFAULT_BREAKDOWN["age"]),
        "interests": fallback_profile.get("interests", DEFAULT_BREAKDOWN["interests"]),
    }


def build_content_angles(name: str, category: str) -> List[Dict[str, str]]:
    angle_bank = {
        "music": [
            {"hook": f"{name} x Dubai after-dark energy", "reel_idea": "Concert-style lifestyle montage with luxury city edits", "viral_format": "Fast-cut trend audio remix"},
            {"hook": f"What {name} would do in 24 hours in Dubai", "reel_idea": "Fan fantasy itinerary with branded stops", "viral_format": "POV story reel"},
            {"hook": f"{name}'s fan moment activation", "reel_idea": "User-generated fan reactions and creator duet chain", "viral_format": "Reaction stitching"},
        ],
        "sports": [
            {"hook": f"{name}'s Dubai performance routine", "reel_idea": "Training + recovery + luxury crossover montage", "viral_format": "Challenge-based transformation clip"},
            {"hook": "Can Dubai creators match this elite standard?", "reel_idea": "Creator challenge with brand sponsor", "viral_format": "Competition ladder"},
            {"hook": f"{name} style discipline meets Dubai ambition", "reel_idea": "Motivational short-form branded series", "viral_format": "Narrated progression arc"},
        ],
        "fashion": [
            {"hook": f"{name} redefines Dubai luxury", "reel_idea": "Editorial shoot mixed with retail or hotel brand integration", "viral_format": "Transition reel"},
            {"hook": f"Three Dubai looks inspired by {name}", "reel_idea": "Wardrobe carousel turned into shoppable content", "viral_format": "Before-after styling edit"},
            {"hook": f"{name}'s red-carpet energy for GCC brands", "reel_idea": "Premium still-motion hybrid campaign asset", "viral_format": "Moodboard montage"},
        ],
        "creator": [
            {"hook": f"{name} launches a Dubai challenge", "reel_idea": "High-retention challenge concept with audience participation", "viral_format": "Challenge loop"},
            {"hook": f"{name} picks the best Dubai brand experience", "reel_idea": "Fast-paced taste test or ranking format", "viral_format": "Countdown format"},
            {"hook": f"Why {name} would win Dubai social right now", "reel_idea": "Aggressive opinion-led reel with proof clips", "viral_format": "Hot-take explainer"},
        ],
    }
    return angle_bank.get(category, angle_bank["creator"])


def build_research_summary(name: str, fallback_profile: Dict[str, Any], market_fit: str, engagement_level: str) -> str:
    return (
        f"{name} is a high-leverage {fallback_profile.get('category', 'creator')} asset for Gulf-facing campaigns. "
        f"{fallback_profile.get('summary', '')} Current engagement is best classified as {engagement_level.lower()}, "
        f"which makes this talent suitable for awareness bursts, creator-led commerce, and premium brand storytelling. {market_fit}"
    )


def enrich_with_model(base_payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = (
        "Improve this celebrity intelligence object for a premium growth agency report. "
        "Return strict JSON with keys: research_summary, audience_breakdown, content_angles, growth_platform_focus, roi_projection.\n"
        f"Input: {base_payload}"
    )
    model_payload = call_model_json(
        prompt=prompt,
        required_keys=["research_summary", "audience_breakdown", "content_angles", "growth_platform_focus", "roi_projection"],
        system_prompt="You are a celebrity growth strategist building a premium intelligence report for brands in Dubai.",
        timeout=12,
    )
    if not model_payload:
        return base_payload

    merged = base_payload.copy()
    merged.update(model_payload)
    return merged


def run(celebrity_name: str) -> Dict[str, Any]:
    if not celebrity_name:
        return get_fallback_profile("")

    fallback_profile = get_fallback_profile(celebrity_name)
    queries = [
        f"{celebrity_name} followers engagement audience",
        f"{celebrity_name} Instagram YouTube TikTok followers demographics",
        f"{celebrity_name} audience geography Dubai UAE brand campaign",
    ]

    try:
        search_results = gather_search_context(queries, limit_per_query=4, scrape_top=2)
        combined_text = summarize_search_text(search_results)

        content_type = best_content_type(combined_text or fallback_profile.get("category", "creator"))
        geography = infer_geography(combined_text, fallback_profile)
        engagement_level = infer_engagement_level(combined_text, fallback_profile)
        follower_data = extract_follower_data(combined_text, fallback_profile)
        market_fit = build_market_fit(content_type, geography, engagement_level, fallback_profile)
        audience_breakdown = build_audience_breakdown(fallback_profile, geography)
        roi_projection = estimate_roi(
            fallback_profile.get("brand_alignment_score", 80),
            fallback_profile.get("engagement_potential", 80),
            fallback_profile.get("audience_size", 80),
        )

        base_payload: Dict[str, Any] = {
            "name": celebrity_name,
            "audience": f"{follower_data}; geography: {geography}",
            "top_content": content_type,
            "engagement_level": engagement_level,
            "market_fit": market_fit,
            "research_summary": build_research_summary(celebrity_name, fallback_profile, market_fit, engagement_level),
            "audience_breakdown": audience_breakdown,
            "content_angles": build_content_angles(celebrity_name, content_type),
            "growth_platform_focus": build_platform_mix(content_type),
            "roi_projection": roi_projection,
            "audience_size": fallback_profile.get("audience_size", 80),
            "engagement_potential": fallback_profile.get("engagement_potential", 80),
            "virality_probability": fallback_profile.get("virality_probability", 80),
            "brand_alignment_score": fallback_profile.get("brand_alignment_score", 80),
            "discovery_source": fallback_profile.get("discovery_source", "fallback"),
        }

        return enrich_with_model(base_payload)
    except Exception as exc:
        print("Celebrity Agent Error:", exc)
        content_type = fallback_profile.get("category", "creator")
        geography = fallback_profile.get("primary_geo", DEFAULT_BREAKDOWN["geo"])
        market_fit = build_market_fit(content_type, geography, "Moderate to High", fallback_profile)
        return {
            "name": celebrity_name,
            "audience": f"Estimated audience strength score {fallback_profile.get('audience_size', 80)}/100; geography: {geography}",
            "top_content": content_type,
            "engagement_level": "Moderate to High",
            "market_fit": market_fit,
            "research_summary": build_research_summary(celebrity_name, fallback_profile, market_fit, "Moderate to High"),
            "audience_breakdown": build_audience_breakdown(fallback_profile, geography),
            "content_angles": build_content_angles(celebrity_name, content_type),
            "growth_platform_focus": build_platform_mix(content_type),
            "roi_projection": estimate_roi(
                fallback_profile.get("brand_alignment_score", 80),
                fallback_profile.get("engagement_potential", 80),
                fallback_profile.get("audience_size", 80),
            ),
            "audience_size": fallback_profile.get("audience_size", 80),
            "engagement_potential": fallback_profile.get("engagement_potential", 80),
            "virality_probability": fallback_profile.get("virality_probability", 80),
            "brand_alignment_score": fallback_profile.get("brand_alignment_score", 80),
            "discovery_source": fallback_profile.get("discovery_source", "fallback"),
        }
