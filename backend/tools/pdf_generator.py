from __future__ import annotations

from io import BytesIO
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def _draw_wrapped_text(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, leading: float) -> float:
    """
    Draw text with simple word-wrapping. Returns the new y position.
    """
    if not text:
        return y

    words = text.split()
    line = ""
    for w in words:
        candidate = f"{line} {w}".strip()
        if c.stringWidth(candidate, "Helvetica", 11) <= max_width:
            line = candidate
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
            if y < inch:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = letter[1] - inch
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def generate_report_pdf(report: Dict[str, Any], formatted_text: str) -> bytes:
    """
    Produce a PDF download for a stored report. `formatted_text` should be the same
    formatted report string used in the UI (fast formatter).
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    title = str(report.get("title") or "Report")
    confidence = report.get("confidence_score")
    confidence_text = f"Confidence: {confidence}%" if isinstance(confidence, (int, float)) else "Confidence: -"

    x = inch
    y = height - inch
    max_width = width - 2 * inch
    leading = 14

    c.setFont("Helvetica-Bold", 18)
    y = _draw_wrapped_text(c, title, x, y, max_width, 22)
    c.setFont("Helvetica", 11)
    y -= 6
    y = _draw_wrapped_text(c, confidence_text, x, y, max_width, leading)
    y -= 10

    # Parse formatted_text into sections by known headings
    headings = ["Main Problem:", "Key Insight:", "Strategy:", "Execution Plan:", "Campaign Plan:"]
    sections: Dict[str, str] = {}
    current = None
    for line in formatted_text.splitlines():
        if line.strip() in headings:
            current = line.strip()
            sections[current] = ""
            continue
        if current is None:
            continue
        sections[current] = (sections[current] + ("\n" if sections[current] else "") + line).rstrip()

    def draw_section(name: str, content: str, y_pos: float) -> float:
        nonlocal c
        if y_pos < inch:
            c.showPage()
            y_pos = height - inch
        c.setFont("Helvetica-Bold", 13)
        y_pos = _draw_wrapped_text(c, name.replace(":", ""), x, y_pos, max_width, 18)
        c.setFont("Helvetica", 11)
        y_pos -= 4
        for para_line in (content or "").splitlines():
            if not para_line.strip():
                y_pos -= 6
                continue
            y_pos = _draw_wrapped_text(c, para_line, x, y_pos, max_width, leading)
        y_pos -= 10
        return y_pos

    for h in headings:
        y = draw_section(h, sections.get(h, "").strip(), y)

    c.save()
    return buf.getvalue()
