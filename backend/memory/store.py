import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


MEMORY_DIR = Path(__file__).resolve().parent
RUN_HISTORY_FILE = MEMORY_DIR / "run_history.json"
DECISION_HISTORY_FILE = MEMORY_DIR / "decision_history.json"
OUTCOME_FILE = MEMORY_DIR / "outcomes.json"
RESEARCH_CACHE_FILE = MEMORY_DIR / "research_cache.json"


def _ensure_memory_dir() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
    _ensure_memory_dir()
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, payload) -> None:
    _ensure_memory_dir()
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def save_run(data):
    history = _read_json(RUN_HISTORY_FILE, [])
    history.append(data)
    _write_json(RUN_HISTORY_FILE, history)


def record_decision(input_data, strategy, confidence, decision_inputs=None):
    history = _read_json(DECISION_HISTORY_FILE, [])
    history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_data,
            "strategy": strategy,
            "confidence": confidence,
            "decision_inputs": decision_inputs or {},
        }
    )
    _write_json(DECISION_HISTORY_FILE, history)


def store_outcome(input_data, strategy, confidence, success=False, metrics=None):
    outcomes = _read_json(OUTCOME_FILE, [])
    outcomes.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_data,
            "strategy": strategy,
            "confidence": confidence,
            "success": bool(success),
            "metrics": metrics or {},
        }
    )
    _write_json(OUTCOME_FILE, outcomes)


def successful_outcomes(strategy: str) -> list[dict]:
    outcomes = _read_json(OUTCOME_FILE, [])
    return [
        item
        for item in outcomes
        if isinstance(item, dict) and item.get("strategy") == strategy and item.get("success") is True
    ]


def get_cached_research(query: str, max_age_hours: int = 24):
    cache = _read_json(RESEARCH_CACHE_FILE, {})
    entry = cache.get(query)
    if not entry:
        return None

    timestamp = datetime.fromisoformat(entry["timestamp"])
    if datetime.now(timezone.utc) - timestamp > timedelta(hours=max_age_hours):
        return None

    return entry["payload"]


def store_cached_research(query: str, payload: dict):
    cache = _read_json(RESEARCH_CACHE_FILE, {})
    cache[query] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    _write_json(RESEARCH_CACHE_FILE, cache)
