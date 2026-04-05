import requests


API_KEY = "sk-36f731a2000b49f4b76b2b6bb3b6a1ca"
BASE_URL = "https://ws-7cdqxbw1m3iabksm.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"


def qwen_generate(prompt):
    try:
        url = f"{BASE_URL}/chat/completions"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen-plus",
            "messages": [
                {"role": "system", "content": "You are an AI analyst helping extract insights."},
                {"role": "user", "content": prompt[:2000]}
            ],
            "temperature": 0.7
        }

        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("Qwen error:", e)
        return "AI insight unavailable"
