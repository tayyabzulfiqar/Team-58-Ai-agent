from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime


_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


def run_ai_system(input_text: str) -> dict:
    # Local import keeps this script runnable from repo root without packaging steps.
    from core.orchestrator import run_system

    result = run_system(input_text)
    if isinstance(result, dict):
        return result
    return {"error": "non_dict_output", "raw": str(result)}


def evaluate_output(output: dict) -> dict:
    errors: list[dict] = []

    if not output.get("detected_domain"):
        errors.append({"layer": "domain_detection", "issue": "missing domain"})

    if not output.get("detected_intent"):
        errors.append({"layer": "intent_mapping", "issue": "missing intent"})

    if not output.get("primary_signal"):
        errors.append({"layer": "signal_extraction", "issue": "missing signal"})

    if not output.get("reasoning_chain"):
        errors.append({"layer": "reasoning", "issue": "no reasoning"})

    if not output.get("final_output"):
        errors.append({"layer": "output", "issue": "no output"})

    if errors:
        return {"status": "fail", "errors": errors}
    return {"status": "pass"}


def _normalize_for_evaluation(pipeline_result: dict) -> dict:
    detected_domain = ""
    detected_intent = False
    primary_signal = ""
    reasoning_chain = []

    if isinstance(pipeline_result, dict):
        detected_domain = str(pipeline_result.get("domain") or "")
        primary_signal = str(pipeline_result.get("primary_signal") or "")
        reasoning_chain = list(pipeline_result.get("reasoning_chain") or [])
        detected_intent = bool(
            pipeline_result.get("intent_weights")
            or pipeline_result.get("primary_signal")
            or pipeline_result.get("secondary_signals")
            or pipeline_result.get("signals")
        )

    return {
        "detected_domain": detected_domain,
        "detected_intent": detected_intent,
        "primary_signal": primary_signal,
        "reasoning_chain": reasoning_chain,
        "final_output": pipeline_result if isinstance(pipeline_result, dict) else {},
    }


def generate_report(results: list[dict]) -> dict:
    total = len(results)
    fail = sum(1 for r in results if r.get("status") == "fail")
    passed = total - fail

    layer_counts = Counter()
    for r in results:
        if r.get("status") != "fail":
            continue
        for err in r.get("errors") or []:
            layer_counts[str(err.get("layer") or "unknown")] += 1

    failures_by_layer = dict(sorted(layer_counts.items(), key=lambda kv: (-kv[1], kv[0])))
    fail_examples: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r.get("status") != "fail":
            continue
        for err in r.get("errors") or []:
            layer = str(err.get("layer") or "unknown")
            if len(fail_examples[layer]) < 5:
                fail_examples[layer].append(
                    {
                        "input_id": r.get("input_id"),
                        "input": r.get("input", ""),
                        "issue": err.get("issue", ""),
                    }
                )

    return {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "total": total,
        "pass": passed,
        "fail": fail,
        "pass_rate": round((passed / total) if total else 0.0, 4),
        "failures_by_layer": failures_by_layer,
        "failure_examples": fail_examples,
        "results": results,
    }


