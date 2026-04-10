import json
import os
from typing import Any, Dict, Optional

import requests


QWEN_SYSTEM_PROMPT = (
    "Convert structured business intelligence JSON into a high-quality consulting report. Use sections:\n"
    "- Main Problem\n"
    "- Key Insight\n"
    "- Strategy\n"
    "- Execution Plan\n"
    "- Campaign Plan\n"
    "Make it clear, concise, and professional."
)


def _extract_text(payload: Any) -> Optional[str]:
    if not isinstance(payload, dict):
        return None

    output = payload.get("output")
    if isinstance(output, dict):
        choices = output.get("choices")
        if isinstance(choices, list) and choices:
            c0 = choices[0] if isinstance(choices[0], dict) else {}
            msg = c0.get("message") if isinstance(c0.get("message"), dict) else {}
            content = msg.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
            text = c0.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
        text = output.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()

    return None


def generate_consulting_report(data: Dict[str, Any], timeout_s: float = 5.0) -> Optional[str]:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        return None

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    payload: Dict[str, Any] = {
        "model": "qwen-turbo",
        "input": {
            "messages": [
                {"role": "system", "content": QWEN_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(data)},
            ]
        },
        "parameters": {"result_format": "message"},
    }

    try:
        res = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=timeout_s,
        )
        res.raise_for_status()
        parsed = res.json()
        return _extract_text(parsed)
    except Exception:
        return None
