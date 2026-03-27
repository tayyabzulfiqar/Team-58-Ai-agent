import json
import os
import re
from datetime import datetime

# Paths
RAW_PATH = "data/raw/raw_data.json"
PROCESSED_PATH = "data/processed/processed_data.json"


# -------------------------------
# 🧹 CLEANING FUNCTION
# -------------------------------
def clean_text(text):
    if not text or not isinstance(text, str):
        return None

    # Trim + normalize spaces
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    # Lowercase
    text = text.lower()

    # Remove excessive punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Remove non-ascii (optional)
    text = text.encode("ascii", "ignore").decode()

    # Filter low signal
    if len(text) < 10:
        return None

    return text


# -------------------------------
# 🔁 DEDUPLICATION
# -------------------------------
def deduplicate(records):
    seen = set()
    unique = []

    for record in records:
        text = record["text"]
        if text not in seen:
            seen.add(text)
            unique.append(record)

    return unique


# -------------------------------
# 🏷 TAGGING ENGINE
# -------------------------------
def generate_tags(text):
    tags = []

    if any(word in text for word in ["ai", "gpt", "llm"]):
        tags.append("AI")

    if any(word in text for word in ["startup", "funding", "founder"]):
        tags.append("Startup")

    if any(word in text for word in ["saas", "subscription"]):
        tags.append("SaaS")

    if any(word in text for word in ["automation", "agent"]):
        tags.append("Automation")

    if not tags:
        tags.append("General")

    return tags


# -------------------------------
# 📊 SIGNAL STRENGTH
# -------------------------------
def calculate_signal(text):
    length = len(text)
    keyword_weight = sum([
        5 if word in text else 0
        for word in ["ai", "startup", "saas", "automation"]
    ])
    return length + keyword_weight


# -------------------------------
# 🚀 MAIN PROCESSOR
# -------------------------------
def process_data():
    # Load raw data
    if not os.path.exists(RAW_PATH):
        print("❌ Raw data file not found")
        return

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed = []

    for item in raw_data:
        text = item.get("text")

        # 🧹 CLEAN
        cleaned_text = clean_text(text)
        if not cleaned_text:
            continue

        # 🏷 TAGS
        tags = generate_tags(cleaned_text)

        # 📊 METRICS
        length = len(cleaned_text)
        word_count = len(cleaned_text.split())
        signal_strength = calculate_signal(cleaned_text)

        processed.append({
            "text": cleaned_text,
            "source": item.get("source", "unknown"),
            "cleaned": True,
            "length": length,
            "word_count": word_count,
            "tags": tags,
            "signal_strength": signal_strength,
            "processed_at": datetime.utcnow().isoformat()
        })

    # 🔁 DEDUPLICATE
    processed = deduplicate(processed)

    # Ensure output folder exists
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)

    # Save processed data
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    # ✅ VALIDATION OUTPUT
    print("Processing Complete")
    print(f"Total Records: {len(processed)}")


# -------------------------------
# ▶️ EXECUTE
# -------------------------------
if __name__ == "__main__":
    process_data()