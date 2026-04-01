import json

INPUT_PATH = "data/processed/ai_enriched.json"
OUTPUT_PATH = "data/processed/ideas.txt"

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_ideas(data):
    ideas = []

    for item in data:
        text = item["text"]
        score = item.get("ai_score", 0)

        if score >= 8:
            idea = f"""
IDEA:
Build a SaaS or service around: "{text}"

HOW TO MAKE MONEY:
- Create a solution targeting this problem
- Sell as subscription or service
- Use ads / outreach to find customers
"""
            ideas.append(idea)

    return ideas

def save_ideas(ideas):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(ideas))

    print("Ideas generated:", OUTPUT_PATH)

def run():
    data = load_data()
    ideas = generate_ideas(data)
    save_ideas(ideas)

if __name__ == "__main__":
    run()