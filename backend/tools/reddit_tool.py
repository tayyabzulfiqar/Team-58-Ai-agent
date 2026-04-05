import requests


def reddit_tool(query):
    try:
        url = f"https://www.reddit.com/search.json?q={query}&limit=5"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers)
        data = res.json()

        posts = []

        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            posts.append({
                "title": p.get("title", ""),
                "text": p.get("selftext", "")
            })

        return {"reddit_data": posts}

    except Exception:
        return {"reddit_data": []}
