"""
FastAPI Server for AI Engine Dashboard
Provides endpoints to run full pipeline and get results
"""
import sys
import os

# Add project root to Python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import json
from pathlib import Path
from datetime import datetime

# Try to import optional components - fail gracefully if they don't work
try:
    from scripts.core.master_controller import MasterController
    controller = MasterController()
    CONTROLLER_AVAILABLE = True
except Exception as e:
    print(f"Warning: MasterController not available: {e}")
    controller = None
    CONTROLLER_AVAILABLE = False

try:
    from scripts.scheduler.auto_scheduler import start_scheduler, get_scheduler_status
    from scripts.scheduler.event_trigger import get_priority_events, get_latest_priority_run, check_leads_batch
    SCHEDULER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Scheduler not available: {e}")
    start_scheduler = None
    get_scheduler_status = None
    get_priority_events = None
    get_latest_priority_run = None
    check_leads_batch = None
    SCHEDULER_AVAILABLE = False

try:
    from scripts.env_debug import print_env_status
except Exception as e:
    print(f"Warning: env_debug not available: {e}")
    def print_env_status():
        print("Env debug not available")

app = FastAPI(
    title="AI Engine API",
    description="API for running AI pipeline and getting intelligence results",
    version="1.0.0"
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start auto-scheduler on startup
scheduler_started = False

class LeadInput(BaseModel):
    name: str
    company: str
    industry: str
    budget: float
    location: str

class PipelineRequest(BaseModel):
    leads: List[LeadInput]

class SingleAgentRequest(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]
    role: str = "admin"

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        from scripts.intelligence_tools import chat_with_claude
        response = chat_with_claude(request.message)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Start auto-scheduler on server startup"""
    global scheduler_started
    
    # Print environment variable status for debugging
    print_env_status()
    
    if not scheduler_started and SCHEDULER_AVAILABLE and start_scheduler:
        try:
            start_scheduler()
            scheduler_started = True
            print("✓ Auto-scheduler started")
        except Exception as e:
            print(f"✗ Auto-scheduler failed to start: {e}")
    else:
        print("ℹ Scheduler not available or already started")

@app.get("/")
async def root():
    return {"status": "AI Engine API Running", "version": "1.0.0", "auto_run": SCHEDULER_AVAILABLE}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if CONTROLLER_AVAILABLE and controller:
            status = controller.get_system_status()
        else:
            status = {"system": "not_available"}
        
        if SCHEDULER_AVAILABLE and get_scheduler_status:
            scheduler_status = get_scheduler_status()
        else:
            scheduler_status = {"running": False}
            
        return {
            "status": "healthy",
            "system": status,
            "scheduler": scheduler_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    if not CONTROLLER_AVAILABLE or not controller:
        return {"agents": [], "error": "Controller not available"}
    try:
        agents = controller.agent_registry.list_agents()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-full")
async def run_full_pipeline(request: PipelineRequest):
    """
    Run full AI pipeline with leads
    Returns: strategies, predictions, market insights, etc.
    """
    if not CONTROLLER_AVAILABLE or not controller:
        return {"error": "Controller not available", "status": "failed"}
    try:
        # Convert leads to format expected by controller
        leads_data = [
            {
                "name": lead.name,
                "company": lead.company,
                "industry": lead.industry,
                "budget": lead.budget,
                "location": lead.location
            }
            for lead in request.leads
        ]
        
        # Run full pipeline
        result = controller.run_full_pipeline(leads_data, role="admin")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-agent")
async def run_single_agent(request: SingleAgentRequest):
    """
    Run a single agent with input data
    """
    if not CONTROLLER_AVAILABLE or not controller:
        return {"error": "Controller not available", "status": "failed"}
    try:
        result = controller.run_single_agent(
            request.agent_name,
            request.input_data,
            request.role
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_system_status():
    """Get current system status"""
    if not CONTROLLER_AVAILABLE or not controller:
        return {"error": "Controller not available"}
    try:
        return controller.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/live-data")
async def get_live_data():
    """
    Get latest run data from auto-scheduler
    Returns: data/live/latest_run.json
    """
    try:
        live_data_path = Path("data/live/latest_run.json")
        
        if not live_data_path.exists():
            scheduler_status = get_scheduler_status() if (SCHEDULER_AVAILABLE and get_scheduler_status) else {"running": False}
            return {
                "status": "no_data",
                "message": "No live data available yet. Scheduler is running...",
                "scheduler": scheduler_status
            }
        
        with open(live_data_path, 'r') as f:
            live_data = json.load(f)
        
        return live_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/status")
async def scheduler_status():
    """Get auto-scheduler status"""
    if SCHEDULER_AVAILABLE and get_scheduler_status:
        return get_scheduler_status()
    return {"error": "Scheduler not available", "running": False}

@app.post("/scheduler/trigger")
async def trigger_run():
    """Manually trigger a pipeline run"""
    if not CONTROLLER_AVAILABLE or not controller:
        return {"error": "Controller not available", "status": "failed"}
    try:
        result = controller.run_full_pipeline(
            {"leads": [
                {"name": "Manual Lead 1", "company": "TestCorp", "industry": "Tech", "budget": 50000, "location": "Dubai"},
                {"name": "Manual Lead 2", "company": "TestInc", "industry": "Finance", "budget": 100000, "location": "London"}
            ]},
            role="admin"
        )
        
        # Save to live data
        live_data = {
            "timestamp": datetime.now().isoformat(),
            "run_id": "manual",
            "status": "success",
            "data": result
        }
        
        live_data_path = Path("data/live/latest_run.json")
        live_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(live_data_path, 'w') as f:
            json.dump(live_data, f, indent=2, default=str)
        
        return {"status": "success", "message": "Pipeline triggered manually", "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-system")
async def run_system():
    """
    Run full AI system pipeline and return formatted results for dashboard
    Executes: data_agent → processing → intelligence → decision → qualification
    """
    if not CONTROLLER_AVAILABLE or not controller:
        return {
            "opportunities": [],
            "scores": [],
            "decisions": [],
            "campaigns": [],
            "status": "error",
            "message": "Controller not available"
        }
    
    try:
        # Run full pipeline with sample leads
        result = controller.run_full_pipeline(
            {"leads": [
                {"name": "Acme Corp", "company": "Acme", "industry": "Technology", "budget": 75000, "location": "San Francisco"},
                {"name": "Global Finance", "company": "GF Inc", "industry": "Finance", "budget": 120000, "location": "New York"},
                {"name": "Health Plus", "company": "HealthPlus", "industry": "Healthcare", "budget": 45000, "location": "Boston"},
                {"name": "Retail Giant", "company": "RetailGiant", "industry": "Retail", "budget": 90000, "location": "Chicago"}
            ]},
            role="admin"
        )
        
        # Extract and format data for dashboard
        opportunities = []
        scores = []
        decisions = []
        campaigns = []
        
        if "results" in result and "strategies" in result["results"]:
            strategies = result["results"]["strategies"]
            if "individual_decisions" in strategies:
                for i, decision in enumerate(strategies["individual_decisions"]):
                    opportunities.append({
                        "id": i + 1,
                        "name": decision.get("lead_name", f"Opportunity {i+1}"),
                        "company": decision.get("company", "Unknown"),
                        "score": decision.get("priority_score", 0),
                        "status": decision.get("decision", "Pending"),
                        "revenue_potential": decision.get("revenue_potential", 0),
                        "industry": decision.get("industry", "Unknown"),
                        "location": decision.get("location", "Unknown")
                    })
            
            if "strategic_recommendations" in strategies:
                decisions = strategies["strategic_recommendations"]
        
        # Format scores for analytics
        if opportunities:
            scores = [opp["score"] for opp in opportunities]
        
        # Create campaigns from opportunities
        for opp in opportunities[:3]:
            campaigns.append({
                "id": opp["id"],
                "name": f"Campaign for {opp['name']}",
                "status": "Active" if opp["score"] > 80 else "Pending",
                "budget": opp["revenue_potential"],
                "roi": round(opp["score"] * 1.2, 1),
                "target": opp["industry"]
            })
        
        return {
            "opportunities": opportunities,
            "scores": scores,
            "decisions": decisions,
            "campaigns": campaigns,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "raw_data": result
        }
        
    except Exception as e:
        return {
            "opportunities": [],
            "scores": [],
            "decisions": [],
            "campaigns": [],
            "status": "error",
            "message": str(e)
        }

@app.get("/priority-events")
async def priority_events(limit: int = 50):
    """
    Get all high-priority events
    Returns: List of high-value lead triggers (score > 90 or revenue > $50K)
    """
    if not SCHEDULER_AVAILABLE or not get_priority_events:
        return {"error": "Priority events not available", "count": 0, "events": []}
    try:
        events = get_priority_events(limit)
        return {
            "status": "success",
            "count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/priority-events/latest")
async def latest_priority_event():
    """
    Get latest priority run
    """
    if not SCHEDULER_AVAILABLE or not get_latest_priority_run:
        return {"status": "no_data", "message": "Priority events not available"}
    try:
        event = get_latest_priority_run()
        if event is None:
            return {
                "status": "no_data",
                "message": "No priority events yet"
            }
        return {
            "status": "success",
            "event": event
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
