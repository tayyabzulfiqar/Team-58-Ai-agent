import requests

API_KEY = "fc-8bde7b59ae604f6089287919ff7089c3"

url = "https://api.firecrawl.dev/v1/scrape"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "url": "https://example.com",
    "formats": ["markdown"]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
except Exception as e:
    print("ERROR:", str(e))
