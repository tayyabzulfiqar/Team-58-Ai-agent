import requests


def reddit_tool(query):
    try:
        url = f"https://www.reddit.com/search.json?q={query}&limit=5"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()

        posts = []

        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            title = (p.get("title") or "").strip()
            text = (p.get("selftext") or "").strip()
            if not title and not text:
                continue
            permalink = p.get("permalink") or ""
            posts.append(
                {
                    "title": title,
                    "text": text,
                    "url": f"https://www.reddit.com{permalink}" if permalink else "",
                    "subreddit": p.get("subreddit", ""),
                    "score": p.get("score", 0),
                }
            )

        return {"reddit_data": posts}

    except Exception:
        return {"reddit_data": []}
