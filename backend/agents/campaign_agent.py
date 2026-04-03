import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("API_KEY", "").strip()
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")



CAMPAIGN_BLUEPRINTS = {
    "creator": {
        "platform": "TikTok + Instagram Reels",
        "posting_time": "7:30 PM GST",
        "idea": "48-hour Dubai challenge sprint with creator duets, brand giveaways, and paid retargeting cutdowns",
        "hook": "Turn viral attention into a Dubai conversion storm before the trend cools down",
    },
    "music": {
        "platform": "TikTok + Instagram + YouTube Shorts",
        "posting_time": "8:00 PM GST",
        "idea": "Dubai after-dark fan activation with teaser clips, venue partnerships, and remix-ready short-form moments",
        "hook": "Make the audience feel they are inside the biggest entertainment moment in Dubai this month",
    },
    "sports": {
        "platform": "Instagram Reels + TikTok + YouTube Shorts",
        "posting_time": "6:30 PM GST",
        "idea": "Performance-meets-luxury Dubai campaign with training content, challenge mechanics, and sponsor integration",
        "hook": "Package elite discipline as aspirational Dubai status and make the audience want in",
    },
    "fashion": {
        "platform": "Instagram Reels + Stories + TikTok",
        "posting_time": "8:30 PM GST",
        "idea": "Luxury capsule drop campaign with editorial visuals, creator seeding, and retail conversion hooks",
        "hook": "Own the Dubai luxury conversation with visually dominant short-form storytelling",
    },
    "film": {
        "platform": "Instagram + TikTok + YouTube",
        "posting_time": "7:00 PM GST",
        "idea": "Premiere-style Dubai narrative rollout with behind-the-scenes moments and tourism-led brand placements",
        "hook": "Blend cinematic presence with city-scale aspiration and make every post feel launch-worthy",
    },
    "general": {
        "platform": "Instagram + TikTok",
        "posting_time": "7:00 PM GST",
        "idea": "Dubai-first attention sprint with short-form hooks, creator collaboration, and retargeting layers",
        "hook": "Own attention quickly, then convert momentum into brand demand and inbound leads",
    },
}


def infer_campaign_type(strategy):
    text = " ".join(
        [
            str(strategy.get("pattern", "")),
            str(strategy.get("business_idea", "")),
            str(strategy.get("marketing_hook", "")),
            str(strategy.get("solution", "")),
        ]
    ).lower()

    if any(keyword in text for keyword in ["music", "concert", "fan", "album", "artist", "singer"]):
        return "music"
    if any(keyword in text for keyword in ["sport", "fitness", "performance", "football", "athlete"]):
        return "sports"
    if any(keyword in text for keyword in ["fashion", "luxury", "beauty", "style", "designer"]):
        return "fashion"
    if any(keyword in text for keyword in ["film", "movie", "cinema", "actor", "actress"]):
        return "film"
    if any(keyword in text for keyword in ["creator", "youtube", "tiktok", "social", "challenge"]):
        return "creator"
    return "general"


def fallback_campaign(strategy):
    campaign_type = infer_campaign_type(strategy)
    blueprint = CAMPAIGN_BLUEPRINTS.get(campaign_type, CAMPAIGN_BLUEPRINTS["general"])

    return {
        "idea": strategy.get("business_idea") or blueprint["idea"],
        "hook": strategy.get("marketing_hook") or blueprint["hook"],
        "platform": blueprint["platform"],
        "posting_time": blueprint["posting_time"],
    }


def parse_ai_response(text):
    try:
        data = json.loads(text)
        keys = ["idea", "hook", "platform", "posting_time"]
        if isinstance(data, dict) and all(key in data for key in keys):
            return {key: str(data[key]).strip() for key in keys}
    except json.JSONDecodeError:
        pass

    return None


def call_ai_api(strategy, retries=1, timeout=5):
    if not API_KEY or not BASE_URL:
        raise ValueError("API_KEY or BASE_URL not set")

    prompt = (
        f"Generate an aggressive Dubai-ready social campaign from this business strategy: {strategy.get('business_idea')}. "
        f"Hook: {strategy.get('marketing_hook')}. "
        f"Return JSON: {{\"idea\": \"campaign idea\", \"hook\": \"attention-grabbing hook\", "
        f"\"platform\": \"best platform mix\", \"posting_time\": \"optimal Gulf posting time\"}}"
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a celebrity campaign strategist for Dubai and GCC consumer brands."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()

            parsed = parse_ai_response(content)
            if parsed is not None:
                return parsed

            return fallback_campaign(strategy)

        except Exception:
            if attempt == retries:
                raise
            time.sleep(1)

    raise RuntimeError("AI API failed after retries")


def run(strategies):
    try:
        campaigns = []
        if not strategies:
            strategies = [
                {
                    "business_idea": "Launch a Dubai-focused celebrity growth campaign",
                    "marketing_hook": "Turn audience attention into premium Dubai brand momentum",
                }
            ]

        use_ai = False
        try:
            ping = requests.get(BASE_URL, timeout=2)
            use_ai = ping.status_code < 400
        except Exception:
            use_ai = False

        for strategy in strategies:
            if use_ai:
                try:
                    campaign = call_ai_api(strategy)
                except Exception:
                    campaign = fallback_campaign(strategy)
            else:
                campaign = fallback_campaign(strategy)

            campaigns.append(campaign)

        print(f"Generated {len(campaigns)} campaigns")
        return campaigns

    except Exception as exc:
        print("Campaign Agent Error:", exc)
        return []
