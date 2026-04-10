def report_generator(data):
    safe_data = data if isinstance(data, dict) else {}
    scoring = safe_data.get("scoring") if isinstance(safe_data.get("scoring"), dict) else {}
    raw_opps = scoring.get("validated_opportunities")
    opportunities = raw_opps if isinstance(raw_opps, list) else []
    opportunities = [op for op in opportunities if isinstance(op, dict)]
    top = scoring.get("top") if isinstance(scoring.get("top"), dict) else {}

    decision = safe_data.get("decision") if isinstance(safe_data.get("decision"), dict) else {}
    execution = safe_data.get("execution") if isinstance(safe_data.get("execution"), dict) else {}

    # MAIN PROBLEM (CLEAN + REAL)
    raw_problem = str(decision.get("decision", "") or "")

    # clean system text → human readable
    main_problem = raw_problem.replace("Primary signal", "").replace("'", "").strip()
    if " selected" in main_problem:
        main_problem = main_problem.split(" selected", 1)[0].strip()
    if main_problem.endswith(":"):
        main_problem = main_problem[:-1].strip()
    if main_problem.startswith("signal"):
        main_problem = main_problem[len("signal") :].strip()
    if main_problem.startswith(":"):
        main_problem = main_problem[1:].strip()
    if not main_problem and opportunities:
        first_title = str(opportunities[0].get("title") or "").strip()
        if first_title:
            main_problem = f"Primary issue: {first_title}"
    if not main_problem:
        main_problem = "Conversion performance issue"

    # KEY INSIGHT (REAL)
    key_insight = str(top.get("title") or "").replace("Primary signal", "").replace("'", "").strip()
    if not key_insight and opportunities:
        key_insight = str(opportunities[0].get("title") or "").replace("Primary signal", "").replace("'", "").strip()
    if not key_insight:
        key_insight = "No dominant insight detected"

    # WHAT'S HAPPENING (REAL DATA)
    whats_happening = []
    seen_happening = set()
    for op in opportunities[:3]:
        title = str(op.get("title") or "").strip()
        if title:
            cleaned = title.replace("Primary signal", "").replace("'", "").strip()
            if cleaned and cleaned.lower() not in seen_happening:
                seen_happening.add(cleaned.lower())
                whats_happening.append(f"Users experiencing: {cleaned}")
    if not whats_happening:
        whats_happening = [
            "Users dropping before conversion",
            "Low engagement signals detected",
        ]

    # ROOT CAUSES (DERIVED)
    root_causes = []
    seen_causes = set()
    for op in opportunities[:3]:
        title = str(op.get("title") or "").strip()
        if not title:
            continue
        clean_title = title.replace("Primary signal", "").replace("'", "").strip()
        key = clean_title.lower()
        if clean_title and key not in seen_causes:
            seen_causes.add(key)
            root_causes.append(f"Caused by: {clean_title}")
    if not root_causes:
        root_causes = [
            "Lack of clear value proposition",
            "Weak conversion funnel",
            "Insufficient user trust signals",
        ]

    # EXECUTION STEPS (SAFE)
    raw_steps = execution.get("steps")
    steps = raw_steps if isinstance(raw_steps, list) else []
    steps = [str(s).strip() for s in steps if isinstance(s, str) and str(s).strip()]
    if not steps and opportunities:
        for op in opportunities[:3]:
            title = str(op.get("title") or "").strip()
            if title:
                steps.append(title)

    # ACTION PLAN (STRICT FROM EXECUTION; SAFE FALLBACK)
    action_plan = []
    for i, step in enumerate(steps):
        action_plan.append(
            {
                "step": i + 1,
                "title": step,
                "description": f"Execute step: {step}",
                "timeline": f"{(i + 1) * 3} days",
            }
        )
    if not action_plan:
        action_plan = [
            {
                "step": 1,
                "title": "Diagnose funnel bottleneck",
                "description": "Identify the highest-friction stage before optimizing",
                "timeline": "3 days",
            }
        ]

    # STRATEGY
    strategy = {
        "title": main_problem if main_problem else "Optimization strategy",
        "points": steps,
    }

    # CAMPAIGN CHANNELS (SAFE DEFAULTS)
    raw_channels = execution.get("platforms")
    channels = raw_channels if isinstance(raw_channels, list) else []
    channels = [str(c).strip() for c in channels if isinstance(c, str) and str(c).strip()]
    if not channels:
        channels = ["facebook", "instagram"]

    # CAMPAIGN PLAN (DYNAMIC)
    campaign_plan = {
        "offer": f"Targeted offer based on {key_insight}",
        "message": f"Addressing {main_problem} with clear value proposition",
        "channels": channels,
        "goal": "Increase conversion rate and user engagement",
    }

    # CONFIDENCE (SCALED)
    try:
        base_score = float(top.get("score", 0) or 0)
    except Exception:
        base_score = 0.0
    confidence_score = int(base_score * 10)
    if confidence_score <= 10:
        confidence_score *= 10
    confidence_score = max(0, min(100, confidence_score))

    return {
        "main_problem": main_problem,
        "key_insight": key_insight,
        "strategy": strategy,
        "whats_happening": whats_happening,
        "root_causes": root_causes,
        "action_plan": action_plan,
        "campaign_plan": campaign_plan,
        "confidence_score": confidence_score,
    }
