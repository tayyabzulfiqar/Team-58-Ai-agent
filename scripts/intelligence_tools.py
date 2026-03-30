import json
import os
import re
from typing import Any, Dict, Iterable, List

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("API_KEY", "").strip()
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "").strip()
SEARXNG_URL = os.getenv("SEARXNG_URL", "https://searx.be").rstrip("/")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "").strip()
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

API_URL = f"{BASE_URL}/v1/chat/completions" if BASE_URL else "https://api.openai.com/v1/chat/completions"

FALLBACK_CELEBRITIES = [
    {
        "name": "Cristiano Ronaldo",
        "category": "sports",
        "audience_size": 98,
        "engagement_potential": 92,
        "virality_probability": 90,
        "brand_alignment_score": 94,
        "primary_geo": "Middle East, Europe, South Asia",
        "age_band": "18-34",
        "interests": ["fitness", "luxury lifestyle", "football", "fashion"],
        "signature_formats": ["training reels", "luxury brand shoots", "short motivational clips"],
        "summary": "Global football icon with elite luxury pull, GCC resonance, and broad conversion power across sport, fashion, and hospitality.",
    },
    {
        "name": "Taylor Swift",
        "category": "music",
        "audience_size": 95,
        "engagement_potential": 88,
        "virality_probability": 93,
        "brand_alignment_score": 84,
        "primary_geo": "North America, Europe, GCC affluent youth",
        "age_band": "16-34",
        "interests": ["music", "live experiences", "fashion", "premium lifestyle"],
        "signature_formats": ["tour clips", "fan-story content", "behind-the-scenes storytelling"],
        "summary": "High-conviction fandom brand with exceptional virality, premium consumer intent, and event-led monetization strength.",
    },
    {
        "name": "MrBeast",
        "category": "creator",
        "audience_size": 96,
        "engagement_potential": 94,
        "virality_probability": 97,
        "brand_alignment_score": 89,
        "primary_geo": "Global, MENA youth, North America, South Asia",
        "age_band": "13-30",
        "interests": ["challenge content", "entrepreneurship", "gaming", "food brands"],
        "signature_formats": ["stunts", "giveaways", "challenge videos", "high-retention hooks"],
        "summary": "Top-tier creator with unmatched viral packaging, youth relevance, and powerful commerce crossover for GCC brand launches.",
    },
    {
        "name": "Zendaya",
        "category": "fashion",
        "audience_size": 86,
        "engagement_potential": 84,
        "virality_probability": 82,
        "brand_alignment_score": 91,
        "primary_geo": "North America, Europe, Middle East luxury audience",
        "age_band": "18-34",
        "interests": ["fashion", "beauty", "film", "luxury travel"],
        "signature_formats": ["editorial visuals", "red-carpet moments", "beauty partnerships"],
        "summary": "Premium fashion and entertainment figure with strong luxury compatibility and high-value audience appeal in Dubai.",
    },
    {
        "name": "Virat Kohli",
        "category": "sports",
        "audience_size": 93,
        "engagement_potential": 90,
        "virality_probability": 87,
        "brand_alignment_score": 92,
        "primary_geo": "India, UAE, South Asia diaspora",
        "age_band": "18-40",
        "interests": ["cricket", "fitness", "family lifestyle", "fashion"],
        "signature_formats": ["match clips", "fitness content", "brand-led lifestyle edits"],
        "summary": "Massive South Asian and UAE appeal with strong trust, sports authority, and direct fit for Dubai consumer brands.",
    },
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def safe_json_loads(value: str) -> Dict[str, Any] | None:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def safe_request(method: str, url: str, timeout: int = 10, **kwargs) -> requests.Response | None:
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except Exception as exc:
        print(f"Request Error [{method} {url}]: {exc}")
        return None


def search_searxng(query: str, limit: int = 5) -> List[Dict[str, str]]:
    response = safe_request(
        "GET",
        f"{SEARXNG_URL}/search",
        params={"q": query, "format": "json"},
        timeout=15,
    )
    if response is None:
        return []

    try:
        data = response.json()
    except Exception as exc:
        print(f"SearXNG Parse Error: {exc}")
        return []

    if not isinstance(data, dict):
        return []

    results = []
    for item in data.get("results", [])[:limit]:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "title": normalize_text(item.get("title")),
                "url": normalize_text(item.get("url")),
                "content": normalize_text(item.get("content")),
                "source": normalize_text(item.get("engine")) or "searxng",
            }
        )
    return results


