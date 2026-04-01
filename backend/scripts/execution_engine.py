import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")

INPUT_PATH = "data/processed/decisions.json"
OUTPUT_PATH = "data/processed/execution.json"


def load_decisions():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def call_ai(decision):
    url = f"{BASE_URL}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a world-class startup founder and marketer.

Build a FULL execution plan for this:

Pattern: {decision.get("pattern")}
Decision: {decision.get("decision")}
Priority: {decision.get("priority")}

Only respond in STRICT JSON:

{{
"business_name": "",
"one_liner": "",
"target_audience": "",
"offer": "",
"landing_page_headline": "",
"landing_page_subheadline": "",
"ad_copy": "",
"cold_outreach_message": ""
}}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=25)
        data = res.json()
        content = data["choices"][0]["message"]["content"]

        return json.loads(content)

    except Exception as e:
        print("Execution AI Error:", e)
        return {
            "business_name": "fallback",
            "one_liner": "fallback",
            "target_audience": "fallback",
            "offer": "fallback",
            "landing_page_headline": "fallback",
            "landing_page_subheadline": "fallback",
            "ad_copy": "fallback",
            "cold_outreach_message": "fallback"
        }


def run():
    decisions = load_decisions()
    executions = []

    for d in decisions:
        if d.get("decision") != "BUILD":
            continue

        ai_output = call_ai(d)

        executions.append({
            "pattern": d.get("pattern"),
            **ai_output
        })

        print(f"Execution plan created for: {d.get('pattern')}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(executions, f, indent=2)

    print("Execution engine complete")


if __name__ == "__main__":
    run()