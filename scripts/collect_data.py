import json
import requests
from datetime import datetime
from pathlib import Path

from reddit_collector import fetch_reddit
from search_agent import fetch_search_results  # NEW (SearXNG)

OUTPUT_PATH = "data/raw/raw_data.json"

# Hacker News
HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_LIMIT = 25


# -----------------------------
# 🔹 Hacker News
# -----------------------------
def fetch_hn():
    print("Fetching Hacker News data...")

    try:
        response = requests.get(HN_TOP_URL, timeout=10)
        response.raise_for_status()

        story_ids = response.json()[:HN_LIMIT]

        results = []
        for sid in story_ids:
            item = requests.get(HN_ITEM_URL.format(sid), timeout=10).json()

            if item and item.get("title"):
                results.append({
                    "text": item["title"],
                    "source": "hackernews",
                    "collected_at": str(datetime.now()),
                    "trust_score": None,
                    "status": "raw",
                    "tags": ["hn"],
                    "processed": False
                })

        print(f"HN: {len(results)}")
        return results

    except Exception as e:
        print("HN Error:", e)
        return []


# -----------------------------
# 🔹 Firecrawl Loader
# -----------------------------
def load_firecrawl():
    path = Path("data/raw/firecrawl_data.json")

    if not path.exists():
        print("Firecrawl file not found, creating empty")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        output = []

        for item in data:
            if isinstance(item, dict):
                text = item.get("text") or item.get("title")
            elif isinstance(item, str):
                text = item
            else:
                text = None

            if text:
                output.append({
                    "text": text,
                    "source": "firecrawl",
                    "collected_at": str(datetime.now()),
                    "trust_score": None,
                    "status": "raw",
                    "tags": ["firecrawl"],
                    "processed": False
                })

        print(f"Firecrawl: {len(output)}")
        return output

    except Exception as e:
        print("Firecrawl Error:", e)
        return []


# -----------------------------
# 🔹 Save
# -----------------------------
def save_data(data):
    path = Path(OUTPUT_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Combined data saved")


# -----------------------------
# 🔹 MAIN RUN
# -----------------------------
def run():
    print("Collecting Multi-Source Data...\n")

    # 1️⃣ Hacker News
    hn_data = fetch_hn()

    # 2️⃣ Reddit
    reddit_data = fetch_reddit()
    print(f"Reddit: {len(reddit_data)}")

    # 3️⃣ Firecrawl
    firecrawl_data = load_firecrawl()

    # 4️⃣ SearXNG (NEW 🔥)
    search_data = fetch_search_results()
    print(f"SearXNG: {len(search_data)}")

    # 🔥 COMBINE ALL
    combined = hn_data + reddit_data + firecrawl_data + search_data

    print(f"\nTotal Combined Data: {len(combined)}")

    save_data(combined)


if __name__ == "__main__":
    run()