def strong_awareness_signal(text):
    t = str(text).lower()

    strong_patterns = [
        "new startup",
        "launch campaign",
        "brand awareness campaign",
        "enter new market",
        "new product launch"
    ]

    return any(p in t for p in strong_patterns)


def detect_objective(text):
    t = str(text).lower()

    conversion_keywords = [
        "lead", "conversion", "funnel", "roi",
        "sales", "performance", "optimize", "cpa"
    ]

    emotional_keywords = [
        "emotion", "story", "trust", "engagement",
        "connection", "resonate", "loyalty"
    ]

    awareness_keywords = [
        "brand awareness",
        "brand launch",
        "new launch",
        "product launch",
        "new startup",
        "early stage startup",
        "market entry",
        "go to market",
        "gtm",
        "visibility campaign"
    ]

    conversion_score = sum(1 for k in conversion_keywords if k in t)
    emotional_score = sum(1 for k in emotional_keywords if k in t)
    awareness_score = sum(1 for k in awareness_keywords if k in t)

    scores = {
        "conversion": conversion_score,
        "emotional": emotional_score,
        "awareness": awareness_score
    }

    if strong_awareness_signal(text):
        return "awareness"

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "mixed"

    return best
