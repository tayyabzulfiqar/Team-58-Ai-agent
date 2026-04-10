from core.guarded_pipeline import run_guarded_pipeline
from core.input_utils import extract_query_text
from core.logging_utils import get_logger
from agents.research_agent import ResearchAgent
from agents.campaign_agent import CampaignAgent
from tools.cleaner_tool import cleaner_tool
from tools.decision_tool import decision_tool
from tools.execution_tool import execution_tool
from tools.objective_detector import detect_objective
from tools.reasoning_tool import reasoning_tool
from tools.scoring_tool import scoring_tool
from tools.structuring_tool import structuring_tool
from tools.validation_tool import validation_tool


logger = get_logger("team58.orchestrator")


def _signal_from_pipeline(base_pipeline: dict) -> str:
    primary = str(base_pipeline.get("primary_signal") or "").strip().lower()
    if primary in {"conversion optimization", "retention", "paid ads", "lead generation"}:
        return primary
    # Fallback based on any ranked signals
    signals = list(base_pipeline.get("signals") or [])
    for item in signals:
        name = str(item.get("name") or "").strip().lower()
        if name in {"conversion optimization", "retention", "paid ads", "lead generation"}:
            return name
    return "conversion optimization"


def _fallback_research_insights(query: str, primary_signal: str) -> list[str]:
    text = str(query or "").lower()
    insights: list[str] = []

    # Generic but still causal and deterministic, grounded in common failure modes.
    if primary_signal == "conversion optimization":
        insights.extend(
            [
                "Visitors are arriving but not taking purchase action, indicating decision-stage friction",
                "Value or pricing clarity is likely insufficient to justify the purchase",
                "Trust proof is likely weak (reviews, guarantees, social proof), reducing checkout confidence",
            ]
        )
        if any(t in text for t in ("pricing", "price", "expensive", "cheap")):
            insights.insert(1, "Pricing/value mismatch is implied, which often prevents checkout completion")
        if any(t in text for t in ("checkout", "payment", "cart", "steps", "abandon")):
            insights.insert(0, "Checkout friction is implied, which commonly causes last-step drop-off")

    elif primary_signal == "retention":
        insights.extend(
            [
                "Users drop after first use, indicating weak activation and habit formation",
                "Onboarding likely fails to deliver early value fast enough to earn repeat usage",
                "Lifecycle re-engagement triggers likely are missing or poorly timed",
            ]
        )

    elif primary_signal == "paid ads":
        insights.extend(
            [
                "Paid traffic quality is likely misaligned with buyer intent, reducing ROI",
                "Targeting and creative-message fit likely drifted, causing expensive low-quality clicks",
                "Budget likely concentrates on low-efficiency segments without conversion feedback loops",
            ]
        )
        if any(t in text for t in ("cpc", "cost", "expensive")):
            insights.insert(0, "Rising cost signals point to bidding/targeting inefficiency, not just creative issues")
        if any(t in text for t in ("roi", "roas", "return")):
            insights.insert(1, "Low returns imply post-click conversion quality issues or poor segment mix")

    else:  # lead generation
        insights.extend(
            [
                "Top-funnel visibility is likely low, limiting qualified traffic volume",
                "Channel mix may not reach high-intent audiences consistently",
                "Positioning/message may be too broad to attract intent-aligned visitors",
            ]
        )

    # Ensure minimum 3 insights always.
    deduped: list[str] = []
    seen = set()
    for item in insights:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return (deduped + ["Funnel friction exists and must be isolated to one dominant bottleneck"])[:5]


def _fallback_root_causes(primary_signal: str) -> list[str]:
    if primary_signal == "conversion optimization":
        return [
            "Checkout and decision-stage friction prevents completion",
            "Offer/value proof is not strong enough to justify purchase",
            "Trust signals are insufficient to reduce perceived risk",
        ]
    if primary_signal == "retention":
        return [
            "Onboarding fails to deliver early value and activation",
            "Product habit loop is weak, causing drop after first use",
            "Re-engagement system is missing or ineffective",
        ]
    if primary_signal == "paid ads":
        return [
            "Targeting is misaligned with conversion intent",
            "Creative-message mismatch reduces post-click quality",
            "Budget allocation favors low-efficiency segments",
        ]
    return [
        "Low top-funnel visibility limits qualified traffic",
        "Channels are not reaching high-intent audiences consistently",
        "Positioning is too broad to attract qualified demand",
    ]


