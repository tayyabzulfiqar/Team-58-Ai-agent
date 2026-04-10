from collections import Counter

from core.input_utils import extract_query_text
from core.logging_utils import get_logger


logger = get_logger("team58.structuring")

AUDIENCE_PATTERNS = [
    ("enterprise saas", "Enterprise SaaS revenue teams"),
    ("saas", "SaaS growth teams"),
    ("b2b", "B2B commercial teams"),
    ("ecommerce", "Ecommerce marketing teams"),
    ("startup", "Startup go-to-market teams"),
]

TREND_RULES = {
    "AI-driven marketing": {"ai", "automation", "agent", "llm"},
    "Conversion optimization": {"conversion", "cro", "trial", "paid", "funnel"},
    "Personalization": {"personalization", "personalized", "segmentation"},
    "Product-led growth": {"trial", "onboarding", "activation", "product-led"},
    "Thought leadership": {"content", "authority", "education", "awareness"},
}

PAIN_POINT_RULES = {
    "High funnel drop-off": {"drop-off", "abandonment", "friction"},
    "Weak conversion efficiency": {"low conversion", "conversion rate", "trial-to-paid", "pipeline conversion"},
    "Rising acquisition cost": {"cac", "acquisition cost", "expensive", "roi"},
    "Poor lead quality": {"unqualified", "lead quality", "intent", "qualification"},
    "Crowded competitive market": {"competition", "competitive", "crowded"},
}

OPPORTUNITY_DEFINITIONS = [
    {
        "name": "Trial-to-paid conversion acceleration",
        "summary": "Improve onboarding, activation, and value proof to raise paid conversion rates.",
        "trend_triggers": {"Conversion optimization", "Product-led growth"},
        "pain_triggers": {"High funnel drop-off", "Weak conversion efficiency"},
    },
    {
        "name": "AI-assisted lead qualification",
        "summary": "Use intent signals and automation to qualify enterprise prospects earlier.",
        "trend_triggers": {"AI-driven marketing"},
        "pain_triggers": {"Poor lead quality", "Rising acquisition cost"},
    },
    {
        "name": "Proof-led enterprise demand capture",
        "summary": "Use benchmarks, case studies, and ROI proof to win enterprise pipeline.",
        "trend_triggers": {"Thought leadership", "Conversion optimization"},
        "pain_triggers": {"Crowded competitive market", "Weak conversion efficiency"},
    },
    {
        "name": "Brand visibility expansion",
        "summary": "Expand awareness and category visibility where buyers need education before conversion.",
        "trend_triggers": {"Thought leadership"},
        "pain_triggers": {"Crowded competitive market"},
    },
]

KNOWN_COMPETITORS = {
    "hubspot": "HubSpot",
    "salesforce": "Salesforce",
    "marketo": "Marketo",
    "apollo": "Apollo",
    "zoominfo": "ZoomInfo",
    "intercom": "Intercom",
    "drift": "Drift",
    "pipedrive": "Pipedrive",
    "outreach": "Outreach",
    "gong": "Gong",
}


def _collect_source_texts(data: dict) -> list[dict]:
    sources = data.get("sources", [])
    result = []
    for source in sources:
        text = " ".join(
            part for part in [source.get("title", ""), source.get("snippet", ""), source.get("content", "")]
            if part
        ).lower()
        result.append({"url": source.get("url"), "text": text})
    return result


def _match_labels(source_texts: list[dict], mapping: dict[str, set[str]]) -> tuple[list[str], dict[str, list[str]]]:
    selected = []
    support_map: dict[str, list[str]] = {}

    for label, keywords in mapping.items():
        supporting_urls = []
        for source in source_texts:
            if any(keyword in source["text"] for keyword in keywords):
                supporting_urls.append(source["url"])

        if supporting_urls:
            selected.append(label)
            support_map[label] = sorted(set(url for url in supporting_urls if url))

    return selected, support_map


def _infer_audience(query: str) -> str:
    lowered = query.lower()
    for pattern, audience in AUDIENCE_PATTERNS:
        if pattern in lowered:
            return audience
    return "Growth and marketing teams"


def _extract_competitors(source_texts: list[dict]) -> list[str]:
    competitors = []
    combined = " ".join(source["text"] for source in source_texts)
    for token, label in KNOWN_COMPETITORS.items():
        if token in combined:
            competitors.append(label)
    return competitors[:5]


def _build_opportunities(
    trends: list[str],
    pain_points: list[str],
    trend_support: dict[str, list[str]],
    pain_support: dict[str, list[str]],
) -> list[dict]:
    opportunities = []
    trend_set = set(trends)
    pain_set = set(pain_points)

    for definition in OPPORTUNITY_DEFINITIONS:
        if not (definition["trend_triggers"] & trend_set or definition["pain_triggers"] & pain_set):
            continue

        supporting_urls = set()
        for trend in definition["trend_triggers"] & trend_set:
            supporting_urls.update(trend_support.get(trend, []))
        for pain in definition["pain_triggers"] & pain_set:
            supporting_urls.update(pain_support.get(pain, []))

        opportunities.append(
            {
                "name": definition["name"],
                "summary": definition["summary"],
                "matched_trends": sorted(definition["trend_triggers"] & trend_set),
                "matched_pain_points": sorted(definition["pain_triggers"] & pain_set),
                "supporting_sources": sorted(supporting_urls),
            }
        )

    if not opportunities:
        opportunities.append(
            {
                "name": "Demand capture optimization",
                "summary": "Tighten lead capture and value messaging around the strongest buyer intent signals.",
                "matched_trends": trends[:2],
                "matched_pain_points": pain_points[:2],
                "supporting_sources": sorted(
                    {
                        url
                        for urls in list(trend_support.values())[:2] + list(pain_support.values())[:2]
                        for url in urls
                    }
                ),
            }
        )

    return opportunities


def structuring_tool(data: dict) -> dict:
    logger.info("structuring:start")
    query = extract_query_text({"query": data.get("query", "")})
    source_texts = _collect_source_texts(data)

    if not source_texts:
        raise RuntimeError("Structuring tool received zero source texts.")

    trends, trend_support = _match_labels(source_texts, TREND_RULES)
    pain_points, pain_support = _match_labels(source_texts, PAIN_POINT_RULES)
    competitors = _extract_competitors(source_texts)
    audience = _infer_audience(query)
    opportunities = _build_opportunities(trends, pain_points, trend_support, pain_support)

    result = {
        "audience": audience,
        "trends": trends,
        "competitors": competitors,
        "pain_points": pain_points,
        "opportunities": opportunities,
        "support": {
            "trends": trend_support,
            "pain_points": pain_support,
        },
    }
    logger.info("structuring:done opportunities=%s", len(opportunities))
    return result
