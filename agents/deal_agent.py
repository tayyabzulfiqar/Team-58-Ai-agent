from typing import Any, Dict, List

from scripts.intelligence_tools import best_content_type, estimate_roi, gather_search_context, summarize_search_text


BRAND_MAP = {
    "fashion": ["Ounass", "Level Shoes", "Namshi", "Faces", "Atlantis The Royal"],
    "music": ["Coca-Cola Arena", "Anghami", "Dubai Calendar", "Virgin Megastore", "Visit Dubai"],
    "film": ["VOX Cinemas", "MBC", "Dubai Tourism", "Emaar", "Atlantis Dubai"],
    "sports": ["GymNation", "Sun and Sand Sports", "PUMA Middle East", "Dubai Fitness Challenge", "Under Armour Middle East"],
    "creator": ["Noon", "Careem", "Talabat UAE", "Emaar", "Visit Dubai"],
    "comedy": ["Dubai Comedy Festival", "Noon", "Deliveroo UAE", "Virgin Radio Dubai", "Visit Dubai"],
}


def build_deal_ideas(celebrity_name: str, content_type: str, brands: List[str]) -> List[str]:
    offer_type = {
        "fashion": "luxury capsule + creator commerce rollout",
        "music": "event-led awareness surge + ticketing conversion push",
        "film": "premiere activation + tourism narrative campaign",
        "sports": "performance challenge + branded fitness funnel",
        "comedy": "short-form branded entertainment series",
        "creator": "social-first commerce sprint + lead capture offer",
    }.get(content_type, "social-first awareness and conversion campaign")

    return [f"{brand}: {celebrity_name} x Dubai {offer_type}" for brand in brands[:4]]


def build_outreach_message(celebrity_data: Dict[str, Any], brands: List[str]) -> str:
    name = celebrity_data.get("name", "our talent")
    top_content = celebrity_data.get("top_content", "creator content")
    audience = celebrity_data.get("audience", "global digital audience")
    market_fit = celebrity_data.get("market_fit", "Strong Dubai market fit")
    targets = ", ".join(brands[:3]) or "your brand"

    return (
        f"Hi team, we are packaging {name} for a Dubai-first brand growth sprint. "
        f"The talent is strongest in {top_content}, brings an audience profile of {audience}, and has clear commercial fit: {market_fit} "
        f"We believe {targets} can use this talent to win attention fast, generate social proof, and convert campaign momentum into measurable pipeline."
    )


def build_monetization_strategy(celebrity_data: Dict[str, Any], brands: List[str]) -> Dict[str, List[str] | str]:
    name = celebrity_data.get("name", "Talent")
    category = celebrity_data.get("top_content", "creator")
    return {
        "brand_deals": [
            f"{name} fronted hero campaign for {brands[0]} with 30-day amplification",
            f"Quarterly ambassador structure with {brands[1]} including paid media cutdowns",
        ],
        "affiliate_funnels": [
            f"Trackable creator landing page tied to {category} content drops",
            "Limited-time offer funnel driven by short-form content and remarketing",
        ],
        "lead_generation_strategy": (
            "Use gated VIP drops, waitlists, and high-intent remarketing audiences built from Reel viewers, "
            "site visitors, and brand-engaged followers."
        ),
    }


def build_pricing_tiers(celebrity_data: Dict[str, Any], roi_projection: Dict[str, str]) -> List[Dict[str, Any]]:
    name = celebrity_data.get("name", "Talent")
    return [
        {
            "tier": "Basic",
            "price": "$12,000",
            "deliverables": [f"4 short-form assets with {name}", "1 campaign concept", "1 outreach-ready brand package"],
            "expected_results": f"Reach up to {roi_projection.get('estimated_reach', '500,000')} with top-of-funnel traction.",
            "timeline": "14 days",
        },
        {
            "tier": "Pro",
            "price": "$25,000",
            "deliverables": ["8 short-form assets", "1 long-form hero cut", "brand outreach sequence", "paid amplification plan"],
            "expected_results": f"Drive {roi_projection.get('estimated_leads', '1,000-2,000')} qualified actions plus sponsor-ready proof.",
            "timeline": "30 days",
        },
        {
            "tier": "Premium",
            "price": "$45,000",
            "deliverables": ["12+ assets", "full 30-day content system", "deal sourcing", "reporting dashboard", "sales funnel integration"],
            "expected_results": f"Target {roi_projection.get('estimated_revenue', '$100,000-$200,000')} in attributable opportunity.",
            "timeline": "45 days",
        },
    ]


def run(celebrity_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        name = celebrity_data.get("name", "").strip()
        content_type = celebrity_data.get("top_content") or "creator"
        queries = [
            f"Dubai influencer campaigns {content_type}",
            f"Dubai brands celebrity partnerships {content_type}",
            f"{name} Dubai collaboration brand campaign",
        ]

        search_results = gather_search_context(queries, limit_per_query=4, scrape_top=2)
        search_text = summarize_search_text(search_results)
        inferred_type = best_content_type(search_text) if search_text else content_type
        target_brands = BRAND_MAP.get(inferred_type, BRAND_MAP["creator"])
        roi_projection = celebrity_data.get("roi_projection") or estimate_roi(
            int(celebrity_data.get("brand_alignment_score", 80)),
            int(celebrity_data.get("engagement_potential", 80)),
            int(celebrity_data.get("audience_size", 80)),
        )

        return {
            "target_brands": target_brands,
            "deal_ideas": build_deal_ideas(name or "Celebrity", inferred_type, target_brands),
            "outreach_message": build_outreach_message(celebrity_data, target_brands),
            "monetization_strategy": build_monetization_strategy(celebrity_data, target_brands),
            "roi_projection": roi_projection,
            "deal_structure": build_pricing_tiers(celebrity_data, roi_projection),
        }
    except Exception as exc:
        print("Deal Agent Error:", exc)
        fallback_brands = BRAND_MAP["creator"]
        roi_projection = estimate_roi(
            int(celebrity_data.get("brand_alignment_score", 80)),
            int(celebrity_data.get("engagement_potential", 80)),
            int(celebrity_data.get("audience_size", 80)),
        )
        return {
            "target_brands": fallback_brands,
            "deal_ideas": build_deal_ideas(celebrity_data.get("name", "Celebrity"), "creator", fallback_brands),
            "outreach_message": build_outreach_message(celebrity_data, fallback_brands),
            "monetization_strategy": build_monetization_strategy(celebrity_data, fallback_brands),
            "roi_projection": roi_projection,
            "deal_structure": build_pricing_tiers(celebrity_data, roi_projection),
        }
