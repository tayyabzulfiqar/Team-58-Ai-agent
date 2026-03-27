import os
import sys
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from controllers.agent_controller import (
    build_top_three_report_entries,
    print_executive_summary,
    save_json,
    save_text,
)
from agents.research_agent import run as research_run
from agents.insights_agent import run as insights_run
from agents.strategy_agent import run as strategy_run
from scripts.intelligence_tools import discover_trending_celebrities
from scripts.client_report_builder import build_final_report

app = FastAPI(title="Team-58 AI Agent API", version="1.0.0")

@app.get("/")
async def root():
    return {"status": "ok", "service": "Team-58 AI Agent API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze():
    try:
        research_data = research_run()
        insights_data = insights_run(research_data)
        strategies = strategy_run(insights_data)
        ranked_celebrities = discover_trending_celebrities(limit=3)
        top_entries = build_top_three_report_entries(ranked_celebrities, insights_data, strategies)
        report = build_final_report(top_entries, insights_data, strategies)
        save_json("top_celebrities.json", ranked_celebrities)
        save_json("celebrity_growth_report.json", top_entries)
        save_text("client_ready_report.md", report)
        return {"status": "success", "celebrities_analyzed": len(ranked_celebrities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
