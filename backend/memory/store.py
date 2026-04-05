import json
import os


MEMORY_FILE = "backend/memory/data.json"


def save_run(data):
    if not os.path.exists("backend/memory"):
        os.makedirs("backend/memory")

    if not os.path.exists(MEMORY_FILE):
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

    if not os.path.exists("backend/memory"):
        os.makedirs("backend/memory")

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)
