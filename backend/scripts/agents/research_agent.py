import os
import logging
import openai

logger = logging.getLogger("research_agent")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")
    raise RuntimeError("OPENAI_API_KEY is required.")
openai.api_key = OPENAI_API_KEY

import os
import logging
from openai import OpenAI
import signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("research_agent")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")
    raise RuntimeError("OPENAI_API_KEY is required.")
client = OpenAI(api_key=OPENAI_API_KEY)

def safe_json_parse(content):
    import json
    try:
        return json.loads(content)
    except Exception:
        return {"raw_output": content}

def research_market(topic: str) -> dict:
    if not isinstance(topic, str) or len(topic) < 3:
        return {"status": "error", "message": "Invalid input: topic must be string of min length 3."}
    prompt = f"""
You are a market research expert. For the topic/niche: {topic}, return a JSON with:
trends (list), competitors (list), keywords (list).
"""
    try:
        def handler(signum, frame):
            raise TimeoutError("OpenAI call timed out")
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(15)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
            timeout=15
        )
        signal.alarm(0)
        content = response.choices[0].message.content
        result = safe_json_parse(content)
        logger.info("Research completed successfully.")
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Research failed: {e}")
        return {"status": "error", "message": str(e)}
    prompt = f"""
You are a market research expert. For the topic/niche: {topic}, return a JSON with:
trends (list), competitors (list), keywords (list).
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        content = response.choices[0].message.content
        import json
        result = json.loads(content)
        logger.info("Research completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Research failed: {e}")
        return {"error": str(e)}
