from core.input_utils import extract_query_text
from core.logging_utils import get_logger
from memory.store import get_cached_research
from memory.store import store_cached_research
from tools.extractor_tool import extractor_tool
from tools.query_rewriter import rewrite_query
from tools.reddit_tool import reddit_tool
from tools.scraper_tool import scraper_tool
from tools.search_tool import search_tool


logger = get_logger("team58.research")


SOURCE_TYPE_TARGET = {
    "blog": "blog",
    "news": "news",
    "case_study": "case_study",
    "forum": "forum",
    "reddit": "reddit",
}


def _normalize_text(value):
    return " ".join(str(value or "").split()).strip()


def _classify_source_type(url: str, title: str, snippet: str, planned_type: str) -> str:
    haystack = f"{url} {title} {snippet}".lower()

    if "reddit.com" in haystack:
        return "reddit"
    if any(token in haystack for token in ("forum", "community", "quora.com", "discuss")):
        return "forum"
    if any(token in haystack for token in ("case study", "customer story", "success story")):
        return "case_study"
    if any(token in haystack for token in ("news", "/news/", "press release", "latest")):
        return "news"

    return SOURCE_TYPE_TARGET.get(planned_type, "blog")


def _make_source_item(search_query, result, scraped, source_type: str) -> dict:
    content = extractor_tool(scraped.get("content", ""))
    return {
        "query": search_query,
        "url": result.get("link", "").strip(),
        "source": result.get("link", "").strip(),
        "type": source_type,
        "domain": result.get("domain"),
        "title": _normalize_text(result.get("title")),
        "snippet": _normalize_text(result.get("snippet")),
        "metadata": scraped.get("metadata", {}),
        "content": _normalize_text(content),
    }


def _make_search_evidence_item(search_query, result, source_type: str) -> dict:
    title = _normalize_text(result.get("title"))
    snippet = _normalize_text(result.get("snippet"))
    content = _normalize_text(f"{title} {snippet}")
    return {
        "query": search_query,
        "url": result.get("link", "").strip(),
        "source": result.get("link", "").strip(),
        "type": source_type,
        "domain": result.get("domain"),
        "title": title,
        "snippet": snippet,
        "metadata": {"snippet_only": True},
        "content": content[:2000],
    }


def _distribution(items):
    counts = {}
    for item in items:
        source_type = item.get("type")
        if not source_type:
            continue
        counts[source_type] = counts.get(source_type, 0) + 1
    return counts


def _cache_is_usable(payload) -> bool:
    if not isinstance(payload, dict):
        return False
    sources = payload.get("sources", [])
    if len(sources) < 10:
        return False
    if len(_distribution(sources)) < 3:
        return False
    return True


class ResearchAgent:
    def run(self, input_data):
        query = extract_query_text(input_data)
        logger.info("research:start query=%s", query)

        cached = get_cached_research(query)
        if cached and _cache_is_usable(cached):
            logger.info("research:cache-hit query=%s", query)
            return cached

        search_queries = rewrite_query(query)
        seen_urls = set()
        collected_sources = []
        all_results = []

        for plan in search_queries:
            search_query = plan["query"]
            try:
                search_results = search_tool(search_query, limit=plan.get("limit", 4))
            except Exception as exc:
                logger.warning("research:search-failed query=%s error=%s", search_query, exc)
                continue

            for result in search_results.get("results", []):
                url = result["link"].strip()
                if url in seen_urls:
                    continue

                all_results.append(result)
                try:
                    scraped = scraper_tool(url)
                    source_type = _classify_source_type(
                        url,
                        result.get("title"),
                        result.get("snippet"),
                        plan.get("source_type", "blog"),
                    )
                    source_item = _make_source_item(search_query, result, scraped, source_type)
                    if not source_item["content"]:
                        continue
                    seen_urls.add(url)
                    collected_sources.append(source_item)
                except Exception as exc:
                    logger.warning("research:scrape-failed url=%s error=%s", url, exc)
                    source_type = _classify_source_type(
                        url,
                        result.get("title"),
                        result.get("snippet"),
                        plan.get("source_type", "blog"),
                    )
                    fallback_item = _make_search_evidence_item(search_query, result, source_type)
                    if fallback_item["content"]:
                        seen_urls.add(url)
                        collected_sources.append(fallback_item)
                    continue

        reddit_results = reddit_tool(query)
        for post in reddit_results.get("reddit_data", []):
            title = _normalize_text(post.get("title"))
            text = _normalize_text(post.get("text"))
            content = _normalize_text(f"{title} {text}")
            if not content:
                continue
            source = post.get("url") or f"reddit:{title.lower()}"
            if source in seen_urls:
                continue
            seen_urls.add(source)
            collected_sources.append(
                {
                    "query": search_queries[-1]["query"] if search_queries else query,
                    "url": source,
                    "source": source,
                    "type": "reddit",
                    "domain": "reddit.com",
                    "title": title,
                    "snippet": text[:500],
                    "metadata": {"subreddit": post.get("subreddit"), "score": post.get("score")},
                    "content": content[:4000],
                }
            )

        if len(_distribution(collected_sources)) < 3:
            missing_type_plans = [
                plan
                for plan in search_queries
                if _distribution(collected_sources).get(SOURCE_TYPE_TARGET.get(plan["source_type"], plan["source_type"]), 0) == 0
            ]
            for plan in missing_type_plans:
                try:
                    search_results = search_tool(plan["query"], limit=5)
                except Exception as exc:
                    logger.warning("research:rebalance-search-failed query=%s error=%s", plan["query"], exc)
                    continue

                for result in search_results.get("results", []):
                    url = result["link"].strip()
                    if url in seen_urls:
                        continue
                    try:
                        scraped = scraper_tool(url)
                        source_type = _classify_source_type(
                            url,
                            result.get("title"),
                            result.get("snippet"),
                            plan.get("source_type", "blog"),
                        )
                        source_item = _make_source_item(plan["query"], result, scraped, source_type)
                        if not source_item["content"]:
                            continue
                        seen_urls.add(url)
                        collected_sources.append(source_item)
                    except Exception as exc:
                        logger.warning("research:rebalance-scrape-failed url=%s error=%s", url, exc)
                        source_type = _classify_source_type(
                            url,
                            result.get("title"),
                            result.get("snippet"),
                            plan.get("source_type", "blog"),
                        )
                        fallback_item = _make_search_evidence_item(plan["query"], result, source_type)
                        if fallback_item["content"]:
                            seen_urls.add(url)
                            collected_sources.append(fallback_item)
                        continue

                if len(_distribution(collected_sources)) >= 3:
                    break

        if not collected_sources:
            raise RuntimeError("ResearchAgent collected zero usable sources.")

        payload = {
            "query": query,
            "queries": search_queries,
            "search_results": all_results,
            "sources": collected_sources,
            "reddit": reddit_results.get("reddit_data", []),
        }
        store_cached_research(query, payload)
        logger.info(
            "research:done queries=%s sources=%s distribution=%s",
            len(search_queries),
            len(collected_sources),
            _distribution(collected_sources),
        )
        return payload
