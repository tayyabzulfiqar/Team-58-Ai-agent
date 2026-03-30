import json
from datetime import datetime

INPUT_PATH = "data/processed/ai_enriched.json"
OUTPUT_PATH = "data/processed/daily_report.txt"

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_report(data):
    high_value = []
    medium_value = []

    for item in data:
        score = item.get("ai_score", 0)

        if score >= 8:
            high_value.append(item)
        elif score >= 6:
            medium_value.append(item)

    report = []

    report.append("=" * 60)
    report.append("DAILY AI MARKET INTELLIGENCE REPORT")
    report.append(f"Generated: {datetime.now()}")
    report.append("=" * 60)

    report.append("\nTOP HIGH-VALUE OPPORTUNITIES:\n")

    for item in high_value[:10]:
        report.append(f"[AI] {item['text']} (Score: {item['ai_score']})")

    report.append("\nEMERGING SIGNALS:\n")

    for item in medium_value[:10]:
        report.append(f"[MONITOR] {item['text']} (Score: {item['ai_score']})")

    report.append("\nRECOMMENDED ACTION:\n")
    report.append("- Focus on AI and automation trends")
    report.append("- Validate top ideas in market")
    report.append("- Build or sell solutions around high-score signals")

    return "\n".join(report)

def save_report(report):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print("Report generated:", OUTPUT_PATH)

def run():
    data = load_data()
    report = generate_report(data)
    save_report(report)

if __name__ == "__main__":
    run()