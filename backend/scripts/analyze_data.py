import json
from collections import Counter
from datetime import datetime

INPUT_PATH = "data/processed/processed_data.json"
OUTPUT_PATH = "data/processed/analysis_output.json"

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_tags(data):
    counter = Counter()
    for item in data:
        for tag in item["tags"]:
            counter[tag] += 1
    return counter

def calculate_trends(tag_counts):
    trends = []
    for tag, count in tag_counts.items():
        trends.append({
            "trend": tag,
            "count": count,
            "score": count * 10
        })
    trends.sort(key=lambda x: x["score"], reverse=True)
    return trends

def detect_opportunities(trends):
    opportunities = []
    for t in trends:
        if t["score"] >= 20:
            opportunities.append({
                "trend": t["trend"],
                "opportunity": "High demand detected",
                "score": t["score"]
            })
    return opportunities

def run():
    data = load_data()
    tag_counts = analyze_tags(data)
    trends = calculate_trends(tag_counts)
    opportunities = detect_opportunities(trends)

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "trends": trends,
        "opportunities": opportunities
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Analysis Complete")

if __name__ == "__main__":
    run()