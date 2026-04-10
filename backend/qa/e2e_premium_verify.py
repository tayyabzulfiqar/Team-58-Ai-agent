import json
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

import requests
from playwright.sync_api import sync_playwright


FRONTEND_BASE = "http://127.0.0.1:5173"
BACKEND_BASE = "http://127.0.0.1:8000"


@dataclass
class VerificationResult:
    report_id: str
    main_problem_text: str
    console_errors: List[str]
    pdf_download_bytes: int
    share_url: str


def _extract_report_id(url: str) -> Optional[str]:
    m = re.search(r"/report/([^/?#]+)", url)
    if m:
        return m.group(1)
    return None


def _wait_backend_ready(report_id: str, timeout_s: int = 180) -> dict:
    started = time.time()
    while time.time() - started < timeout_s:
        rep = requests.get(f"{BACKEND_BASE}/api/reports/{report_id}", timeout=10).json()
        if isinstance(rep, dict) and rep.get("status") == "ready":
            return rep
        time.sleep(2)
    raise RuntimeError("Backend report did not reach status=ready in time")


def run() -> VerificationResult:
    query = f"Luxury gym in Dubai struggling with retention (QA {int(time.time())})"
    console_errors: List[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(f"pageerror: {exc}"))

        page.goto(f"{FRONTEND_BASE}/", wait_until="domcontentloaded")

        page.get_by_placeholder("Describe your business challenge or goal...").fill(query)
        page.get_by_role("button", name="Generate", exact=True).click()

        page.wait_for_url(re.compile(r".*/processing.*"), timeout=10_000)
        page.wait_for_url(re.compile(r".*/report.*"), timeout=15_000)

        # ReportPage uses location state by default, so the URL is `/report`.
        # Pull the latest report_id from the backend (reports are returned latest-first).
        reports = requests.get(f"{BACKEND_BASE}/api/reports", timeout=10).json()
        if not isinstance(reports, list) or not reports:
            raise RuntimeError("Backend /api/reports returned no reports")
        report_id = str(reports[0].get("report_id") or "")
        if not report_id:
            raise RuntimeError("Could not determine report_id from backend /api/reports")

        backend_report = _wait_backend_ready(report_id, timeout_s=240)
        backend_main_problem = ""
        if isinstance(backend_report.get("data"), dict):
            backend_main_problem = str(backend_report["data"].get("main_problem") or "").strip()

        # Wait for dashboard content to reflect backend data.
        page.get_by_text("Main Problem", exact=True).wait_for(timeout=120_000)
        if backend_main_problem:
            page.locator(f"text={backend_main_problem}").first.wait_for(timeout=120_000)

        # Ensure we render dynamic content (not generic placeholders).
        main_problem = page.locator("text=Main Problem").first
        # main problem value is in the card body; read the whole card for a simple check.
        main_problem_text = page.locator("div").filter(has_text="Main Problem").first.inner_text().strip()
        if not main_problem_text:
            raise RuntimeError("Main Problem card is empty")

        full_text = page.locator("body").inner_text()
        banned = ["Week 1", "Week 2", "Optimize funnel", "Launch ads", "optimize funnel", "launch ads"]
        for b in banned:
            if b in full_text:
                raise RuntimeError(f"Found banned template phrase in UI: {b}")

        # PDF download
        with page.expect_download(timeout=30_000) as dl_info:
            page.get_by_role("button", name=re.compile(r"PDF", re.I)).click()
        download = dl_info.value
        path = download.path()
        pdf_bytes = 0
        if path:
            pdf_bytes = os.path.getsize(str(path))
        if pdf_bytes <= 0:
            raise RuntimeError("PDF download is empty")

        # Share via backend, then open the share page.
        share = requests.post(f"{BACKEND_BASE}/api/reports/{report_id}/share", timeout=10)
        share.raise_for_status()
        share_payload = share.json()
        share_url = share_payload.get("share_url") or ""
        if not share_url:
            raise RuntimeError("Backend did not return share_url")

        page.goto(f"{FRONTEND_BASE}{share_url}", wait_until="networkidle")
        # Share page may show an overlay while the report is still processing.
        overlay = page.get_by_text("AI agents are analyzing", exact=False)
        try:
            overlay.wait_for(state="detached", timeout=180_000)
        except Exception:
            pass

        page.get_by_text("Main Problem", exact=True).wait_for(state="attached", timeout=180_000)
        if backend_main_problem:
            page.locator(f"text={backend_main_problem}").first.wait_for(timeout=120_000)

        browser.close()

    return VerificationResult(
        report_id=report_id,
        main_problem_text=main_problem_text,
        console_errors=console_errors,
        pdf_download_bytes=pdf_bytes,
        share_url=share_url,
    )


if __name__ == "__main__":
    result = run()
    print(json.dumps(result.__dict__, indent=2))
    if result.console_errors:
        print("\nConsole errors detected:", file=sys.stderr)
        for e in result.console_errors:
            print(f"- {e}", file=sys.stderr)
        sys.exit(2)
