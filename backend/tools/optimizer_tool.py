def optimizer_tool(campaigns):
    best = None
    best_score = -1

    for c in campaigns:
        score = len(c.get("headline", "")) + len(c.get("hook", ""))

        if score > best_score:
            best_score = score
            best = c

    return {
        "best_campaign": best,
        "optimization_score": best_score
    }
