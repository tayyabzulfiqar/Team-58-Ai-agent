from core.logging_utils import get_logger


logger = get_logger("team58.cleaner")


def _trim_text(value: str, limit: int = 4000) -> str:
    text = " ".join(value.split())
    return text[:limit].strip()


def cleaner_tool(data):
    logger.info("cleaner:start")
    sources = data.get("sources", []) if isinstance(data, dict) else []
    cleaned_sources = []
    seen_urls = set()
    seen_content = set()

    for source in sources:
        url = (source.get("url") or "").strip()
        content = _trim_text(source.get("content", ""))
        title = _trim_text(source.get("title", ""), limit=300)
        snippet = _trim_text(source.get("snippet", ""), limit=500)

        if not url or not content:
            continue

        fingerprint = (title.lower(), content[:500].lower())
        if url in seen_urls or fingerprint in seen_content:
            continue

        seen_urls.add(url)
        seen_content.add(fingerprint)

        cleaned_sources.append(
            {
                **source,
                "url": url,
                "title": title,
                "snippet": snippet,
                "content": content,
            }
        )

    if not cleaned_sources:
        raise RuntimeError("Cleaner removed all sources; no usable research data remains.")

    result = {**data, "sources": cleaned_sources}
    logger.info("cleaner:done kept=%s", len(cleaned_sources))
    return result
