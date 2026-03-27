import json
import os
from collections import Counter

INPUT_PATH = "data/processed/trusted_data.json"
OUTPUT_PATH = "data/memory/memory.json"

# ✅ STOPWORDS
STOPWORDS = [
    "the","is","in","and","to","of","for","on","with",
    "this","that","your","data","says","are","was",
    "from","have","has","had","will","can","you",
    "about","into","over","after","before","between",
    "also","more","than","other","some","such"
]

# ✅ IMPORTANT WORD BOOST
IMPORTANT_KEYWORDS = [
    "ai","gpt","openai","automation","startup",
    "saas","agent","llm","machine","learning",
    "business","software","platform","tool"
]


def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_keywords(data):
    words = []

    for item in data:
        text = item.get("text", "").lower()

        for word in text.split():
            if (
                len(word) > 3
                and word not in STOPWORDS
                and word.isalpha()
            ):
                if word in IMPORTANT_KEYWORDS:
                    words.extend([word, word, word])  # 🔥 boost
                else:
                    words.append(word)

    return words


def build_memory(words):
    counter = Counter(words)
    memory = []

    for word, count in counter.items():
        if count >= 2:
            memory.append({
                "keyword": word,
                "frequency": count
            })

    return memory


def run():
    data = load_data()
    words = extract_keywords(data)
    memory = build_memory(words)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

    print("Memory updated")
    print(f"Total memory size: {len(memory)}")


if __name__ == "__main__":
    run()