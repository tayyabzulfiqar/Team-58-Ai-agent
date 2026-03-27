import json

INPUT_PATH = "data/processed/processed_data.json"
OUTPUT_PATH = "data/processed/ai_enriched.json"

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def ai_analyze(text):
    text = text.lower()

    if "ai" in text or "gpt" in text:
        return "AI", "Growing AI trend", 9
    elif "startup" in text:
        return "Startup", "Startup activity rising", 7
    else:
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