def _fallback_campaign_plan(primary_signal: str) -> list[str]:
    if primary_signal == "conversion optimization":
        return [
            "Instrument landing-to-checkout funnel drop-off by step",
            "Fix the single biggest abandonment point first",
            "Align ad message to landing offer and proof",
            "Run one controlled conversion test (headline/offer/CTA)",
        ]
    if primary_signal == "retention":
        return [
            "Map first-session activation milestones and completion rate",
            "Fix onboarding step with highest drop-off",
            "Launch reactivation triggers for inactive users (day 1–7)",
            "Measure repeat usage by cohort and iterate weekly",
        ]
    if primary_signal == "paid ads":
        return [
            "Cut waste: pause low-ROI segments and tighten targeting",
            "Refresh creatives to match buyer intent and landing promise",
            "Rebuild tracking toward conversion-quality events (not CTR)",
            "Scale only after ROI stabilizes across cohorts",
        ]
    return [
        "Pick one primary channel and validate traffic quality for 2 weeks",
        "Tighten positioning and intent keywords for that channel",
        "Create one high-intent landing/lead magnet for capture",
        "Review weekly and expand to second channel after baseline",
    ]


def _fallback_suggestions(primary_signal: str) -> list[dict]:
    if primary_signal == "conversion optimization":
        return [
            {
                "headline": "Turn More Visitors Into Buyers Without More Ad Spend",
                "hook": "Fix the one conversion bottleneck causing drop-off before purchase.",
                "cta": "Get the Conversion Fix Plan",
            }
        ]
    if primary_signal == "retention":
        return [
            {
                "headline": "Stop One-Time Users From Disappearing After Day One",
                "hook": "Improve onboarding and reactivation so users return and stick.",
                "cta": "Audit My Retention Loop",
            }
        ]
    if primary_signal == "paid ads":
        return [
            {
                "headline": "Reduce Wasted Spend and Recover ROI From Your Ads",
                "hook": "Tighten targeting and message fit so clicks turn into revenue.",
                "cta": "Fix My Paid Performance",
            }
        ]
    return [
        {
            "headline": "Build Qualified Traffic Before You Optimize Conversion",
            "hook": "Validate one channel and one message that pulls high-intent visitors.",
            "cta": "Launch My Demand Sprint",
        }
    ]


def _clamp_confidence(value: float) -> float:
    try:
        v = float(value)
    except Exception:
        v = 0.8
    return round(max(0.7, min(0.95, v)), 3)


