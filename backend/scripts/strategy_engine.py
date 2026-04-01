import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

INPUT_PATH = "data/processed/patterns.json"
OUTPUT_PATH = "data/processed/strategy.json"

API_KEY = os.getenv("API_KEY", "").strip()
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
API_URL = f"{BASE_URL}/v1/chat/completions" if BASE_URL else "https://api.openai.com/v1/chat/completions"


def load_patterns():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fallback_strategy(pattern, frequency):
    return {
        "pattern": pattern,
        "target_audience": "General market",
        "pain_point": "Identify and align product to current demand",
        "solution": f"Explore the {pattern} trend and develop a focused MVP",
        "business_idea": f"Launch a pilot offering for {pattern} related users",
        "marketing_hook": f"Solve urgent {pattern} market needs with a high-value product"
    }


def parse_ai_response(text):
    try:
        data = json.loads(text)
        keys = ["target_audience", "pain_point", "solution", "business_idea", "marketing_hook"]
        if isinstance(data, dict) and all(key in data for key in keys):
            return {
                key: str(data[key]).strip() for key in keys
            }
    except json.JSONDecodeError:
        pass

    return None


def call_ai_api(pattern, frequency, retries=1, timeout=5):
    if not API_KEY or not BASE_URL:
        raise ValueError("API_KEY or BASE_URL not set")

    # quick timeout safeguard: ensure API is reachable first
    try:
        ping = requests.get(BASE_URL, timeout=2)
        if ping.status_code >= 400:
            raise RuntimeError("API endpoint unreachable")
    except Exception:
        raise RuntimeError("API endpoint unreachable")

    prompt = (
        f"Generate business strategy from this pattern: {pattern}. "
        f"Only return a strict JSON object with these fields: target_audience, pain_point, solution, business_idea, marketing_hook. "
        f"Do not include markdown or extra text."
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a business strategy generation engine."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()

            parsed = parse_ai_response(content)
            if parsed is not None:
                parsed["pattern"] = pattern
                return parsed

            # If parsing fails, attempt to clean and parse again with manual object extraction
            cleaned = content
            if cleaned.startswith("`"):
                cleaned = cleaned.strip("`\n ")

            parsed = parse_ai_response(cleaned)
            if parsed is not None:
                parsed["pattern"] = pattern
                return parsed

            # if not parseable, use fallback with plain text in solution
            return {
                "pattern": pattern,
                "target_audience": "General market",
                "pain_point": "N/A",
                "solution": content,
                "business_idea": "N/A",
                "marketing_hook": "N/A"
            }

        except Exception as exc:
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)

    raise RuntimeError("AI API failed after retries")


def run():
    patterns = load_patterns()
    strategies = []

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Limit to top 5 patterns to avoid hanging
    patterns = patterns[:5] if len(patterns) > 5 else patterns

    # Try reachability check once
    use_ai = False
    try:
        ping = requests.get(BASE_URL, timeout=2)
        use_ai = ping.status_code < 400
    except Exception:
        use_ai = False

    for p in patterns:
        pattern = p.get("pattern") or ""
        freq = int(p.get("frequency", 0))

        if use_ai:
            try:
                strategy = call_ai_api(pattern, freq)
            except Exception:
                strategy = fallback_strategy(pattern, freq)
        else:
            strategy = fallback_strategy(pattern, freq)

        strategies.append(strategy)

    print(f"Generated {len(strategies)} strategies")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(strategies, f, indent=2)

    print("Strategy output saved to", OUTPUT_PATH)


if __name__ == "__main__":
    run()