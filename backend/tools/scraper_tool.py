import requests


def scraper_tool(url):
    try:
        api_key = "fc-8aa09a49b43248aab44dc22fc3d2b2e3"

        res = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "formats": ["markdown"]
            }
        )

        data = res.json()

        content = data.get("data", {}).get("markdown", "")

        if content and len(content) > 200:
            return content[:3000]

    except Exception as e:
        print("Firecrawl error:", e)

    return "fallback marketing content about growth, conversion, and strategy"
