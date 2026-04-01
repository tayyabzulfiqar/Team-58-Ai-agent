import json
import os
import sys
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.campaign_agent import run as campaign_run
from agents.celebrity_agent import run as celebrity_run
from agents.deal_agent import run as deal_run
from agents.growth_agent import run as growth_run
from agents.insights_agent import run as insights_run
from agents.research_agent import run as research_run
from agents.strategy_agent import run as strategy_run
from scripts.client_report_builder import build_final_report
from scripts.intelligence_tools import discover_trending_celebrities


OUTPUT_DIR = "data/processed"


def save_json(filename: str, payload: Any) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def save_text(filename: str, content: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as file:
        file.write(content)


def build_celebrity_strategy(celebrity_data: Dict[str, Any]) -> List[Dict[str, str]]:
    content_type = str(celebrity_data.get("top_content", "creator"))
    return [
        {
            "pattern": f"{celebrity_data.get('name', 'Celebrity')} {content_type} Dubai growth",
            "target_audience": celebrity_data.get("audience", "Global digital audience"),
            "pain_point": "Need to convert attention into premium brand demand in Dubai.",
            "solution": (
                f"Use {content_type}-led storytelling to activate Dubai brand partnerships and audience conversion. "
                f"{celebrity_data.get('market_fit', 'Position with Dubai-specific premium partnerships.')}"
            ),
            "business_idea": (
                f"Launch a Dubai-first {content_type} celebrity campaign sprint for {celebrity_data.get('name', 'the talent')}."
            ),
            "marketing_hook": (
                f"Turn {celebrity_data.get('name', 'the talent')}'s {content_type} audience momentum into a Dubai brand acquisition engine."
            ),
        }
    ]


def build_top_three_report_entries(
    ranked_celebrities: List[Dict[str, Any]], insights: Dict[str, Any], strategies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    entries = []

    for ranked in ranked_celebrities[:3]:
        celebrity_name = ranked.get("name", "")
        celebrity_data = celebrity_run(celebrity_name)
        celebrity_data["ranking_score"] = ranked.get("ranking_score", celebrity_data.get("ranking_score"))
        celebrity_data["engagement_potential"] = ranked.get("engagement_potential", celebrity_data.get("engagement_potential"))
        celebrity_data["audience_size"] = ranked.get("audience_size", celebrity_data.get("audience_size"))
        celebrity_data["virality_probability"] = ranked.get("virality_probability", celebrity_data.get("virality_probability"))
        celebrity_data["brand_alignment_score"] = ranked.get("brand_alignment_score", celebrity_data.get("brand_alignment_score"))

        celebrity_strategies = build_celebrity_strategy(celebrity_data) + strategies[:2]
        campaigns = campaign_run(celebrity_strategies)
        growth_plan = growth_run(celebrity_data, insights, celebrity_strategies)
        deal_data = deal_run(celebrity_data)

        entries.append(
            {
                "celebrity_data": celebrity_data,
                "campaigns": campaigns,
                "growth_plan": growth_plan,
                "deal_data": deal_data,
            }
        )

    return entries


def print_executive_summary(entries: List[Dict[str, Any]]) -> None:
    print("\n=== FINAL OUTPUT ===")
    for index, entry in enumerate(entries, start=1):
        celebrity = entry["celebrity_data"]
        growth = entry["growth_plan"]
        deal = entry["deal_data"]
        roi = deal.get("roi_projection", {})

        print(f"\n{index}. Celebrity: {celebrity.get('name', 'N/A')}")
        print(f"Research Summary: {celebrity.get('research_summary', 'N/A')}")
        print(f"Growth Plan: {growth.get('growth_plan', 'N/A')}")
        print(f"Monetization: {deal.get('monetization_strategy', {}).get('lead_generation_strategy', 'N/A')}")
        print(
            f"ROI: Reach {roi.get('estimated_reach', 'N/A')} | Leads {roi.get('estimated_leads', 'N/A')} | "
            f"Revenue {roi.get('estimated_revenue', 'N/A')} | ROAS {roi.get('projected_roas', 'N/A')}"
        )


def main() -> None:
    try:
        print("Starting Research Agent...")
        research_data = research_run()
        print("Research complete")

        print("Starting Insights Agent...")
        insights_data = insights_run(research_data)
        print("Insights complete")

        print("Starting Strategy Agent...")
        strategies = strategy_run(insights_data)
        print("Strategy complete")

        print("Discovering trending celebrities...")
        ranked_celebrities = discover_trending_celebrities(limit=3)
        print(f"Discovered and ranked {len(ranked_celebrities)} celebrities")

        print("Building celebrity intelligence dossiers...")
        top_entries = build_top_three_report_entries(ranked_celebrities, insights_data, strategies)

        report = build_final_report(top_entries, insights_data, strategies)

        save_json("top_celebrities.json", ranked_celebrities)
        save_json("celebrity_growth_report.json", top_entries)
        save_text("client_ready_report.md", report)

        print_executive_summary(top_entries)
        print("\nClient-ready report saved to data/processed/client_ready_report.md")
        print("All agents completed successfully")

    except Exception as exc:
        print("Controller Error:", exc)


if __name__ == "__main__":
    main()
