from fastapi import BackgroundTasks
from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware

from core.guarded_pipeline import validate_input_payload
from core.input_utils import extract_query_text
from core.logging_utils import configure_logging
from core.logging_utils import get_logger
from core.orchestrator import run_system
from tools.insight_enricher import enrich_insights
from tools.output_validator import validate_output
from tools.dashscope_client import generate_consulting_report
from tools.pdf_generator import generate_report_pdf
from tools.report_formatter import format_report
from tools.report_generator import report_generator
from tools.report_store import create_report
from tools.report_store import create_pending_report
from tools.report_store import get_all_reports
from tools.report_store import get_report
from tools.report_store import get_saved_reports
from tools.report_store import toggle_save
from tools.report_store import update_report
from tools.share_store import create_share_link
from tools.share_store import get_report_id_for_share

configure_logging()
logger = get_logger("team58.api")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _normalize_result(input_data: dict, pipeline_result: dict) -> dict:
    if isinstance(pipeline_result, dict) and pipeline_result.get("validation_type") == "low_quality" and len(pipeline_result.keys()) == 1:
        return {"validation_type": "low_quality"}

    # Keep the pipeline output as-is (product-level output), but ensure required contract keys exist.
    normalized = {
        "domain": "business",
        "validation_type": "valid_weak",
        "signals": [],
        "clusters": [],
        "top_cluster": "",
        "confidence": 0.5,
    }
    if isinstance(pipeline_result, dict):
        normalized.update(dict(pipeline_result))
        normalized.setdefault("domain", "business")
        normalized.setdefault("validation_type", "valid_weak")
        normalized.setdefault("signals", [])
        normalized.setdefault("clusters", [])
        normalized.setdefault("top_cluster", "")
        normalized.setdefault("confidence", 0.5)

    errors = validate_output(normalized)
    if errors:
        logger.warning("api:output-validation-failed errors=%s", errors)
        normalized = {
            "domain": "general",
            "validation_type": "low_quality",
            "signals": [],
            "clusters": [],
            "top_cluster": "",
            "confidence": 0.0,
            "primary_signal": "",
            "secondary_signals": [],
            "intent_weights": [],
            "reasoning": "",
            "root_causes": [],
            "ambiguity": False,
            "status": "needs_clarification",
            "status_reason": "Output validation failed",
            "status_suggestion": "Ask user for more detail",
            "decision_path": "clarification",
            "final_signals": [],
        }
    return normalized

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "AI Engine Running",
        "agents": ["research", "data", "campaign"],
        "contract_status": "ENFORCED",
    }

@app.post("/run-system")
@app.post("/api/run-system")
def run_system_endpoint(input_data: dict = Body(default={})):
    try:
        logger.info("api:run-system:start")
        if not validate_input_payload(input_data):
            logger.info("api:run-system:invalid-input-contract")
            return {"validation_type": "low_quality"}
        patched_input = dict(input_data)
        patched_input["query"] = extract_query_text(input_data)
        pipeline_result = run_system(patched_input)
        if not isinstance(pipeline_result, dict):
            return _normalize_result(patched_input, {})
        logger.info("api:run-system:success")
        return _normalize_result(patched_input, pipeline_result)
    except Exception as exc:
        logger.exception("api:run-system:failure")
        return {
            "domain": "general",
            "validation_type": "low_quality",
            "signals": [],
            "clusters": [],
            "top_cluster": "",
            "confidence": 0.0,
            "primary_signal": "",
            "secondary_signals": [],
            "intent_weights": [],
            "reasoning": "",
            "root_causes": [],
            "ambiguity": False,
            "status": "needs_clarification",
            "status_reason": "Pipeline exception",
            "status_suggestion": "Ask user for more detail",
            "decision_path": "clarification",
            "final_signals": [],
        }


def _build_report_from_query(query: str) -> dict:
    raw = run_system({"query": query})
    if not isinstance(raw, dict):
        raw = {}

    actions = list(raw.get("actions") or [])
    opportunities = []
    for item in actions:
        if not isinstance(item, dict):
            continue
        title = item.get("action")
        if not title:
            continue
        opp = {"title": title}
        for k in ("impact", "difficulty", "priority", "reason"):
            if item.get(k) is not None:
                opp[k] = item.get(k)
        opportunities.append(opp)

    if not opportunities:
        plan = list((raw.get("campaign") or {}).get("plan") or [])
        for step in plan:
            if isinstance(step, str) and step.strip():
                opportunities.append({"title": step.strip()})

    research = list(raw.get("research") or [])
    top_title = research[0] if research else (raw.get("insights") or raw.get("primary_signal") or "")
    score = raw.get("confidence") or 0

    steps = list((raw.get("campaign") or {}).get("plan") or [])
    if not steps:
        steps = [op.get("title") for op in opportunities if op.get("title")]

    signal_to_channels = {
        "conversion optimization": ["facebook", "instagram"],
        "paid ads": ["facebook", "instagram", "google"],
        "lead generation": ["facebook", "instagram", "linkedin"],
        "seo": ["google"],
        "retention": ["email", "push"],
    }
    platforms = []
    primary = str(raw.get("primary_signal") or "").strip().lower()
    if primary in signal_to_channels:
        platforms.extend(signal_to_channels[primary])

    adapted = {
        "query": query,
        "raw": raw,
        "scoring": {"validated_opportunities": opportunities, "top": {"title": top_title, "score": float(score or 0)}},
        "decision": {"decision": raw.get("main_problem") or raw.get("status_reason") or raw.get("reasoning") or ""},
        "execution": {"steps": [s for s in steps if isinstance(s, str) and s.strip()], "platforms": platforms},
    }
    report = report_generator(adapted)
    report = enrich_insights(query, raw, report)
    return report


