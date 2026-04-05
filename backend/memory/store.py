import json
import os
from pathlib import Path


MEMORY_DIR = Path(__file__).resolve().parent
MEMORY_FILE = MEMORY_DIR / "data.json"


def save_run(data):
    if not MEMORY_DIR.exists():
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not MEMORY_FILE.exists():
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)

    with open(MEMORY_FILE, "r") as f:
        existing = json.load(f)

    existing.append(data)

    with open(MEMORY_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def store_outcome(input_data, strategy, confidence):
    entry = {
        "input": input_data,
        "strategy": strategy,
        "confidence": confidence
    }

    if not MEMORY_DIR.exists():
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)
