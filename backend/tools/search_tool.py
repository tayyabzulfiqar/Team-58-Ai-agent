import os
from urllib.parse import urlparse

import requests

from core.logging_utils import get_logger


logger = get_logger("team58.search")
SERPER_URL = "https://google.serper.dev/search"
SERPER_API_KEY = os.getenv("SERPER_API_KEY") or "d19745e642d83ff377b1f3647b958824d055b59b"


def search_tool(query: str, limit: int = 5) -> dict:
    if not SERPER_API_KEY:
        raise RuntimeError("SERPER_API_KEY is not configured.")

    logger.info("search:start query=%s limit=%s", query, limit)
    response = requests.post(
        SERPER_URL,
        json={"q": query, "num": max(1, min(limit, 10))},
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    results = []

    for item in data.get("organic", [])[:limit]:
        link = item.get("link")
        title = item.get("title")
        snippet = item.get("snippet")

        if not link or not title:
            continue

        results.append(
            {
                "title": title.strip(),
                "snippet": (snippet or "").strip(),
                "link": link.strip(),
                "domain": urlparse(link).netloc,
                "position": item.get("position"),
            }
        )

    if not results:
        raise RuntimeError(f"Serper returned no organic results for query: {query}")

    logger.info("search:done query=%s results=%s", query, len(results))
    return {"query": query, "results": results}
