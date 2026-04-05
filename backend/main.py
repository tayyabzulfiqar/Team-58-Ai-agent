from fastapi import FastAPI
from fastapi import Body

from core.orchestrator import run_system

app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "AI Engine Running",
        "agents": ["research", "data", "campaign"]
    }

@app.post("/run-system")
def run_system_endpoint(input_data: dict = Body(default={})):
    return run_system(input_data)
