import sys

from agents.research_agent import search_serper
from agents.scraper_agent import scrape_multiple
from agents.pre_filter import pre_filter_results
from agents.scoring_engine import score_results
from agents.trust_engine import apply_trust_layer, classify_lead
from agents.diversity_engine import enforce_diversity

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run_pipeline(query):
    print("🔍 Searching...")
    urls = search_serper(query)

    print("🌐 Scraping...")
    raw_data = scrape_multiple(urls[:5])

    print("🧹 Hard Filter...")
    filtered_data, _ = pre_filter_results(raw_data)

    print("🧠 Scoring...")
    intent_analysis = {
        "intent_type": "transactional",
        "buyer_stage": "decision",
        "urgency": 3,
    }

    scored = score_results(filtered_data, query, intent_analysis)
    scored = [
        {**item, "discarded": item.get("intent_score", 0.0) < 0.35}
        for item in scored
        if item.get("intent_score", 0.0) >= 0.35
    ]

    print("🛡️ Trust Layer...")
    trusted = apply_trust_layer(scored, query)

    print("🌍 Diversity Layer...")
    final_results = enforce_diversity(
        sorted(
            [item for item in trusted if classify_lead(item) != "DISCARD"],
            key=lambda x: x["score"],
            reverse=True,
        ),
        limit=5,
    )

    return final_results


if __name__ == "__main__":
    query = "insurance sales training companies USA"
    results = run_pipeline(query)

    print("\n🔥 FINAL AI OUTPUT:\n")

    for item in results:
        print(f"Company: {item['entity']['company_name']}")
        print(f"Score: {item['score']}")
        print(f"Intent: {item['intent_type']}")
        print(f"Type: {item['content_type']}")
        print(f"Actionability: {item['actionability_score']}")
        print(f"Reason: {item['reason']}")
        print("-" * 60)
