import requests
import json
from datetime import datetime

SEARXNG_URL = "https://searx.be/search"
QUERY = "AI business ideas OR startup trends OR SaaS opportunities"


def fetch_search_results():
    print("Fetching SearXNG data...")

    try:
        params = {
            "q": QUERY,
            "format": "json"
        }

        response = requests.get(SEARXNG_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            print("SearXNG returned non-dict response")
            return []

        results = data.get("results", [])
        if not isinstance(results, list):
            print("SearXNG results not a list")
            return []

        output = []

        for item in results[:10]:
            if isinstance(item, dict):
                title = item.get("title", "")
                url = item.get("url", "")
                content = item.get("content", "")
                text = f"{title} - {content}".strip() if content else title
            elif isinstance(item, str):
                text = item
            else:
                continue

            if text:
                output.append({
                    "text": text,
                    "source": "searxng",
                    "collected_at": str(datetime.now()),
                    "trust_score": None,
                    "status": "raw",
                    "tags": ["search"],
                    "processed": False
                })

        print(f"SearXNG fetched {len(output)} results")
        return output

    except requests.exceptions.RequestException as e:
        print("SearXNG network error:", e)
        return []
    except json.JSONDecodeError as e:
        print("SearXNG JSON decode error:", e)
        return []
    except Exception as e:
        print("SearXNG unexpected error:", e)
        return []