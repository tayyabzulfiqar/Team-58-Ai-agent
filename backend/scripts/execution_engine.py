import json
import os
import requests
from dotenv import load_dotenv

# === GLOBAL DEBUG MODE ===
DEBUG_MODE = True

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")

INPUT_PATH = "data/processed/decisions.json"
OUTPUT_PATH = "data/processed/execution.json"


def load_decisions():
    if not os.path.exists(INPUT_PATH):
        print("No decisions file found → skipping execution safely")
        return []
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading decisions.json: {e}")
            return []
    if not data:
        print("Empty decisions → skipping execution safely")
        return []
    return data


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
    try:
        decisions = load_decisions()
        executions = []
        if DEBUG_MODE:
            print(f"DEBUG: Loaded {len(decisions)} decisions.")
        if not decisions:
            print("No valid decisions to execute. Skipping execution step.")
            return "skipped"
        for d in decisions:
            if d.get("decision", d.get("action")) != "BUILD":
                continue
            try:
                ai_output = call_ai(d)
            except Exception as e:
                print(f"ERROR in call_ai: {e}")
                ai_output = {"error": str(e)}
            executions.append({
                "pattern": d.get("pattern", "unknown"),
                **ai_output
            })
            if DEBUG_MODE:
                print(f"Execution plan created for: {d.get('pattern', 'unknown')}")
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(executions, f, indent=2)
        print("Execution engine complete")
        return "success"
    except Exception as e:
        print(f"ERROR in execution engine: {e}")
        return "fallback"


if __name__ == "__main__":
    run()