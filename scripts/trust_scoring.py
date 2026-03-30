import json

INPUT_PATH = "data/processed/processed_data.json"
OUTPUT_PATH = "data/processed/trusted_data.json"


def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_trust(item):
    score = 0

    text = item.get("text", "").lower()
    source = item.get("source", "")

    # 1️⃣ Source reliability
    if source == "hackernews":
        score += 5
    elif source == "reddit":
        score += 3
    elif source == "searxng":
        score += 2

    # 2️⃣ Length quality
    if len(text) > 50:
        score += 3

    # 3️⃣ Keywords (signal strength)
    if any(word in text for word in ["ai", "startup", "automation", "gpt"]):
        score += 5

    # 4️⃣ Noise filter
    if any(word in text for word in ["buy now", "discount", "click here"]):
        score -= 5

    return score


def run():
    data = load_data()
    trusted = []

    for item in data:
        trust_score = calculate_trust(item)

        item["trust_score"] = trust_score

        # FILTER (IMPORTANT)
        if trust_score >= 5:
            trusted.append(item)

    import os
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(trusted, f, indent=2)

    print(f"Trust scoring complete")
    print(f"Total input: {len(data)}")
    print(f"Trusted data: {len(trusted)}")


if __name__ == "__main__":
    run()