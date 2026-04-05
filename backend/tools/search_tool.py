import requests


def search_tool(query):
    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": "d19745e642d83ff377b1f3647b958824d055b59b",
            "Content-Type": "application/json"
        }

        res = requests.post(url, json={"q": query}, headers=headers)
        data = res.json()

        results = []

        for item in data.get("organic", [])[:5]:
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            })

        if results:
            return {"results": results}

    except Exception as e:
        print("Serper error:", e)

    return {
        "results": [
            {"title": f"{query} strategy", "snippet": "marketing growth tactics", "link": "fallback"}
        ]
    }
