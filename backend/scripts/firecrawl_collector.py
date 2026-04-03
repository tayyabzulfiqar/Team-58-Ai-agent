import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = "fc-8aa09a49b43248aab44dc22fc3d2b2e3"

OUTPUT_PATH = "data/raw/firecrawl_data.json"


def fetch_firecrawl_data():
    url = "https://api.firecrawl.dev/v1/scrape"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "url": "https://news.ycombinator.com/",
        "formats": ["markdown"]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None


def run():
    data = fetch_firecrawl_data()

    if not data:
        return

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Firecrawl data saved")


if __name__ == "__main__":
    run()