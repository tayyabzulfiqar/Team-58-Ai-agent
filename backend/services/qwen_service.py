import os

import requests

from core.logging_utils import get_logger


logger = get_logger("team58.qwen")
API_KEY = os.getenv("QWEN_API_KEY") or "sk-36f731a2000b49f4b76b2b6bb3b6a1ca"
BASE_URL = os.getenv("QWEN_BASE_URL") or "https://ws-7cdqxbw1m3iabksm.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = os.getenv("QWEN_MODEL", "qwen-plus")


def qwen_generate(prompt: str, *, system_prompt: str = "You are an AI analyst helping extract insights.") -> str:
    if not API_KEY:
        raise RuntimeError("QWEN_API_KEY is not configured.")

    url = f"{BASE_URL}/chat/completions"
    logger.info("qwen:start prompt_chars=%s", len(prompt))

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt[:6000]},
            ],
            "temperature": 0,
        },
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Invalid Qwen response payload: {data}") from exc

    if not content or not str(content).strip():
        raise RuntimeError("Qwen returned an empty response.")

    logger.info("qwen:done response_chars=%s", len(content))
    return str(content).strip()
