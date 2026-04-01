from typing import Any, Dict, List


def join_lines(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def format_content_angles(angles: List[Dict[str, str]]) -> str:
    if not angles:
        return "- No content angles available."
    lines = []
    for angle in angles:
        lines.append(
            f"- Hook: {angle.get('hook', 'N/A')} | Reel: {angle.get('reel_idea', 'N/A')} | Format: {angle.get('viral_format', 'N/A')}"
        )
    return "\n".join(lines)


def format_platform_focus(platform_focus: Dict[str, str]) -> str:
    if not isinstance(platform_focus, dict):
        return str(platform_focus)
    return "\n".join(f"- {platform}: {strategy}" for platform, strategy in platform_focus.items())


def format_schedule(schedule: Any) -> str:
    if isinstance(schedule, dict):
        return "\n".join(f"- {platform}: {plan}" for platform, plan in schedule.items())
    if isinstance(schedule, list):
        return join_lines([str(item) for item in schedule])
    return str(schedule)


def format_deal_structure(tiers: List[Dict[str, Any]]) -> str:
    blocks = []
    for tier in tiers:
        deliverables = ", ".join(tier.get("deliverables", []))
        blocks.append(
            f"- {tier.get('tier', 'Tier')} | {tier.get('price', 'N/A')} | Deliverables: {deliverables} | "
            f"Results: {tier.get('expected_results', 'N/A')} | Timeline: {tier.get('timeline', 'N/A')}"
        )
    return "\n".join(blocks)


def build_celebrity_section(entry: Dict[str, Any]) -> str:
    celebrity = entry["celebrity_data"]
    growth = entry["growth_plan"]
    deal = entry["deal_data"]
    campaigns = entry.get("campaigns", [])
    audience_breakdown = celebrity.get("audience_breakdown", {})
    monetization = deal.get("monetization_strategy", {})
    roi = deal.get("roi_projection", {})
    campaign_summary = campaigns[0] if campaigns else {}

    return f"""
## {celebrity.get('name', 'Celebrity')}

### Executive Snapshot
{celebrity.get('research_summary', 'No summary available.')}

### Ranking Score
- Engagement Potential: {celebrity.get('engagement_potential', 'N/A')}/100
- Audience Size: {celebrity.get('audience_size', 'N/A')}/100
- Virality Probability: {celebrity.get('virality_probability', 'N/A')}/100
- Brand Alignment: {celebrity.get('brand_alignment_score', 'N/A')}/100
- Composite Score: {celebrity.get('ranking_score', 'N/A')}/100

### Audience Breakdown
- Geography: {audience_breakdown.get('geo', 'N/A')}
- Age: {audience_breakdown.get('age', 'N/A')}
- Interests: {", ".join(audience_breakdown.get('interests', []))}

### Content Angles
{format_content_angles(celebrity.get('content_angles', []))}

### Growth Strategy
{growth.get('growth_plan', 'N/A')}

### Platform Focus
{format_platform_focus(growth.get('platform_focus', {}))}

### 30-Day Execution Roadmap
{format_schedule(growth.get('campaign_plan_30_day', []))}

### Campaign Plan
- Idea: {campaign_summary.get('idea', 'N/A')}
- Hook: {campaign_summary.get('hook', 'N/A')}
- Platform: {campaign_summary.get('platform', 'N/A')}
- Posting Time: {campaign_summary.get('posting_time', 'N/A')}

### Monetization Strategy
- Brand Deals: {", ".join(monetization.get('brand_deals', []))}
- Affiliate Funnels: {", ".join(monetization.get('affiliate_funnels', []))}
- Lead Generation: {monetization.get('lead_generation_strategy', 'N/A')}

### ROI Projection
- Estimated Reach: {roi.get('estimated_reach', 'N/A')}
- Estimated Leads: {roi.get('estimated_leads', 'N/A')}
- Estimated Revenue: {roi.get('estimated_revenue', 'N/A')}
- Projected ROAS: {roi.get('projected_roas', 'N/A')}

### Deal Structure
{format_deal_structure(deal.get('deal_structure', []))}

### Target Brands
{join_lines(deal.get('target_brands', []))}

### Outreach Message
{deal.get('outreach_message', 'N/A')}
""".strip()


def build_final_report(top_celebrities: List[Dict[str, Any]], insights: Dict[str, Any], strategies: List[Dict[str, Any]]) -> str:
    summary_lines = [
        "# TEAM 58 Celebrity Growth Intelligence Report",
        "",
        "Prepared as a client-ready growth strategy document for Dubai-focused celebrity partnerships, monetization, and campaign execution.",
        "",
        "## Executive Brief",
        "- Objective: Identify the three highest-upside celebrity assets for fast brand growth in Dubai.",
        "- Method: Blend trend intelligence, celebrity scoring, audience relevance, campaign fit, and monetization upside.",
        "- Output: A tactical 30-day plan, monetization model, deal structure, and ROI view for each selected talent.",
        "",
        "## Market Context",
        f"- Insight trends tracked: {', '.join(item.get('trend', 'general') for item in insights.get('trends', [])[:5]) or 'general demand patterns'}",
        f"- Strategy hooks available: {' | '.join(item.get('marketing_hook', item.get('solution', 'growth angle')) for item in strategies[:5]) or 'premium positioning and conversion-led messaging'}",
        "",
        "## Top 3 Opportunities",
    ]

    sections = [build_celebrity_section(entry) for entry in top_celebrities]
    return "\n\n".join(summary_lines + sections)
