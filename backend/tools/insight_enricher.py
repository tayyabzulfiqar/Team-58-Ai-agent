from __future__ import annotations

from typing import Any, Dict, List, Tuple


_BANNED_PHRASES = (
    "week 1",
    "week 2",
    "optimize funnel",
    "improve conversion",
)


def _as_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _clamp(n: int) -> int:
    return max(0, min(100, int(n)))


def _contains_any(text: str, terms: List[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


def _detect_context(query: str) -> str:
    q = query.lower()
    if _contains_any(q, ["saas", "subscription", "trial", "onboarding", "activation"]):
        return "saas_activation"
    if _contains_any(q, ["ecommerce", "e-commerce", "checkout", "cart", "shopify", "store"]):
        return "ecommerce_conversion"
    if _contains_any(q, ["gym", "clinic", "salon", "restaurant", "local business", "studio"]):
        return "local_retention"
    if _contains_any(q, ["agency", "client acquisition", "leads", "lead generation", "cac"]):
        return "agency_leads"
    if _contains_any(q, ["app", "mobile app", "engagement", "daily active", "dau"]):
        return "app_engagement"
    return "general_business"


def _strip_generic_text(text: str) -> str:
    clean = _as_str(text)
    low = clean.lower()
    if any(b in low for b in _BANNED_PHRASES):
        return ""
    return clean


def _filter_list(items: Any) -> List[str]:
    out: List[str] = []
    for item in _as_list(items):
        if not isinstance(item, str):
            continue
        clean = _strip_generic_text(item)
        if clean:
            out.append(clean)
    return out


def _context_reasoning(context: str, query: str) -> Dict[str, str]:
    if context == "saas_activation":
        return {
            "analysis": (
                f"Sign-ups are happening, but activation is weak. Input context: {query}. "
                "Users are likely reaching account creation without reaching first value."
            ),
            "why_this_problem": (
                "The onboarding sequence delays the first meaningful outcome, so users do not connect setup effort "
                "to business ROI. Pricing may appear before value proof, increasing hesitation."
            ),
            "impact_explanation": (
                "Without activation-first onboarding, paid acquisition efficiency drops, trial cohorts decay quickly, "
                "and expansion revenue stalls because retention starts weak from day one."
            ),
        }
    if context == "ecommerce_conversion":
        return {
            "analysis": (
                f"Purchase intent exists but conversion leaks near checkout. Input context: {query}. "
                "The likely break is trust, cost visibility, or payment friction."
            ),
            "why_this_problem": (
                "Users hesitate when final price, shipping, or policy confidence becomes ambiguous at decision time. "
                "If trust signals are weak, even high-intent sessions fail to complete."
            ),
            "impact_explanation": (
                "Conversion leakage at checkout inflates CAC per order and compresses contribution margin despite steady traffic."
            ),
        }
    if context == "local_retention":
        return {
            "analysis": (
                f"Retention is the core issue. Input context: {query}. "
                "Customers are not forming a repeat-visit habit after initial signup."
            ),
            "why_this_problem": (
                "The service experience likely lacks a clear habit loop: predictable cadence, visible progress, "
                "and fast re-engagement after missed visits."
            ),
            "impact_explanation": (
                "When repeat visits decline, lifetime value drops and acquisition spend must replace churn, reducing net growth."
            ),
        }
    if context == "agency_leads":
        return {
            "analysis": (
                f"Lead flow may be broad but not qualified. Input context: {query}. "
                "Pipeline quality appears weaker than top-of-funnel volume."
            ),
            "why_this_problem": (
                "Positioning and offer framing may attract low-intent audiences, increasing sales-cycle friction and CAC."
            ),
            "impact_explanation": (
                "If qualification stays weak, close rates remain unstable and delivery capacity is consumed by poor-fit prospects."
            ),
        }
    if context == "app_engagement":
        return {
            "analysis": (
                f"Engagement is likely shallow beyond first sessions. Input context: {query}. "
                "Users may complete basic exploration without forming repeat usage."
            ),
            "why_this_problem": (
                "Core product moments may not be frequent or rewarding enough to build routine behavior."
            ),
            "impact_explanation": (
                "Low engagement lowers retention and monetization efficiency, limiting revenue growth even with healthy installs."
            ),
        }
    return {
        "analysis": f"Observed business challenge: {query}.",
        "why_this_problem": "Signals suggest value communication and execution sequencing are misaligned with user decision moments.",
        "impact_explanation": "If unresolved, conversion efficiency and customer lifetime value both degrade over time.",
    }


def _scoring(context: str, query: str, raw: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, int]:
    q = query.lower()
    severity = 55
    opportunity = 60
    confidence = 58

    if context in ("saas_activation", "ecommerce_conversion", "local_retention"):
        severity += 20
        opportunity += 15

    if _contains_any(q, ["never convert", "don't convert", "struggling", "drop", "churn", "retention"]):
        severity += 10

    if _contains_any(q, ["onboarding", "pricing", "retention", "checkout", "activation"]):
        opportunity += 8

    signal_count = 0
    signal_count += len(_as_list(raw.get("actions")))
    signal_count += len(_as_list(raw.get("root_causes")))
    signal_count += len(_as_list(raw.get("research")))
    signal_count += len(_as_list(report.get("strategy", {}).get("points") if isinstance(report.get("strategy"), dict) else []))

    if signal_count >= 6:
        confidence += 20
    elif signal_count >= 3:
        confidence += 10
    else:
        confidence -= 6

    return {
        "severity": _clamp(severity),
        "opportunity": _clamp(opportunity),
        "confidence": _clamp(confidence),
    }


def _big_opportunity(context: str) -> Dict[str, str]:
    if context == "saas_activation":
        return {
            "title": "Close the activation-to-payment gap in the first session",
            "impact": "Users who reach first value faster are materially more likely to upgrade and stay retained.",
            "estimated_uplift": "25-40%",
        }
    if context == "ecommerce_conversion":
        return {
            "title": "Remove checkout trust and payment friction",
            "impact": "Resolving last-step hesitation captures existing purchase intent without increasing traffic spend.",
            "estimated_uplift": "15-30%",
        }
    if context == "local_retention":
        return {
            "title": "Build a repeat-visit habit loop for members",
            "impact": "Structured habit-building and recovery after missed visits increases renewal stability.",
            "estimated_uplift": "20-35%",
        }
    if context == "agency_leads":
        return {
            "title": "Improve qualification before sales handoff",
            "impact": "Higher lead fit reduces CAC waste and improves close rates with existing pipeline volume.",
            "estimated_uplift": "15-28%",
        }
    if context == "app_engagement":
        return {
            "title": "Design for recurring product moments",
            "impact": "Increasing repeat usage raises retention and creates stronger monetization windows.",
            "estimated_uplift": "18-32%",
        }
    return {
        "title": "Align value communication with user decision moments",
        "impact": "Clear problem-to-value mapping improves conversion consistency across the funnel.",
        "estimated_uplift": "10-22%",
    }


def _action_reason(context: str, title: str, idx: int) -> str:
    if context == "saas_activation":
        reasons = [
            "Users drop before they experience the product's core outcome.",
            "Early proof of value is required before presenting pricing decisions.",
            "Lifecycle nudges should react to user friction points, not generic timing.",
            "Retention improves when onboarding outcomes tie to customer business goals.",
        ]
        return reasons[idx] if idx < len(reasons) else "This step reduces activation friction and lifts paid conversion."
    if context == "local_retention":
        reasons = [
            "Retention improves when members follow a consistent habit loop.",
            "Progress visibility increases motivation for repeat visits.",
            "Recovery flows reduce churn after missed sessions.",
            "Structured feedback reveals fixable reasons behind cancellations.",
        ]
        return reasons[idx] if idx < len(reasons) else "This step increases repeat visits and renewal probability."
    if context == "ecommerce_conversion":
        reasons = [
            "Trust and cost clarity remove final-stage hesitation.",
            "Lower checkout friction improves completion rate with existing demand.",
            "Payment flexibility captures users with different preferences.",
            "Decision certainty at checkout drives immediate revenue lift.",
        ]
        return reasons[idx] if idx < len(reasons) else "This step removes blockers between intent and payment."
    return "This step addresses a core conversion bottleneck tied to observed behavior."


def _enrich_action_plan(context: str, report: Dict[str, Any], scoring: Dict[str, int]) -> List[Dict[str, Any]]:
    plan_raw = _as_list(report.get("action_plan"))
    out: List[Dict[str, Any]] = []
    base = scoring.get("opportunity", 60)
    for idx, step in enumerate(plan_raw):
        if not isinstance(step, dict):
            continue
        title = _strip_generic_text(_as_str(step.get("title")))
        if not title:
            continue
        impact = step.get("impact_score")
        if not isinstance(impact, int):
            impact = _clamp(base + max(0, 15 - idx * 4))
        out.append(
            {
                "step": idx + 1,
                "title": title,
                "timeline": _as_str(step.get("timeline")),
                "impact_score": _clamp(impact),
                "reason": _action_reason(context, title, idx),
            }
        )
    return out


def _remove_generic_from_report(report: Dict[str, Any]) -> Dict[str, Any]:
    report["main_problem"] = _strip_generic_text(_as_str(report.get("main_problem")))
    report["key_insight"] = _strip_generic_text(_as_str(report.get("key_insight")))
    report["whats_happening"] = _filter_list(report.get("whats_happening"))
    report["root_causes"] = _filter_list(report.get("root_causes"))
    strategy = report.get("strategy")
    if isinstance(strategy, dict):
        strategy["points"] = _filter_list(strategy.get("points"))
        report["strategy"] = strategy
    return report


def enrich_insights(query: str, raw: dict, report: dict) -> dict:
    """
    Takes:
    - user query
    - raw pipeline output
    - generated report

    Returns:
    - enhanced report with deep intelligence
    """
    q = _as_str(query)
    safe_raw = raw if isinstance(raw, dict) else {}
    safe_report = report.copy() if isinstance(report, dict) else {}

    context = _detect_context(q)
    reasoning = _context_reasoning(context, q)
    scoring = _scoring(context, q, safe_raw, safe_report)
    opportunity = _big_opportunity(context)

    safe_report = _remove_generic_from_report(safe_report)
    safe_report["reasoning"] = reasoning
    safe_report["scoring"] = scoring
    safe_report["big_opportunity"] = opportunity
    safe_report["action_plan"] = _enrich_action_plan(context, safe_report, scoring)
    safe_report["confidence_score"] = scoring.get("confidence", safe_report.get("confidence_score", 0))
    safe_report["context"] = context

    # Ensure no banned phrases remain in action plan reasons/titles.
    cleaned_plan: List[Dict[str, Any]] = []
    for item in _as_list(safe_report.get("action_plan")):
        if not isinstance(item, dict):
            continue
        title = _strip_generic_text(_as_str(item.get("title")))
        reason = _strip_generic_text(_as_str(item.get("reason")))
        if not title:
            continue
        item["title"] = title
        item["reason"] = reason
        cleaned_plan.append(item)
    safe_report["action_plan"] = cleaned_plan

    return safe_report

