from datetime import datetime, timezone

from core.logging_utils import get_logger
from tools.decision_tool import decision_tool
from tools.execution_tool import execution_tool
from tools.optimizer_tool import optimizer_tool


logger = get_logger("team58.campaign")


class CampaignAgent:
    def run(self, input_data):
        logger.info("campaign:start")
        decision = decision_tool(
            input_data,
            original_input=input_data.get("original_input", "")
            if isinstance(input_data, dict)
            else ""
        )
        execution_plan = execution_tool(
            decision,
            input_data.get("structured_intelligence", {}),
            input_data.get("validation", {}),
            decision.get("decision_inputs", {}).get("budget_tier", "medium"),
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
                "headline": f"{s} plan for {execution_plan.get('priority_opportunity', 'growth execution')}",
                "hook": execution_plan.get("target_audience", "Target the highest-potential audience"),
                "cta": f"Launch on {', '.join(execution_plan.get('platform_selection', [])[:2]) or 'priority channels'}"
            })

        filtered = [c for c in campaigns if c["strategy"] == selected_strategy]

        if filtered:
            best = filtered[0]
            score = len(best["headline"]) + len(best["hook"])
        else:
            optimized = optimizer_tool(campaigns)
            best = optimized["best_campaign"]
            score = optimized["optimization_score"]

        result = {
            "best_campaign": best,
            "all_campaigns": campaigns,
            "optimization_score": score,
            "decision_meta": decision,
            "objective": input_data.get("objective", "mixed"),
            "analysis": input_data.get("analysis", {}),
            "structured_intelligence": input_data.get("structured_intelligence", {}),
            "scored_opportunities": input_data.get("scored_opportunities", {}),
            "validation": input_data.get("validation", {}),
            "reasoning": input_data.get("reasoning", {}),
            "research": input_data.get("research", {}),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "execution_plan": execution_plan,
        }
        logger.info("campaign:done strategy=%s", decision.get("selected_strategy"))
        return result