def _generate_report_task(report_id: str, query: str) -> None:
    try:
        report = _build_report_from_query(query)
        title = report.get("main_problem") or query or "Report"
        confidence = report.get("confidence_score") or 0
        update_report(report_id, data=report, status="ready", title=title, confidence_score=confidence, error=None)
    except Exception as exc:
        logger.exception("api:analyze:background-failure report_id=%s", report_id)
        update_report(report_id, status="error", error=str(exc))


@app.post("/api/analyze")
def analyze(background_tasks: BackgroundTasks, data=Body(default={})):
    payload = data if isinstance(data, dict) else {"query": str(data)}
    query = str(payload.get("query", "") or "").strip()
    pending = create_pending_report(query)
    background_tasks.add_task(_generate_report_task, pending.get("report_id"), query)
    return pending


@app.get("/api/reports")
def get_reports():
    reports = get_all_reports()
    # return only summary (lightweight)
    return [
        {
            "report_id": r.get("report_id"),
            "title": r.get("title"),
            "confidence_score": r.get("confidence_score"),
            "created_at": r.get("created_at"),
            "status": r.get("status"),
        }
        for r in list(reports)[::-1]  # latest first
        if isinstance(r, dict)
    ]


@app.get("/api/reports/saved")
def fetch_saved_reports():
    reports = get_saved_reports()
    return [
        {
            "report_id": r.get("report_id"),
            "title": r.get("title"),
            "confidence_score": r.get("confidence_score"),
            "created_at": r.get("created_at"),
            "status": r.get("status"),
        }
        for r in list(reports)[::-1]
        if isinstance(r, dict)
    ]


@app.post("/api/reports/{report_id}/save")
def save_report(report_id: str):
    report = toggle_save(report_id)
    if not report:
        return {"error": "Report not found"}
    return {"message": "Saved status updated", "saved": report.get("saved", False)}


@app.get("/api/reports/{report_id}")
def fetch_report(report_id: str):
    report = get_report(report_id)
    if not report:
        return {"error": "Report not found"}
    return report


@app.post("/api/format-report")
def format_report_endpoint(payload: dict = Body(default={})):
    """
    Premium formatting endpoint. Attempts AI enhancement via DashScope/Qwen (max ~5s),
    but always returns a readable formatted report using the local formatter as fallback.
    """
    try:
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Body must be { data: ReportData }")

        ai_text = generate_consulting_report(data, timeout_s=5.0)
        text = ai_text.strip() if isinstance(ai_text, str) and ai_text.strip() else format_report(data)
        return {"formatted_text": text}
    except HTTPException:
        raise
    except Exception:
        # Graceful fallback for any runtime errors
        data = payload.get("data") if isinstance(payload, dict) else {}
        return {"formatted_text": format_report(data if isinstance(data, dict) else {})}


@app.get("/api/reports/{report_id}/pdf")
def report_pdf(report_id: str):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.get("status") == "processing":
        raise HTTPException(status_code=409, detail="Report is still processing")
    if report.get("status") == "error":
        raise HTTPException(status_code=409, detail="Report failed to generate")

    formatted_text = format_report(report.get("data") if isinstance(report, dict) else {})
    try:
        pdf_bytes = generate_report_pdf(report, formatted_text)
    except Exception as exc:
        logger.exception("api:pdf-generation-failure report_id=%s", report_id)
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from exc

    headers = {"Content-Disposition": 'attachment; filename="report.pdf"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@app.post("/api/reports/{report_id}/share")
def share_report(report_id: str):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    share_id = create_share_link(report_id)
    return {"share_url": f"/share/{share_id}"}


@app.get("/api/share/{share_id}")
def fetch_shared_report(share_id: str):
    report_id = get_report_id_for_share(share_id)
    if not report_id:
        raise HTTPException(status_code=404, detail="Share link not found")

    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
