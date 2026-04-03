import requests
from bs4 import BeautifulSoup

FIRECRAWL_API_KEY = "fc-8aa09a49b43248aab44dc22fc3d2b2e3"
FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1/scrape"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


def scrape_url(url):
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "formats": ["markdown"],
    }

    try:
        response = requests.post(FIRECRAWL_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print(f"❌ Firecrawl scrape failed for {url}: {error}")
        return {}

    content = ""
    firecrawl_data = data.get("data")
    if isinstance(firecrawl_data, dict):
        content = firecrawl_data.get("markdown") or firecrawl_data.get("content") or firecrawl_data.get("text") or ""
    elif isinstance(firecrawl_data, str):
        content = firecrawl_data

    content = " ".join(content.split())
    if len(content) <= 200:
        return {}

    return {
        "url": url,
        "content": content[:2000],
    }


def _extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img"]):
        tag.decompose()

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join(part for part in paragraphs if part)

    if len(text) < 200:
        article = soup.find("article")
        if article:
            text = article.get_text(" ", strip=True)

    if len(text) < 200 and soup.body:
        text = soup.body.get_text(" ", strip=True)

    return " ".join(text.split())


def scrape_urls(urls):
    data = []

    for url in urls:
        try:
            print(f"🌐 Fetching: {url}")
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)

            if response.status_code != 200:
                print(f"❌ Failed ({response.status_code}): {url}")
                fallback = scrape_url(url)
                if fallback.get("content"):
                    data.append(fallback)
                    print(f"✅ Scraped via Firecrawl fallback: {url}")
                continue

            text = _extract_text_from_html(response.text)

            if len(text) > 200:
                data.append({
                    "url": url,
                    "content": text[:2000],
                })
                print(f"✅ Scraped: {url}")
                continue

            print(f"⚠️ Thin content from page HTML, trying Firecrawl: {url}")
            fallback = scrape_url(url)
            if fallback.get("content"):
                data.append(fallback)
                print(f"✅ Scraped via Firecrawl fallback: {url}")
            else:
                print(f"❌ No usable content: {url}")

        except Exception as error:
            print(f"❌ Error scraping {url}: {error}")
            try:
                fallback = scrape_url(url)
                if fallback.get("content"):
                    data.append(fallback)
                    print(f"✅ Scraped via Firecrawl fallback after error: {url}")
            except Exception as fallback_error:
                print(f"❌ Firecrawl fallback failed for {url}: {fallback_error}")

    print(f"📦 SCRAPED DATA COUNT: {len(data)}")
    return data


def scrape_multiple(urls):
    return scrape_urls(urls)
