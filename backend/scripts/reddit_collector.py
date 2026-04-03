import requests
import json
from datetime import datetime
from pathlib import Path

URL = "https://www.reddit.com/r/technology/top.json?limit=25"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

OUTPUT_PATH = "data/raw/raw_data.json"

def fetch_reddit():
    print("Fetching Reddit data (JSON)...")

    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print("Failed to fetch Reddit:", response.status_code)
            return []

        data_json = response.json()

        posts = data_json.get("data", {}).get("children", [])

        data = []

        for post in posts:
            title = post.get("data", {}).get("title")

            if title:
                data.append({
                    "text": title,
                    "source": "reddit",
                    "collected_at": str(datetime.now()),
                    "trust_score": None,
                    "status": "raw",
                    "tags": [],
                    "processed": False
                })

        print(f"Reddit posts collected: {len(data)}")
        return data

    except Exception as e:
        print("Error:", e)
        return []

def save_data(data):
    path = Path(OUTPUT_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    pass

if __name__ == "__main__":
    data = fetch_reddit()
    print("Reddit data fetched (file writing disabled by pipeline policy)")