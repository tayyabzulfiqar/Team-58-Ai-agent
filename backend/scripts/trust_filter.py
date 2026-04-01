import json

INPUT_PATH = "data/processed/trusted_data.json"
OUTPUT_PATH = "data/processed/high_signal_data.json"

THRESHOLD = 12  # adjustable

def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def filter_data(data):
    high_signal = []

    for item in data:
        if item.get("trust_score", 0) >= THRESHOLD:
            high_signal.append(item)

    return high_signal

def run():
    data = load_data()
    filtered = filter_data(data)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)

    print("High signal extraction complete")
    print(f"High quality signals: {len(filtered)}")

if __name__ == "__main__":
    run()