def main() -> int:
    inputs = [
        "bro traffic aa raha but sale zero kya issue hai",
        "getting clicks but no conversion whats wrong",
        "ads running daily but no result",
        "why my website not converting users",
        "cricket match kal kisne jeeta tha",
        "i am getting leads but no one buying why",
        "sales drop suddenly idk why help",
        "bro system not working properly check karo",
        "too much traffic but revenue zero explain",
        "my landing page sucks maybe idk",
        "why users leaving without buying",
        "CPL low but ROI zero why",
        "ads good but sales dead",
        "confused why no conversions happening",
        "kya scene hai sales ka kuch samaj nahi aa raha",
        "people visiting but not clicking buy button",
        "maybe pricing issue or trust idk",
        "funnel broken or what",
        "why bounce rate high",
        "sales not happening even after ads",
        "i think audience wrong maybe",
        "or landing page problem?",
        "bro check my funnel issue",
        "traffic useless lag raha hai",
        "visitors coming but no action",
        "no checkout happening",
        "users drop off before payment",
        "offer weak hai kya?",
        "maybe copy issue idk",
        "no engagement after click",
        "why people not trusting my page",
        "no testimonials added is that problem",
        "ads working but backend dead",
        "system seems broken",
        "conversion rate literally zero",
        "why no one buying bro",
        "everything looks fine but no sales",
        "confusing situation help",
        "do i need better offer?",
        "or better design?",
        "page loading slow maybe?",
        "or user intent mismatch?",
        "what is the actual issue",
        "im stuck no revenue",
        "traffic waste ho raha hai",
        "users just browsing not buying",
        "funnel optimization needed?",
        "how to fix conversion problem",
        "ads good landing bad?",
        "dont understand problem clearly",
        "need help asap",
        "sales completely dead",
        "cricket score kya tha kal",
        "why people clicking but not buying",
        "trust issue maybe",
        "no guarantee on page",
        "checkout complicated maybe?",
        "too many steps in funnel",
        "drop off at checkout",
        "no urgency on page",
        "maybe no offer clarity",
        "message not clear",
        "what should i fix first",
        "everything confusing",
        "users not understanding product",
        "bad copywriting?",
        "headline weak maybe",
        "CTA not strong?",
        "what is main issue bro",
        "ads targeting wrong?",
        "landing mismatch?",
        "user expectation different",
        "offer not attractive",
        "price too high?",
        "or value not clear",
        "visitors confused",
        "no emotional trigger",
        "no urgency",
        "no scarcity",
        "just traffic no money",
        "serious issue bro",
        "losing money daily",
        "ads eating budget",
        "no returns coming",
        "this is bad situation",
        "need quick fix",
        "what is biggest mistake here",
        "where system failing",
        "how to diagnose properly",
        "is it funnel issue or offer issue",
        "need clarity",
        "everything unclear",
        "data not helping",
        "metrics confusing",
        "need simple answer",
        "what should i do first",
        "step by step fix needed",
        "help me understand problem",
        "why conversion zero",
        "what is root cause",
        "hey bro website pe log aa rahe but koi buy nahi kar raha",
        "i think my funnel is trash",
        "users coming from ads but not converting",
        "maybe pricing too high idk",
        "low conversion high clicks explain",
        "people just scrolling and leaving",
        "checkout abandoned every time",
        "ads spending going waste",
        "no roi from ads",
        "something wrong with landing page",
        "why no sales even with traffic",
        "help me fix funnel bro",
        "offer not converting maybe",
        "people not trusting my brand",
        "no reviews on page maybe issue",
        "landing page confusing af",
        "cta not working maybe",
        "users not understanding product value",
        "too much info on page maybe",
        "people drop at pricing section",
        "no urgency killing sales?",
        "why no one clicking checkout",
        "conversion problem serious",
        "ads fine backend weak",
        "need funnel audit",
        "why users bounce so fast",
        "maybe wrong targeting idk",
        "message mismatch between ad and page",
        "landing page slow af",
        "users not engaging",
        "conversion rate garbage",
        "need help fixing this asap",
        "what am i doing wrong",
        "no buyers only visitors",
        "sales funnel broken completely",
        "ads burning money daily",
        "i cant figure this out",
        "maybe offer is bad",
        "or positioning weak",
        "users confused about product",
        "no emotional connection",
        "no trust signals present",
        "page looks basic maybe",
        "need premium feel",
        "why traffic useless",
        "need serious fix now",
    ]

    results: list[dict] = []
    for i, input_text in enumerate(inputs):
        try:
            system_output = run_ai_system(input_text)
        except Exception as exc:
            system_output = {"error": "exception", "message": str(exc)}

        eval_payload = _normalize_for_evaluation(system_output)
        evaluation = evaluate_output(eval_payload)

        if evaluation["status"] == "fail":
            results.append(
                {
                    "input_id": i + 1,
                    "input": input_text,
                    "status": "fail",
                    "errors": evaluation["errors"],
                }
            )
        else:
            results.append({"input_id": i + 1, "status": "pass"})

    report = generate_report(results)
    report_path = "backend/stress_test_report.json"
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=True, indent=2)

    print(json.dumps({k: report[k] for k in ("total", "pass", "fail", "pass_rate", "failures_by_layer")}, indent=2))
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
