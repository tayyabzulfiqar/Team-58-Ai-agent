import requests

SERPER_API_KEY = "d19745e642d83ff377b1f3647b958824d055b59b"
SERPER_API_URL = "https://google.serper.dev/search"
INVALID_SUFFIXES = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".zip",
)
BLOCKED_DOMAINS = (
    "youtube.com",
    "youtu.be",
    "reddit.com",
)


def search_serper(query):
    print(f"🔎 Searching Serper for: {query}")
    payload = {
        "q": query,
        "num": 10,
    }
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(SERPER_API_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print(f"❌ Search failed for '{query}': {error}")
        return []

    results = data.get("organic", [])
    urls = []
    seen = set()

    for result in results:
        url = (result.get("url") or result.get("link") or "").strip()
        if not url.startswith("http"):
            continue
        if url.lower().endswith(INVALID_SUFFIXES):
            continue
        if any(domain in url.lower() for domain in BLOCKED_DOMAINS):
            continue
        if url in seen:
            continue

        seen.add(url)
        urls.append(url)

        if len(urls) == 10:
            break

    print(f"✅ SEARCH RESULTS ({len(urls)}): {urls}")
    return urls


def get_urls(query):
    return search_serper(query)