def run_system(input_data):
    query = extract_query_text(input_data)
    logger.info("system:start query=%s", query)

    research_data = None
    try:
        research_data = ResearchAgent().run({"query": query})
    except Exception as exc:
        # Failsafe: do not block production flow on research failures.
        logger.warning("system:research-failed query=%s error=%s", query, exc)
        research_data = None

    # Always run the existing pipeline (and pass research if available).
    base_pipeline = run_guarded_pipeline(query, research_data=research_data)

    # Always build a product-level envelope from the base pipeline (deterministic, fast).
    base_main_problem = base_pipeline.get("status_reason") or base_pipeline.get("reasoning") or "Business performance issue detected"
    primary_signal = _signal_from_pipeline(base_pipeline)
    base_root_causes = list(base_pipeline.get("root_causes") or [])[:3] or _fallback_root_causes(primary_signal)
    agent_flow_trace = [{"step": "base_pipeline", "status": "ok"}]
    base_plan = [str(item.get("action", "")) for item in list(base_pipeline.get("actions") or []) if isinstance(item, dict) and item.get("action")]
    base_suggestions = []
    try:
        # CampaignAgent can still run without research; keep it fed with safe defaults.
        objective = detect_objective(query)
        agent_flow_trace.append({"step": "campaign_agent_fallback", "status": "start"})
        campaign_payload = CampaignAgent().run(
            {
                "original_input": query,
                "objective": objective,
                "analysis": {"best_strategy": "Performance marketing"},
                "structured_intelligence": {},
                "scored_opportunities": {},
                "validation": {},
                "reasoning": {},
                "research": {},
            }
        )
        agent_flow_trace[-1]["status"] = "ok"
        timeline = list((campaign_payload.get("execution_plan") or {}).get("timeline") or [])
        if timeline:
            base_plan = timeline
        best = campaign_payload.get("best_campaign") or {}
        if best:
            base_suggestions = [
                {"headline": best.get("headline", ""), "hook": best.get("hook", ""), "cta": best.get("cta", "")}
            ]
    except Exception:
        if agent_flow_trace and agent_flow_trace[-1].get("step") == "campaign_agent_fallback":
            agent_flow_trace[-1]["status"] = "failed"
        pass

    product_output = {
        "main_problem": base_main_problem,
        "research": list(base_pipeline.get("research_insights") or [])[:5],
        "insights": str(base_pipeline.get("reasoning") or "").strip(),
        "strategy": {
            "root_causes": base_root_causes[:3],
            "reasoning": str(base_pipeline.get("reasoning") or "").strip(),
        },
        "campaign": {
            "plan": base_plan[:5] if base_plan else _fallback_campaign_plan(primary_signal),
            "suggestions": base_suggestions or _fallback_suggestions(primary_signal),
        },
        "confidence": _clamp_confidence(base_pipeline.get("confidence") or 0.8),
    }

    # Enforce minimum "product completeness" in fallback mode (no empty sections).
    if not product_output["research"] or len(product_output["research"]) < 3:
        product_output["research"] = _fallback_research_insights(query, primary_signal)[:3]
    else:
        product_output["research"] = product_output["research"][:3]

    if not product_output["insights"]:
        product_output["insights"] = f"Primary bottleneck is '{primary_signal}': users are not progressing cleanly through the journey, so revenue efficiency is constrained."

    if not product_output["strategy"]["root_causes"] or len(product_output["strategy"]["root_causes"]) < 3:
        product_output["strategy"]["root_causes"] = _fallback_root_causes(primary_signal)[:3]
    if not product_output["strategy"]["reasoning"]:
        product_output["strategy"]["reasoning"] = f"Focus on '{primary_signal}' first because it is the highest-impact bottleneck implied by the input."

    if not product_output["campaign"]["plan"] or len(product_output["campaign"]["plan"]) < 3:
        product_output["campaign"]["plan"] = _fallback_campaign_plan(primary_signal)[:4]
    product_output["campaign"]["plan"] = product_output["campaign"]["plan"][:5]

    if not product_output["campaign"]["suggestions"]:
        product_output["campaign"]["suggestions"] = _fallback_suggestions(primary_signal)

    # Attempt the full agentic flow; if any step fails, keep the base product envelope.
    try:
        agent_flow_trace.append({"step": "research", "status": "ok" if research_data else "failed"})
        if not research_data:
            raise RuntimeError("research_unavailable")

        agent_flow_trace.append({"step": "cleaner", "status": "start"})
        cleaned = cleaner_tool(research_data)
        agent_flow_trace[-1]["status"] = "ok"

        agent_flow_trace.append({"step": "structuring", "status": "start"})
        structured_intelligence = structuring_tool(cleaned)
        agent_flow_trace[-1]["status"] = "ok"

        agent_flow_trace.append({"step": "scoring", "status": "start"})
        scored_opportunities = scoring_tool(structured_intelligence)
        agent_flow_trace[-1]["status"] = "ok"

        agent_flow_trace.append({"step": "validation", "status": "start"})
        validated_opportunities = validation_tool(scored_opportunities)
        agent_flow_trace[-1]["status"] = "ok"

        objective = detect_objective(query)
        strategy_input = {
            "objective": objective,
            "analysis": {},
            "structured_intelligence": structured_intelligence,
            "scored_opportunities": scored_opportunities,
            "validation": validated_opportunities,
        }

        agent_flow_trace.append({"step": "decision", "status": "start"})
        decision = decision_tool(strategy_input, original_input=query)
        agent_flow_trace[-1]["status"] = "ok"

        agent_flow_trace.append({"step": "reasoning_llm", "status": "start"})
        llm_reasoning_payload = {}
        try:
            llm_reasoning_payload = reasoning_tool(strategy_input)
            agent_flow_trace[-1]["status"] = "ok"
        except Exception as exc:
            agent_flow_trace[-1]["status"] = "skipped"
            agent_flow_trace[-1]["error"] = str(exc)

        agent_flow_trace.append({"step": "execution_plan", "status": "start"})
        budget_tier = decision.get("decision_inputs", {}).get("budget_tier", "medium")
        execution_plan = execution_tool(decision, structured_intelligence, validated_opportunities, budget_tier)
        agent_flow_trace[-1]["status"] = "ok"

        agent_flow_trace.append({"step": "campaign_agent", "status": "start"})
        campaign_payload = CampaignAgent().run(
            {
                "original_input": query,
                "objective": objective,
                "analysis": {"best_strategy": decision.get("selected_strategy")},
                "structured_intelligence": structured_intelligence,
                "scored_opportunities": scored_opportunities,
                "validation": validated_opportunities,
                "reasoning": llm_reasoning_payload,
                "research": research_data,
            }
        )
        agent_flow_trace[-1]["status"] = "ok"

        # Product-level structured output (stable shape).
        main_problem = base_pipeline.get("status_reason") or base_pipeline.get("reasoning") or "Business performance issue detected"
        research_insights = list(base_pipeline.get("research_insights") or [])
        if not research_insights:
            research_insights = []
        research_list = research_insights[:2]
        if not research_list:
            top_opp = (validated_opportunities.get("validated_opportunities") or [{}])[0]
            if top_opp.get("name"):
                research_list = [f"Top opportunity from sources: {top_opp.get('name')}"]

        root_causes = list(base_pipeline.get("root_causes") or [])
        if len(root_causes) < 3:
            pain_points = list(structured_intelligence.get("pain_points") or [])
            for p in pain_points:
                if len(root_causes) >= 3:
                    break
                root_causes.append(p)
        root_causes = root_causes[:3]

        reasoning_text = decision.get("reason") or base_pipeline.get("reasoning") or ""
        if llm_reasoning_payload.get("llm_reasoning"):
            reasoning_text = f"{reasoning_text} {llm_reasoning_payload.get('llm_reasoning')}".strip()

        plan = list(execution_plan.get("timeline") or [])
        suggestions = []
        best = campaign_payload.get("best_campaign") or {}
        if best:
            suggestions.append(
                {
                    "headline": best.get("headline", ""),
                    "hook": best.get("hook", ""),
                    "cta": best.get("cta", ""),
                }
            )

        product_output = {
            "main_problem": main_problem,
            "research": (research_list + _fallback_research_insights(query, primary_signal))[:3],
            "insights": ", ".join(list(structured_intelligence.get("pain_points") or [])[:3]) or "",
            "strategy": {
                "root_causes": root_causes,
                "reasoning": reasoning_text,
            },
            "campaign": {
                "plan": plan[:5] if plan else _fallback_campaign_plan(primary_signal),
                "suggestions": suggestions or _fallback_suggestions(primary_signal),
            },
            "confidence": _clamp_confidence(base_pipeline.get("confidence") or 0.85),
        }
    except Exception as exc:
        agent_flow_trace.append({"step": "agentic_flow", "status": "failed", "error": str(exc)})

    data = dict(base_pipeline)
    data["agent_flow"] = agent_flow_trace
    data.update(product_output)
    logger.info("system:done query=%s", query)
    return data
