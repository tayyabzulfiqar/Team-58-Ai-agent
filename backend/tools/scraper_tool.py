import os
import re

import requests

from core.logging_utils import get_logger


logger = get_logger("team58.scraper")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY") or "fc-a3cd43f9ccaf4eafb783d87b28168894"
FIRECRAWL_URL = os.getenv("FIRECRAWL_ENDPOINT") or "https://api.firecrawl.dev/v1/scrape"


def _extract_metadata_from_html(html: str) -> dict:
    title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    description_match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return {
        "title": title_match.group(1).strip() if title_match else None,
        "description": description_match.group(1).strip() if description_match else None,
    }


def _strip_html(html: str) -> str:
    without_scripts = re.sub(r"<script.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    without_styles = re.sub(r"<style.*?</style>", " ", without_scripts, flags=re.IGNORECASE | re.DOTALL)
    without_tags = re.sub(r"<[^>]+>", " ", without_styles)
    normalized = re.sub(r"\s+", " ", without_tags)
    return normalized.strip()


def _direct_scrape(url: str) -> dict:
    logger.info("scrape:direct url=%s", url)
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
        },
        timeout=60,
    )
    response.raise_for_status()

    html = response.text
    content = _strip_html(html)
    if len(content) < 200:
        raise RuntimeError(f"Direct scrape content too short for url: {url}")

    metadata = _extract_metadata_from_html(html)
    return {
        "url": url,
        "content": content[:12000],
        "metadata": {
            **metadata,
            "statusCode": response.status_code,
            "contentType": response.headers.get("Content-Type"),
        },
    }


def scraper_tool(url: str) -> dict:
    logger.info("scrape:start url=%s", url)

    if FIRECRAWL_API_KEY:
        try:
            response = requests.post(
                FIRECRAWL_URL,
                headers={
                    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                },
                timeout=60,
            )

            if response.status_code == 402:
                logger.warning("scrape:firecrawl-credit-exhausted url=%s", url)
            else:
                response.raise_for_status()
                payload = response.json()
                data = payload.get("data", {})
                content = (data.get("markdown") or "").strip()

                if len(content) >= 200:
                    result = {
                        "url": url,
                        "content": content[:12000],
                        "metadata": {
                            "title": data.get("metadata", {}).get("title") or data.get("title"),
                            "description": data.get("metadata", {}).get("description"),
                            "language": data.get("metadata", {}).get("language"),
                            "statusCode": data.get("metadata", {}).get("statusCode"),
                        },
                    }
                    logger.info("scrape:done url=%s chars=%s provider=firecrawl", url, len(content))
                    return result
        except Exception as exc:
            logger.warning("scrape:firecrawl-failed url=%s error=%s", url, exc)

    result = _direct_scrape(url)
    logger.info("scrape:done url=%s chars=%s provider=direct", url, len(result["content"]))
    return result
