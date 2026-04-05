import os
import sys

from fastapi import FastAPI
from fastapi import Body

# Support running `uvicorn main:app` from inside the `backend/` directory.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.core.orchestrator import run_system

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
