import logging
from scripts.agents.campaign_agent import generate_campaign
from scripts.agents.research_agent import research_market
from scripts.agents.data_analyzer_agent import analyze_data

logger = logging.getLogger("orchestrator")

def safe_json_parse(content):
    import json
    try:
        return json.loads(content)
    except Exception:
        return {"raw_output": content}


import json
from pathlib import Path

CAMPAIGN_HISTORY_PATH = Path(__file__).parent.parent.parent / "data" / "campaigns" / "campaigns.json"

def save_campaign_to_history(entry: dict):
    try:
        if CAMPAIGN_HISTORY_PATH.exists():
            with open(CAMPAIGN_HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
        history.append(entry)
        with open(CAMPAIGN_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save campaign: {e}")

def fetch_campaign_history() -> list:
    try:
        if CAMPAIGN_HISTORY_PATH.exists():
            with open(CAMPAIGN_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Failed to fetch campaign history: {e}")
        return []

def run_campaign_workflow(product: str, audience: str) -> dict:
    try:
        research = research_market(product)
        if research.get("status") == "error":
            logger.error("Research agent failed.")
            return {"status": "error", "message": "Research agent failed", "data": research}
        campaign = generate_campaign(product, audience)
        if campaign.get("status") == "error":
            logger.error("Campaign agent failed.")
            return {"status": "error", "message": "Campaign agent failed", "data": campaign}
        result = {"research": research["data"], "campaign": campaign["data"], "product": product, "audience": audience}
        save_campaign_to_history(result)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Orchestrator workflow error: {e}")
        return {"status": "error", "message": str(e)}

def run_data_analysis(data: dict) -> dict:
    try:
        # Add scoring system (0-100) and improved campaign
        analysis = analyze_data(data)
        if analysis.get("status") == "error":
            logger.error("Data analyzer agent failed.")
            return {"status": "error", "message": "Data analyzer agent failed", "data": analysis}
        # Simple scoring: count keywords, length, etc.
        campaign = data.get("campaign") or data
        score = 50
        if isinstance(campaign, dict):
            score += 25 if len(str(campaign.get("headline", ""))) > 10 else 0
            score += 25 if len(str(campaign.get("ad_copy", ""))) > 30 else 0
            score = min(score, 100)
        improved = dict(campaign)
        if isinstance(improved, dict):
            improved["headline"] = (improved.get("headline", "") + " (Improved)")
        return {"status": "success", "data": {"analysis": analysis["data"], "score": score, "improved_campaign": improved}}
    except Exception as e:
        logger.error(f"Orchestrator data analysis error: {e}")
        return {"status": "error", "message": str(e)}
