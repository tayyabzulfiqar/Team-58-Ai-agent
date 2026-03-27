import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")

INPUT_PATH = "data/processed/strategy.json"
OUTPUT_PATH = "data/processed/decisions.json"


def load_strategies():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def call_ai(strategy):
    url = f"{BASE_URL}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a ruthless business investor.

Analyze this opportunity:

Pattern: {strategy.get("pattern")}
Target: {strategy.get("target_audience")}
Pain: {strategy.get("pain_point")}
Solution: {strategy.get("solution")}
Idea: {strategy.get("business_idea")}

Return STRICT JSON:
{{
"decision": "BUILD or TEST or IGNORE",
"reason": "",
"priority": 1-10
}}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        data = res.json()
        content = data["choices"][0]["message"]["content"]

        return json.loads(content)

    except Exception as e:
        print("Decision AI Error:", e)
        return {
            "decision": "TEST",
            "reason": "fallback",
            "priority": 5
        }


def run():
    strategies = load_strategies()
    decisions = []

    for s in strategies:
        ai_decision = call_ai(s)

        decisions.append({
            "pattern": s.get("pattern"),
            **ai_decision
        })

        print(f"Decision made for: {s.get('pattern')}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

    print("Decision engine complete")


if __name__ == "__main__":
    run()