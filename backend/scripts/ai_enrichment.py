import os

import json
from utils.llm import llm_call

# SYSTEM GUARD: SSOT - raw_data.json is READ ONLY
INPUT_PATH = os.path.abspath("backend/data/processed/processed_data.json")
OUTPUT_PATH = os.path.abspath("backend/data/processed/ai_enriched.json")

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def ai_analyze(text):
    prompt = f"Analyze this text and provide AI category, insight, and score as JSON. Text: {text}"
    try:
        response = llm_call(prompt)
        data = json.loads(response)
        return (
            data.get("ai_category", "General"),
            data.get("ai_insight", "No strong signal"),
            data.get("ai_score", 5)
        )
    except Exception as e:
        return "General", "No strong signal", 5

def run():
    data = load_data()
    enriched = []

    for item in data:
        category, insight, score = ai_analyze(item["text"])

        enriched.append({
            **item,
            "ai_category": category,
            "ai_insight": insight,
            "ai_score": score
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)

    print("AI Enrichment Complete")

if __name__ == "__main__":
    run()