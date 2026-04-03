
# SYSTEM GUARD: SSOT - raw_data.json is READ ONLY
import json
import os

from utils.llm import llm_call
DEBUG_MODE = True

INPUT_PATH = os.path.abspath("backend/data/processed/strategy.json")
OUTPUT_PATH = os.path.abspath("backend/data/processed/decisions.json")


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
    try:
        response = llm_call(prompt)
        data = json.loads(response)
        data["pattern"] = strategy.get("pattern")
        return data
    except Exception as e:
        return fallback_decision(strategy)


def run():
    try:
        strategies = load_strategies()
    except Exception as e:
        print(f"ERROR loading strategies: {e}")
        strategies = []
    decisions = []

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    for s in strategies:
        decision = None
        try:
            decision = call_ai_api(s)
        except Exception as e:
            print(f"ERROR in call_ai_api: {e}")
            decision = fallback_decision(s)
        decisions.append(decision)
        if DEBUG_MODE:
            print(f"DEBUG Decision for pattern: {s.get('pattern')} -> {decision.get('decision')}")

    # STEP 2 — ADD FALLBACK DECISION (CRITICAL)
    if not decisions:
        decisions = [{
            "action": "monitor",
            "reason": "No strong signals detected",
            "confidence": 0.1,
            "source": "fallback_system"
        }]
        if DEBUG_MODE:
            print("DEBUG: Injected fallback decision due to empty decisions list.")

    # STEP 1 — DEBUG LOGS BEFORE SAVING
    if DEBUG_MODE:
        print("DEBUG decisions:", decisions)
        print("DEBUG count:", len(decisions))

    # STEP 3 — SAFE FILE WRITE
    try:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(decisions, f, indent=2)
        if DEBUG_MODE:
            print("Decisions saved:", OUTPUT_PATH)
            print(f"Total decisions: {len(decisions)}")
    except Exception as e:
        print(f"ERROR saving decisions: {e}")


if __name__ == "__main__":
    run()