import json
import os
import uuid
from datetime import datetime

FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "reports.json"))


def load_reports():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_reports(reports):
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    tmp_path = f"{FILE_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)
    os.replace(tmp_path, FILE_PATH)


def create_report(data):
    reports = load_reports()

    report = {
        "report_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "title": data.get("main_problem", "Report"),
        "confidence_score": data.get("confidence_score", 0),
        "saved": False,
        "data": data,
    }

    reports.append(report)
    save_reports(reports)

    return report


def get_all_reports():
    return load_reports()


def get_report(report_id):
    reports = load_reports()
    for r in reports:
        if r.get("report_id") == report_id:
            return r
    return None


def toggle_save(report_id):
    reports = load_reports()
    for r in reports:
        if r.get("report_id") == report_id:
            r["saved"] = not r.get("saved", False)
            save_reports(reports)
            return r
    return None


def get_saved_reports():
    reports = load_reports()
    return [r for r in reports if isinstance(r, dict) and r.get("saved") is True]
