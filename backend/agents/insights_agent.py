import json
import re
from datetime import datetime
from collections import Counter

from scripts.scoring_engine import HIGH_VALUE_OUTPUT_PATH, load_high_value_data

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

def deduplicate(records):
    seen = set()
    unique = []

    for record in records:
        text = record["text"]
        if text not in seen:
            seen.add(text)
            unique.append(record)

    return unique

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

def calculate_signal(text):
    length = len(text)
    keyword_weight = sum([
        5 if word in text else 0
        for word in ["ai", "startup", "saas", "automation"]
    ])
    return length + keyword_weight

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

def load_insights_input():
    data = load_high_value_data(HIGH_VALUE_OUTPUT_PATH)
    if not data:
        print(f"No high-value data found at {HIGH_VALUE_OUTPUT_PATH}")
    return data


def run(data=None):
    try:
        data = load_insights_input()
        processed = []

        for item in data:
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

            processed_item = {
                "text": cleaned_text,
                "source": item.get("source", "unknown"),
                "processed": True,
                "tags": tags,
                "score": signal_strength,
                "length": length,
                "word_count": word_count,
                "signal_strength": signal_strength,
                "processed_at": datetime.now().isoformat()
            }

            processed.append(processed_item)

        # 🔁 DEDUPLICATE
        processed = deduplicate(processed)

        # TRUST SCORING
        trusted = []
        for item in processed:
            trust_score = calculate_trust(item)
            item["trust_score"] = trust_score

            # FILTER
            if trust_score >= 5:
                trusted.append(item)

        # ANALYSIS
        tag_counts = analyze_tags(trusted)
        trends = calculate_trends(tag_counts)
        opportunities = detect_opportunities(trends)

        insights = {
            "processed_data": trusted,
            "trends": trends,
            "opportunities": opportunities,
            "generated_at": datetime.now().isoformat()
        }

        print("Insights processing complete")
        print(f"Processed records: {len(processed)}")
        print(f"Trusted records: {len(trusted)}")

        return insights

    except Exception as e:
        print("Insights Agent Error:", e)
        return {"processed_data": [], "trends": [], "opportunities": []}
