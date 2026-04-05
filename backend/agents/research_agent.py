from backend.tools.extractor_tool import extractor_tool
from backend.tools.query_rewriter import rewrite_query
from backend.tools.reddit_tool import reddit_tool
from backend.tools.scraper_tool import scraper_tool
from backend.tools.search_tool import search_tool


class ResearchAgent:
    def run(self, input_data):
        query = str(input_data)
        search_results = search_tool(query)
        human_query = rewrite_query(query)
        reddit_results = reddit_tool(human_query)

        enriched = []

        for r in search_results.get("results", []):
            try:
                raw = scraper_tool(r["link"])
                content = extractor_tool(raw)
            except Exception:
                content = ""

            enriched.append({
                "title": r["title"],
                "snippet": r["snippet"],
                "content": content
            })

        return {
            "query": query,
            "data": enriched,
            "reddit": reddit_results.get("reddit_data", [])
        }
