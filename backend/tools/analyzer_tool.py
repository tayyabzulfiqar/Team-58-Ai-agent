import re

from backend.services.qwen_service import qwen_generate


def clean_text(text):
    text = re.sub(r"[{}'\"]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def detect_source_type(text):
    t = text.lower()

    if any(x in t for x in ["ibm", "forbes", "hubspot", "harvard"]):
        return "authority"

    if "reddit" in t:
        return "community"

    return "general"


def get_weight(source_type):
    if source_type == "authority":
        return 3
    if source_type == "community":
        return 1
    return 2


def parse_decision(text):
    strategy = "Performance marketing"
    confidence = 50

    if "<DECISION>" in text:
        block = text.split("<DECISION>")[-1].split("</DECISION>")[0]

        for line in block.splitlines():
            if "strategy=" in line:
                value = line.split("strategy=")[-1].strip().lower()
                value = value.split("|")[0].strip()

                if "emotional" in value:
                    strategy = "Emotional marketing"
                elif "brand" in value:
                    strategy = "Brand awareness"
                elif "performance" in value:
                    strategy = "Performance marketing"

            if "confidence=" in line:
                try:
                    confidence = int(line.split("=")[-1].strip())
                except Exception:
                    pass

    return strategy, confidence


def _repair_decision_block(llm_output):
    repair_prompt = f"""
Convert the following strategist output into ONLY this exact format:

<DECISION>
strategy=Performance marketing | Emotional marketing | Brand awareness
confidence=0-100
</DECISION>

Rules:
- Return only the DECISION block
- Choose exactly one strategy
- Keep confidence as an integer

TEXT:
{llm_output[:2000]}
"""

    return qwen_generate(repair_prompt)


def _normalize_decision_block(repaired_output):
    strategy, confidence = parse_decision(repaired_output)
    return f"<DECISION>\nstrategy={strategy}\nconfidence={confidence}\n</DECISION>"


def extract_reason(text):
    if not text:
        return "Strategy selected based on combined data signals"

    cleaned = text
    if "<DECISION>" in cleaned:
        cleaned = cleaned.split("<DECISION>")[0].strip()

    lines = [line.strip(" -*\t") for line in cleaned.splitlines() if line.strip()]

    for line in reversed(lines):
        lowered = line.lower()
        if lowered.startswith("reason:"):
            reason = line.split(":", 1)[-1].strip()
            if reason:
                return reason
        if len(line) > 30 and "strategy=" not in lowered and "confidence=" not in lowered:
            return line

    return "Strategy selected based on combined data signals"


def analyzer_tool(data):
    items = data.get("data", [])
    reddit = data.get("reddit", [])

    weighted_data = []

    for item in items:
        extracted = item.get("extracted", {})
        points = extracted.get("key_points", [])

        if points:
            for p in points:
                source_type = detect_source_type(p)
                weight = get_weight(source_type)

                weighted_data.append({
                    "text": p,
                    "source": source_type,
                    "weight": weight
                })
        else:
            fallback_points = [
                item.get("title", ""),
                item.get("snippet", ""),
                item.get("content", "")
            ]

            for p in fallback_points:
                if not p:
                    continue

                source_type = detect_source_type(p)
                weight = get_weight(source_type)

                weighted_data.append({
                    "text": p,
                    "source": source_type,
                    "weight": weight
                })

    for r in reddit:
        reddit_text = f"{r.get('title', '')} {r.get('text', '')}".strip()
        weighted_data.append({
            "text": reddit_text,
            "source": "community",
            "weight": 1
        })

    combined = ""

    for d in weighted_data:
        if d["text"]:
            combined += (d["text"] + " ") * d["weight"]

    combined = clean_text(combined)
    llm_insight = qwen_generate(combined)

    analysis_prompt = f"""
ROLE: Senior Marketing Strategist

TASK:
Analyze the data and evaluate strategies.

---

STRATEGIES:

1. Performance marketing
2. Emotional marketing
3. Brand awareness

---

FOR EACH:

- When it works
- Why it works

---

POLICY RULES (MANDATORY):

- Performance marketing:
  Use ONLY when short-term measurable conversions are clearly the primary objective.

- Emotional marketing:
  Use when persuasion, trust, storytelling, or audience resonance is the main driver.

- Brand awareness:
  MUST be selected when:
  
  - new market entry
  - new product launch
  - early-stage startup
  - category creation
  - long-term growth focus

IMPORTANT:
Do NOT default to performance marketing.
Actively evaluate if brand awareness is more appropriate.

---

THEN DECIDE:

Select ONLY ONE best strategy.

---

DATA:
{combined[:2000]}

---

STRICT OUTPUT FORMAT:

You MUST end your response with EXACTLY this format:

<DECISION>
strategy=Performance marketing | Emotional marketing | Brand awareness
confidence=0-100
</DECISION>

IMPORTANT RULES:

- DO NOT write multiple strategies in DECISION
- DO NOT explain inside DECISION block
- DECISION block MUST be last
"""

    llm_output = qwen_generate(analysis_prompt)
    best_strategy, confidence = parse_decision(llm_output)

    if "<DECISION>" not in llm_output:
        repaired_output = _repair_decision_block(llm_output)
        repaired_strategy, repaired_confidence = parse_decision(repaired_output)

        if "<DECISION>" in repaired_output:
            normalized_output = _normalize_decision_block(repaired_output)
            llm_output = f"{llm_output}\n\n{normalized_output}"
            best_strategy, confidence = parse_decision(normalized_output)
        else:
            llm_output = qwen_generate(analysis_prompt)
            best_strategy, confidence = parse_decision(llm_output)

            if "<DECISION>" not in llm_output:
                repaired_output = _repair_decision_block(llm_output)
                repaired_strategy, repaired_confidence = parse_decision(repaired_output)

                if "<DECISION>" in repaired_output:
                    normalized_output = _normalize_decision_block(repaired_output)
                    llm_output = f"{llm_output}\n\n{normalized_output}"
                    best_strategy, confidence = parse_decision(normalized_output)

    extracted_reason = extract_reason(llm_output)

    words = combined.split()
    keywords = list(dict.fromkeys(words[:10]))
    strategies = []
    hooks = []
    trends = []

    if "emotion" in combined:
        strategies.append("emotional marketing")

    if "conversion" in combined:
        strategies.append("performance marketing")

    if "brand" in combined:
        strategies.append("brand awareness")

    if "urgency" in combined or "urgent" in combined or "limited" in combined:
        hooks.append("urgency hook")

    if "discount" in combined or "offer" in combined or "sale" in combined:
        hooks.append("discount-based hook")

    if "ai" in combined or "automation" in combined:
        trends.append("AI-driven marketing")

    return {
        "insight_summary": combined[:200],
        "keywords": keywords,
        "data_size": len(combined),
        "top_strategies": list(set(strategies))[:3],
        "top_hooks": list(set(hooks))[:3],
        "market_trends": list(set(trends))[:3],
        "best_strategy": best_strategy,
        "reason": extracted_reason,
        "confidence": confidence,
        "llm_analysis": llm_output,
        "llm_insight": llm_insight,
        "source_mix": weighted_data[:10],
        "data_points": len(items),
        "status": "analyzed"
    }
