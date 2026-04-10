def rewrite_query(query: str) -> list[dict]:
    base = " ".join((query or "").split()).strip()
    plans = [
        {
            "label": "general",
            "query": base,
            "source_type": "blog",
            "target": "blogs/articles",
            "limit": 4,
        },
        {
            "label": "trend",
            "query": f"{base} industry trends latest",
            "source_type": "news",
            "target": "news/trends",
            "limit": 4,
        },
        {
            "label": "problem",
            "query": f"{base} case study customer pain points",
            "source_type": "case_study",
            "target": "case studies",
            "limit": 4,
        },
        {
            "label": "discussion",
            "query": f"{base} reddit forum discussion",
            "source_type": "forum",
            "target": "reddit/forums",
            "limit": 4,
        },
    ]

    deduped = []
    seen = set()

    for item in plans:
        normalized = item["query"].lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(item)

    return deduped