def scrape_with_firecrawl(url: str) -> str:
    if not FIRECRAWL_API_KEY or not url:
        return ""

    response = safe_request(
        "POST",
        "https://api.firecrawl.dev/v1/scrape",
        timeout=20,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"url": url, "formats": ["markdown"]},
    )
    if response is None:
        return ""

    try:
        payload = response.json()
    except Exception as exc:
        print(f"Firecrawl Parse Error: {exc}")
        return ""

    data = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(data, dict):
        return normalize_text(data.get("markdown") or data.get("content") or "")
    if isinstance(payload, dict):
        return normalize_text(payload.get("markdown") or payload.get("content") or "")
    return ""


def gather_search_context(queries: Iterable[str], limit_per_query: int = 5, scrape_top: int = 2) -> List[Dict[str, str]]:
    collected: List[Dict[str, str]] = []

    for query in queries:
        for result in search_searxng(query, limit=limit_per_query):
            collected.append(result)

    deduped: List[Dict[str, str]] = []
    seen_urls = set()
    for result in collected:
        url = result.get("url", "")
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        deduped.append(result)

    for result in deduped[:scrape_top]:
        scraped_text = scrape_with_firecrawl(result.get("url", ""))
        if scraped_text:
            result["scraped_text"] = scraped_text

    return deduped


def call_model_json(prompt: str, required_keys: List[str], system_prompt: str, timeout: int = 10) -> Dict[str, Any] | None:
    if not API_KEY or not BASE_URL:
        return None

    response = safe_request(
        "POST",
        API_URL,
        timeout=timeout,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
            "max_tokens": 500,
        },
    )
    if response is None:
        return None

    try:
        content = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        print(f"Model Response Error: {exc}")
        return None

    parsed = safe_json_loads(content)
    if parsed and all(key in parsed for key in required_keys):
        return parsed

    cleaned = content.strip("`\n ")
    parsed = safe_json_loads(cleaned)
    if parsed and all(key in parsed for key in required_keys):
        return parsed

    return None


