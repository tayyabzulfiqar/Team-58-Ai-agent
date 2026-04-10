from typing import Any


def extract_query_text(input_data: Any) -> str:
    if isinstance(input_data, dict):
        for key in ("query", "input", "prompt", "topic"):
            value = input_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    if isinstance(input_data, str) and input_data.strip():
        return input_data.strip()

    raise ValueError("A non-empty query string is required.")


def detect_budget_tier(query: str) -> str:
    text = query.lower()

    low_signals = ("low budget", "small budget", "limited budget", "bootstrapped")
    high_signals = ("high budget", "large budget", "enterprise budget", "premium launch")

    if any(signal in text for signal in high_signals):
        return "high"

    if any(signal in text for signal in low_signals):
        return "low"

    return "medium"
