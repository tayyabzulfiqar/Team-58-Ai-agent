import json

INPUT_PATH = "data/processed/ai_enriched.json"
OUTPUT_PATH = "data/processed/leads.txt"

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_leads(data):
    leads = []

    for item in data:
        text = item["text"]
        score = item.get("ai_score", 0)

        if score >= 8:
            lead = f"""
LEAD OPPORTUNITY:
Problem detected: "{text}"

TARGET CLIENT:
- Startups
- Small businesses
- Tech companies

SERVICE YOU CAN SELL:
- AI automation
- SaaS tool
- Consulting service

OUTREACH IDEA:
"Hey, we help businesses solve this exact problem using AI. Let's talk."
"""
            leads.append(lead)

    return leads

def save_leads(leads):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(leads))

    print("Leads generated:", OUTPUT_PATH)

def run():
    data = load_data()
    leads = generate_leads(data)
    save_leads(leads)

if __name__ == "__main__":
    run()