def keyword_match_score(text: str, keywords: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def best_content_type(text: str) -> str:
    content_map = {
        "music": ["song", "music", "album", "concert", "singer", "artist"],
        "film": ["film", "movie", "actor", "actress", "cinema"],
        "fashion": ["fashion", "style", "beauty", "luxury", "designer"],
        "sports": ["sport", "athlete", "fitness", "training", "match"],
        "comedy": ["comedy", "funny", "standup", "entertainment"],
        "creator": ["youtube", "instagram", "tiktok", "content", "creator"],
    }

    lowered = text.lower()
    best_label = "creator"
    best_score = 0
    for label, keywords in content_map.items():
        score = keyword_match_score(lowered, keywords)
        if score > best_score:
            best_label = label
            best_score = score
    return best_label


def summarize_search_text(results: Iterable[Dict[str, str]]) -> str:
    chunks = []
    for result in results:
        chunks.append(normalize_text(result.get("title")))
        chunks.append(normalize_text(result.get("content")))
        chunks.append(normalize_text(result.get("scraped_text")))
    return " ".join(chunk for chunk in chunks if chunk)


def has_telegram_credentials() -> bool:
    return bool(TELEGRAM_API_ID and TELEGRAM_API_HASH)


def fetch_telegram_mentions() -> List[Dict[str, str]]:
    if not has_telegram_credentials():
        return []

    # Placeholder transport: production-safe fallback when a Telegram client is not configured.
    return []


def score_brand_fit_from_text(text: str) -> int:
    luxury_terms = ["luxury", "fashion", "beauty", "hotel", "tourism", "dubai", "uae", "brand", "campaign"]
    sports_terms = ["sport", "fitness", "performance"]
    entertainment_terms = ["music", "film", "creator", "viral", "fan"]
    score = keyword_match_score(text, luxury_terms) * 5
    score += keyword_match_score(text, sports_terms) * 4
    score += keyword_match_score(text, entertainment_terms) * 4
    return max(55, min(98, score + 55))


def extract_celebrity_names(text: str) -> List[str]:
    pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
    blocked = {"Middle East", "United States", "North America", "South Asia", "Dubai Mall"}
    found = []
    for match in re.findall(pattern, text):
        candidate = normalize_text(match)
        if candidate in blocked:
            continue
        if candidate not in found:
            found.append(candidate)
    return found


def fallback_discovery_candidates() -> List[Dict[str, Any]]:
    return [item.copy() for item in FALLBACK_CELEBRITIES]


def fetch_firecrawl_topic_context(topic: str) -> str:
    if not FIRECRAWL_API_KEY:
        return ""

    prompt_url = f"https://www.google.com/search?q={requests.utils.quote(topic)}"
    return scrape_with_firecrawl(prompt_url)


def discover_trending_celebrities(limit: int = 3) -> List[Dict[str, Any]]:
    queries = [
        "trending celebrities 2026 Dubai",
        "viral celebrity campaigns Middle East",
        "top influencers celebrities brand deals UAE",
    ]
    results = gather_search_context(queries, limit_per_query=5, scrape_top=2)
    telegram_mentions = fetch_telegram_mentions()
    context_text = summarize_search_text(results + telegram_mentions)
    context_text += " " + fetch_firecrawl_topic_context("trending celebrity news Dubai")

    discovered_names = extract_celebrity_names(context_text)
    fallback_by_name = {item["name"]: item for item in FALLBACK_CELEBRITIES}
    candidates: List[Dict[str, Any]] = []

    for name in discovered_names:
        baseline = fallback_by_name.get(name)
        if baseline:
            candidate = baseline.copy()
            candidate["discovery_source"] = "live"
            candidates.append(candidate)

    if len(candidates) < limit:
        existing = {item["name"] for item in candidates}
        for celebrity in FALLBACK_CELEBRITIES:
            if celebrity["name"] in existing:
                continue
            candidate = celebrity.copy()
            candidate["discovery_source"] = "fallback"
            candidates.append(candidate)
            if len(candidates) >= max(limit, 5):
                break

    return rank_celebrities(candidates)[:limit]


def rank_celebrities(candidates: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ranked: List[Dict[str, Any]] = []
    for candidate in candidates:
        audience_size = int(candidate.get("audience_size", 70))
        engagement_potential = int(candidate.get("engagement_potential", 70))
        virality_probability = int(candidate.get("virality_probability", 70))
        brand_alignment_score = int(candidate.get("brand_alignment_score", 70))
        total_score = round(
            engagement_potential * 0.3
            + audience_size * 0.25
            + virality_probability * 0.25
            + brand_alignment_score * 0.2
        )
        enriched = candidate.copy()
        enriched["ranking_score"] = total_score
        ranked.append(enriched)

    ranked.sort(key=lambda item: item.get("ranking_score", 0), reverse=True)
    return ranked


def build_platform_mix(category: str) -> Dict[str, str]:
    defaults = {
        "creator": {
            "TikTok": "Aggressive short-form hooks, challenge formats, and creator collabs.",
            "Instagram": "Reels plus Stories for community conversion and branded visuals.",
            "YouTube": "Longer storytelling and episodic campaign assets.",
        },
        "music": {
            "TikTok": "Snippet-driven hooks, trend hijacks, duet formats, and fan remix loops.",
            "Instagram": "Reels, backstage visuals, and premium fan-community storytelling.",
            "YouTube": "Performance cuts, mini-docs, and event recap edits.",
        },
        "sports": {
            "TikTok": "Training moments, challenge mechanics, and motivational edits.",
            "Instagram": "Luxury lifestyle, performance clips, and sponsor integration.",
            "YouTube": "Training series, brand narratives, and documentary-style proof.",
        },
        "fashion": {
            "TikTok": "Outfit transitions, backstage hooks, and trend-native product reveals.",
            "Instagram": "Premium visual storytelling, Reels, and editorial partnership posts.",
            "YouTube": "Campaign films, interviews, and collection launches.",
        },
        "film": {
            "TikTok": "Scene-inspired hooks, memeable moments, and persona-driven clips.",
            "Instagram": "Press visuals, behind-the-scenes footage, and fan activation.",
            "YouTube": "Interviews, trailers, and long-form narratives.",
        },
    }
    return defaults.get(category, defaults["creator"]).copy()


def estimate_roi(brand_alignment_score: int, engagement_potential: int, audience_size: int) -> Dict[str, str]:
    expected_reach = int((audience_size * 12000) + (engagement_potential * 4000))
    lead_range = f"{int(expected_reach * 0.002):,}-{int(expected_reach * 0.0045):,}"
    revenue_range = f"${int(brand_alignment_score * 1800):,}-${int(brand_alignment_score * 3200):,}"
    roas = round((brand_alignment_score * 0.04) + (engagement_potential * 0.03), 1)
    return {
        "estimated_reach": f"{expected_reach:,}",
        "estimated_leads": lead_range,
        "estimated_revenue": revenue_range,
        "projected_roas": f"{roas}x",
    }
