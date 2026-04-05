import json


def enforce_policy(original_input, chosen_strategy):
    t = str(original_input).lower()

    brand_signals = [
        "new market",
        "launch",
        "startup",
        "new product",
        "early stage",
        "brand awareness",
        "visibility"
    ]

    for signal in brand_signals:
        if signal in t:
            return "Brand awareness"

    return chosen_strategy


def generate_reason(data, strategy):
    analysis = data.get("analysis", {})
    text = str(analysis).lower()

    if strategy == "Performance marketing":
        if "conversion" in text or "funnel" in text:
            return "Focus is on conversions and measurable ROI"
        return "Best for driving immediate results"

    if strategy == "Emotional marketing":
        if "story" in text or "emotion" in text:
            return "Relies on emotional engagement and storytelling"
        return "Best for building trust and connection"

    if strategy == "Brand awareness":
        if "launch" in text or "startup" in text:
            return "Suitable for new brand or market entry"
        return "Best for long-term visibility and growth"

    return "Decision based on market signals"


def calculate_confidence(data, strategy):
    analysis = str(data.get("analysis", "")).lower()
    score = 50

    if strategy == "Performance marketing":
        if "conversion" in analysis or "roi" in analysis:
            score += 20

    if strategy == "Emotional marketing":
        if "emotion" in analysis or "story" in analysis:
            score += 20

    if strategy == "Brand awareness":
        if "launch" in analysis or "startup" in analysis:
            score += 20

    if len(analysis) > 300:
        score += 10

    return min(score, 95)


def generate_alternatives(best_strategy):
    strategies = [
        "Performance marketing",
        "Emotional marketing",
        "Brand awareness"
    ]
    return [s for s in strategies if s != best_strategy]


def learning_bonus(strategy):
    try:
        with open("backend/memory/data.json") as f:
            data = json.load(f)

        count = sum(
            1 for d in data
            if isinstance(d, dict) and d.get("strategy") == strategy
        )
        return min(count, 10)
    except Exception:
        return 0


def decision_tool(data, original_input=""):
    objective = data.get("objective", "mixed")

    if objective == "conversion":
        best_strategy = "Performance marketing"
        confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)
        return {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": "Objective is conversion-focused",
            "confidence": confidence,
            "status": "decided"
        }

    if objective == "emotional":
        best_strategy = "Emotional marketing"
        confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)
        return {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": "Objective is emotional engagement",
            "confidence": confidence,
            "status": "decided"
        }

    if objective == "awareness":
        best_strategy = "Brand awareness"
        confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)
        return {
            "selected_strategy": best_strategy,
            "alternatives": generate_alternatives(best_strategy),
            "reason": "Objective is long-term visibility",
            "confidence": confidence,
            "status": "decided"
        }

    best_strategy = data["analysis"]["best_strategy"]
    best_strategy = enforce_policy(original_input, best_strategy)
    reason = generate_reason(data, best_strategy)
    confidence = min(calculate_confidence(data, best_strategy) + learning_bonus(best_strategy), 95)

    return {
        "selected_strategy": best_strategy,
        "alternatives": generate_alternatives(best_strategy),
        "reason": reason if reason else "Decision based on market analysis",
        "confidence": confidence,
        "status": "decided"
    }
