from backend.tools.decision_tool import decision_tool
from backend.tools.optimizer_tool import optimizer_tool


class CampaignAgent:
    def run(self, input_data):
        decision = decision_tool(
            input_data,
            original_input=input_data.get("original_input", "")
            if isinstance(input_data, dict)
            else ""
        )
        selected_strategy = decision.get("selected_strategy")
        strategies = [
            "Emotional marketing",
            "Performance marketing",
            "Brand awareness"
        ]

        campaigns = []

        for s in strategies:
            campaigns.append({
                "strategy": s,
                "headline": f"{s} campaign for growth",
                "hook": f"{s} high-conversion trigger",
                "cta": "Act now to maximize results"
            })

        filtered = [c for c in campaigns if c["strategy"] == selected_strategy]

        if filtered:
            best = filtered[0]
            score = len(best["headline"]) + len(best["hook"])
        else:
            optimized = optimizer_tool(campaigns)
            best = optimized["best_campaign"]
            score = optimized["optimization_score"]

        return {
            "best_campaign": best,
            "all_campaigns": campaigns,
            "optimization_score": score,
            "decision_meta": decision
        }
