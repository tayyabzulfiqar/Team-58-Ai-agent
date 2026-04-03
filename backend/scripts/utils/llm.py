import requests
import time
import os

API_KEY = os.getenv("QWEN_API_KEY", "")
BASE_URL = os.getenv("QWEN_BASE_URL", "https://ws-7cdqxbw1m3iabksm.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1")

def llm_call(prompt):
    print("[QWEN REQUEST]")
    time.sleep(1)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            output = response.json()["choices"][0]["message"]["content"]
            if not output or len(output.strip()) == 0:
                return "AI unavailable — fallback insight generated"
            print("[QWEN RESPONSE OK]")
            return output
        else:
            print(f"[QWEN ERROR] {response.status_code}")
            return "AI unavailable — fallback insight generated"
    except Exception as e:
        print(f"[QWEN EXCEPTION] {str(e)}")
        return "AI unavailable — fallback insight generated"
