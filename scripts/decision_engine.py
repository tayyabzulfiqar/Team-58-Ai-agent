import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("API_KEY", "").strip()
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
API_URL = f"{BASE_URL}/v1/chat/completions" if BASE_URL else "https://api.openai.com/v1/chat/completions"

INPUT_PATH = "data/processed/strategy.json"
OUTPUT_PATH = "data/processed/decisions.json"


def load_strategies():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fallback_decision(strategy):
    return {
        "pattern": strategy.get("pattern"),
        "decision": "MONITOR",
        "reason": "Fallback due to API unavailability",
        "priority": 5
    }


def parse_ai_response(text):
    try:
        data = json.loads(text)
        keys = ["decision", "reason", "priority"]
        if isinstance(data, dict) and all(key in data for key in keys):
            return {
                key: str(data[key]).strip() for key in keys
            }
    except json.JSONDecodeError:
        pass

    return None


def call_ai_api(strategy, retries=2, timeout=10):
    if not API_KEY or not BASE_URL:
        raise ValueError("API_KEY or BASE_URL not set")

    prompt = (
        f"Analyze this business strategy and decide: BUILD, TEST, or IGNORE. "
        f"Pattern: {strategy.get('pattern')}. "
        f"Target Audience: {strategy.get('target_audience')}. "
        f"Pain Point: {strategy.get('pain_point')}. "
        f"Solution: {strategy.get('solution')}. "
        f"Business Idea: {strategy.get('business_idea')}. "
        f"Marketing Hook: {strategy.get('marketing_hook')}. "
        f"Return JSON: {{\"decision\": \"BUILD|TEST|IGNORE\", \"reason\": \"why\", \"priority\": 1-10}}"
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a business decision engine."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()

            parsed = parse_ai_response(content)
            if parsed is not None:
                parsed["pattern"] = strategy.get("pattern")
                return parsed

            # Fallback to plain text parsing
            if "BUILD" in content.upper():
                decision = "BUILD"
            elif "TEST" in content.upper():
                decision = "TEST"
            else:
                decision = "IGNORE"
            return {
                "pattern": strategy.get("pattern"),
                "decision": decision,
                "reason": content,
                "priority": 5
            }

        except Exception as exc:
            if attempt == retries:
                raise
            time.sleep(1)

    raise RuntimeError("AI API failed after retries")


def run():
    strategies = load_strategies()
    decisions = []

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    for s in strategies:
        decision = None
        try:
            decision = call_ai_api(s)
        except Exception:
            decision = fallback_decision(s)

        decisions.append(decision)
        print(f"Decision for pattern: {s.get('pattern')} -> {decision.get('decision')}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

    print("Decisions saved:", OUTPUT_PATH)
    print(f"Total decisions: {len(decisions)}")


if __name__ == "__main__":
    run()