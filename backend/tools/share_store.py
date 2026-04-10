import json
import os
import uuid
from datetime import datetime
from typing import Optional

FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "share_links.json"))


def _load_links():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_links(links):
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    tmp_path = f"{FILE_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2)
    os.replace(tmp_path, FILE_PATH)


def create_share_link(report_id: str) -> str:
    share_id = str(uuid.uuid4())
    links = _load_links()
    links.append(
        {
            "share_id": share_id,
            "report_id": report_id,
            "created_at": datetime.utcnow().isoformat(),
        }
    )
    _save_links(links)
    return share_id


def get_report_id_for_share(share_id: str) -> Optional[str]:
    links = _load_links()
    for link in links:
        if isinstance(link, dict) and link.get("share_id") == share_id:
            rid = link.get("report_id")
            return rid if isinstance(rid, str) and rid else None
    return None

