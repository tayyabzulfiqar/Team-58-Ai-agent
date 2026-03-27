import json
from collections import Counter

INPUT_PATH = "data/memory/memory.json"
OUTPUT_PATH = "data/processed/patterns.json"


def load_memory():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_patterns(memory):
    patterns = []

    keywords = [item.get("keyword", "").strip().lower() for item in memory if item.get("keyword")]

    relevance_set = set(["ai", "automation", "startup", "saas", "agent", "llm", "business", "software", "platform"])

    # create 2-word combinations with relevance filtering
    combos = []
    for i in range(len(keywords)):
        for j in range(i + 1, len(keywords)):
            w1 = keywords[i]
            w2 = keywords[j]
            if not w1 or not w2:
                continue
            combo = f"{w1} {w2}"
            if (w1 in relevance_set) or (w2 in relevance_set):
                combos.append(combo)

    counter = Counter(combos)

    # Prevent explosion; keep highest frequency top 50 patterns
    top = counter.most_common(50)

    for combo, count in top:
        patterns.append({
            "pattern": combo,
            "frequency": count
        })

    return patterns


def run():
    memory = load_memory()
    patterns = detect_patterns(memory)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(patterns, f, indent=2)

    print("Pattern detection complete")
    print(f"Patterns found: {len(patterns)}")


if __name__ == "__main__":
    run()