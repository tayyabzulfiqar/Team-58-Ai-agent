from datetime import datetime, timezone
from typing import Any

from fastapi import Body
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.orchestrator import run_system

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_input_text(input_data: Any) -> str:
    if isinstance(input_data, dict):
        raw = input_data.get("input") or input_data.get("query") or input_data.get("prompt") or ""
        return str(raw).strip()
    return str(input_data).strip()


def _build_default_campaigns(subject: str) -> list[dict[str, str]]:
    base_subject = subject or "your business"
    return [
        {
            "strategy": "Performance marketing",
            "headline": f"Scale faster with a performance push for {base_subject}",
            "hook": "Turn intent signals into measurable conversions.",
            "cta": "Launch the optimized campaign",
        },
        {
            "strategy": "Emotional marketing",
            "headline": f"Build trust and momentum around {base_subject}",
            "hook": "Lead with narrative, credibility, and audience connection.",
            "cta": "Activate the story-led campaign",
        },
        {
            "strategy": "Brand awareness",
            "headline": f"Expand visibility for {base_subject} across key channels",
            "hook": "Own attention early with a memorable awareness strategy.",
            "cta": "Start the awareness rollout",
        },
    ]


def _simulate_pipeline(input_data: Any, error_message: str | None = None) -> dict[str, Any]:
    subject = _extract_input_text(input_data) or "business growth"
    campaigns = _build_default_campaigns(subject)
    best_campaign = campaigns[0]

    return {
        "best_campaign": best_campaign,
        "all_campaigns": campaigns,
        "optimization_score": 86,
        "decision_meta": {
            "selected_strategy": best_campaign["strategy"],
            "alternatives": [campaign["strategy"] for campaign in campaigns[1:]],
            "reason": "Fallback simulation executed while keeping the multi-agent flow available.",
            "confidence": 86,
            "status": "simulated",
        },
        "objective": "conversion",
        "simulation_error": error_message,
    }


def _normalize_result(input_data: Any, pipeline_result: dict[str, Any], simulated: bool) -> dict[str, Any]:
    subject = _extract_input_text(input_data) or "business growth"
    decision_meta = pipeline_result.get("decision_meta", {}) if isinstance(pipeline_result, dict) else {}
    campaigns = pipeline_result.get("all_campaigns") if isinstance(pipeline_result, dict) else None

    if not isinstance(campaigns, list) or not campaigns:
        campaigns = _build_default_campaigns(subject)

    best_campaign = pipeline_result.get("best_campaign") if isinstance(pipeline_result, dict) else None
    if not isinstance(best_campaign, dict):
        selected_strategy = decision_meta.get("selected_strategy")
        best_campaign = next(
            (campaign for campaign in campaigns if campaign.get("strategy") == selected_strategy),
            campaigns[0],
        )

    optimization_score = pipeline_result.get("optimization_score") if isinstance(pipeline_result, dict) else None
    if not isinstance(optimization_score, (int, float)):
        optimization_score = int(decision_meta.get("confidence", 82))

    objective = "mixed"
    if isinstance(pipeline_result, dict):
        objective = str(pipeline_result.get("objective") or "mixed")

    agent_states = [
        {
            "id": "research",
            "name": "Research Agent",
            "shortName": "RESEARCH",
            "status": "active",
            "currentTask": f"Collected market context for '{subject}'",
            "confidence": max(int(decision_meta.get("confidence", 82)) - 4, 50),
        },
        {
            "id": "processing",
            "name": "Data Agent",
            "shortName": "DATA",
            "status": "processing",
            "currentTask": "Normalized signals and prepared structured analysis",
            "confidence": max(int(decision_meta.get("confidence", 82)) - 2, 50),
        },
        {
            "id": "intelligence",
            "name": "Intelligence Agent",
            "shortName": "INTEL",
            "status": "active",
            "currentTask": f"Ranked '{decision_meta.get('selected_strategy', 'best-fit strategy')}' opportunities",
            "confidence": int(decision_meta.get("confidence", 82)),
        },
        {
            "id": "decision",
            "name": "Decision Agent",
            "shortName": "DECIDE",
            "status": "active",
            "currentTask": decision_meta.get("reason", "Selected the strongest campaign strategy"),
            "confidence": int(decision_meta.get("confidence", 82)),
        },
        {
            "id": "campaign",
            "name": "Campaign Agent",
            "shortName": "CAMPAIGN",
            "status": "active",
            "currentTask": f"Prepared launch assets for '{best_campaign.get('strategy', 'campaign execution')}'",
            "confidence": min(int(decision_meta.get("confidence", 82)) + 1, 99),
        },
    ]

    feed = [
        {
            "id": "feed-research",
            "agent": "Research Agent",
            "type": "success",
            "message": f"Research stage completed for '{subject}'.",
            "detail": f"Objective detected: {objective}",
            "timestamp": _timestamp(),
        },
        {
            "id": "feed-data",
            "agent": "Data Agent",
            "type": "processing",
            "message": "Data agent converted findings into structured campaign inputs.",
            "detail": f"{len(campaigns)} campaign options are ready for scoring.",
            "timestamp": _timestamp(),
        },
        {
            "id": "feed-decision",
            "agent": "Decision Agent",
            "type": "info",
            "message": decision_meta.get("reason", "Decision engine selected the best strategy."),
            "detail": f"Chosen strategy: {decision_meta.get('selected_strategy', best_campaign.get('strategy', 'N/A'))}",
            "timestamp": _timestamp(),
        },
        {
            "id": "feed-campaign",
            "agent": "Campaign Agent",
            "type": "success" if not simulated else "warning",
            "message": "Campaign payload prepared for the dashboard.",
            "detail": "Simulation mode is active." if simulated else "Live pipeline response delivered.",
            "timestamp": _timestamp(),
        },
    ]

    return {
        "status": "success",
        "message": "System executed" if not simulated else "System executed in simulation mode",
        "data": {
            "input": subject,
            "objective": objective,
            "insight": best_campaign.get("headline", "Campaign recommendation generated."),
            "summary": decision_meta.get("reason", "Decision engine selected the strongest option."),
            "best_campaign": best_campaign,
            "all_campaigns": campaigns,
            "optimization_score": optimization_score,
            "decision_meta": decision_meta,
            "agent_states": agent_states,
            "feed": feed,
            "simulated": simulated,
            "error": pipeline_result.get("simulation_error") if simulated else None,
        },
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "AI Engine Running",
        "agents": ["research", "data", "campaign"]
    }

@app.post("/run-system")
@app.post("/api/run-system")
def run_system_endpoint(input_data: dict = Body(default={})):
    try:
        pipeline_result = run_system(input_data)
        if not isinstance(pipeline_result, dict):
            pipeline_result = _simulate_pipeline(input_data, "Pipeline returned a non-dict response.")
            return _normalize_result(input_data, pipeline_result, simulated=True)
        return _normalize_result(input_data, pipeline_result, simulated=False)
    except Exception as exc:
        pipeline_result = _simulate_pipeline(input_data, str(exc))
        return _normalize_result(input_data, pipeline_result, simulated=True)
