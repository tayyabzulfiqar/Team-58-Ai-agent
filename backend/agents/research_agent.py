import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from scripts.firecrawl_collector import fetch_firecrawl_data
from scripts.reddit_collector import fetch_reddit
from scripts.scoring_engine import (
    HIGH_VALUE_OUTPUT_PATH,
    filter_high_value_items,
    save_json,
    score_item,
    sort_by_opportunity,
    standardize_item,
    utc_timestamp,
)

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SEARXNG_URL = os.getenv("SEARXNG_URL", "https://searx.be")

RAW_OUTPUT_PATH = Path("data/raw/raw_data.json")

# Hacker News
HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_LIMIT = 25


def build_item(text, source, tags=None):
    return standardize_item(
        {
            "text": text,
            "source": source,
            "processed": False,
            "tags": tags or [],
            "collected_at": utc_timestamp(),
        }
    )


def normalize_source_records(records, default_source):
    normalized = []
    for record in records:
        item = standardize_item(record, default_source=default_source)
        if item:
            normalized.append(item)
    return normalized


def fetch_hn():
    print("Fetching Hacker News data...")

    try:
        response = requests.get(HN_TOP_URL, timeout=10)
        response.raise_for_status()

        story_ids = response.json()[:HN_LIMIT]
        results = []

        for story_id in story_ids:
            try:
                item = requests.get(HN_ITEM_URL.format(story_id), timeout=10).json()
                title = item.get("title") if isinstance(item, dict) else None
                if not title:
                    continue

                standardized = build_item(title, "hackernews", ["hn"])
                if standardized:
                    results.append(standardized)
            except Exception as exc:
                print(f"Error fetching HN item {story_id}: {exc}")

        print(f"HN: {len(results)}")
        return results

    except Exception as exc:
        print("HN Error:", exc)
        return []


def fetch_firecrawl():
    results = []

    try:
        if FIRECRAWL_API_KEY:
            raw = fetch_firecrawl_data()
            if isinstance(raw, dict):
                text = raw.get("content") or raw.get("data") or json.dumps(raw)
                if text:
                    standardized = build_item(str(text), "firecrawl", ["firecrawl"])
                    if standardized:
                        results.append(standardized)
            elif isinstance(raw, list):
                for item in raw:
                    standardized = standardize_item(item, default_source="firecrawl")
                    if standardized:
                        results.append(standardized)

        path = Path("data/raw/firecrawl_data.json")
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                local_data = json.load(file)

            iterable = local_data if isinstance(local_data, list) else [local_data]
            for item in iterable:
                standardized = standardize_item(item, default_source="firecrawl")
                if standardized:
                    results.append(standardized)

        print(f"Firecrawl: {len(results)}")
        return results

    except Exception as exc:
        print("Firecrawl Error:", exc)
        return []


def fetch_telegram_data():
    results = []

    if not TELEGRAM_BOT_TOKEN:
        print("Telegram token not available")
        return results

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(url, params={"limit": 100}, timeout=10)
        response.raise_for_status()
        payload = response.json()

        for update in payload.get("result", []):
            message = update.get("message") or update.get("channel_post") or update.get("edited_message")
            if not message:
                continue

            text = message.get("text") or message.get("caption")
            if not text:
                continue

            standardized = build_item(str(text), "telegram", ["telegram"])
            if standardized:
                results.append(standardized)

        print(f"Telegram: {len(results)}")
        return results
    except Exception as exc:
        print("Telegram Error:", exc)
        return []


def fetch_searxng_data():
    queries = ["trending products 2026", "viral marketing campaigns"]
    results = []

    try:
        base_url = SEARXNG_URL.rstrip("/") + "/search"

        for query in queries:
            response = requests.get(base_url, params={"q": query, "format": "json"}, timeout=15)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict):
                continue

            hits = data.get("results", [])
            if not isinstance(hits, list):
                continue

            for item in hits[:10]:
                if isinstance(item, dict):
                    title = item.get("title", "")
                    content = item.get("content", "")
                    url = item.get("url", "")
                    text = f"{title} {content} {url}".strip()
                elif isinstance(item, str):
                    text = item
                else:
                    continue

                if not text:
                    continue

                standardized = build_item(text, "searxng", ["searxng"])
                if standardized:
                    results.append(standardized)

        print(f"SearXNG: {len(results)}")
        return results

    except Exception as exc:
        print("SearXNG Error:", exc)
        return []


def log_top_items(items, limit=5):
    print("Top 5 highest opportunity items:")
    for index, item in enumerate(items[:limit], start=1):
        preview = item.get("text", "")[:120]
        print(f"{index}. [{item.get('opportunity_score', 0)}] {item.get('source', 'unknown')}: {preview}")


def run():
    print("Collecting Multi-Source Data...\n")

    try:
        hn_data = fetch_hn()

        reddit_data = normalize_source_records(fetch_reddit(), "reddit")
        print(f"Reddit: {len(reddit_data)}")

        firecrawl_data = fetch_firecrawl()
        telegram_data = fetch_telegram_data()
        search_data = fetch_searxng_data()

        combined = hn_data + reddit_data + firecrawl_data + telegram_data + search_data
        print(f"\nTotal Combined Data: {len(combined)}")

        scored_items = []
        for item in combined:
            try:
                scored_items.append(score_item(item))
            except Exception as exc:
                print(f"Research Item Error: {exc}")

        high_value_items = sort_by_opportunity(filter_high_value_items(scored_items))

        save_json(scored_items, RAW_OUTPUT_PATH)
        save_json(high_value_items, HIGH_VALUE_OUTPUT_PATH)

        print(f"Total items collected: {len(scored_items)}")
        print(f"Total high-value items: {len(high_value_items)}")
        log_top_items(high_value_items)

        return high_value_items

    except Exception as exc:
        print("Research Agent Error:", exc)
        return []
