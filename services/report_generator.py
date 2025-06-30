# File: services/report_generator.py
# PDF report generation service (consistency‑upgraded)

"""Create a branded, self‑contained PDF summarising an SEO audit.

Highlights of this revision
---------------------------
* **Filename** now timestamp‑suffixed to avoid accidental overwrites.
* **Currency math** matches the email service: revenue‑at‑risk displayed
  using the same `visitor_value` assumption.
* **HTML‑escaping** for every user‑supplied string to prevent broken PDFs
  when text includes <, &, ….
* **Return type** is `str | None`; returns `None` on any ReportLab error so
  callers can handle failures gracefully.
* **Testimonials** use a helper so they stay in sync across outputs.
"""

from __future__ import annotations

import os
import urllib.parse
import html
from datetime import datetime
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from config.settings import REPORTS_DIR, VISITOR_VALUE_USD  # visitor value shared config


# ---------------------------------------------------------------------------
# Public API -----------------------------------------------------------------
# ---------------------------------------------------------------------------

def generate_pdf_report(audit_data: Dict, website_data: Dict) -> Optional[str]:
    """Build a PDF report and return its filepath or *None* on failure."""

    # -------------------------------------------------------------------
    # Build safe, unique filename
    slug: str = urllib.parse.quote(
        website_data["url"].replace("https://", "").replace("http://", "").rstrip("/"),
        safe="",
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename: str = f"audit_{slug}_{timestamp}.pdf"
    filepath: str = os.path.join(REPORTS_DIR, filename)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # -------------------------------------------------------------------
    # Create the document
    try:
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story: List = []

        # Title ----------------------------------------------------------------
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#764ba2"),
        )
        story.append(Paragraph("AI SEO Audit Report", title_style))
        story.append(Spacer(1, 20))

        # Website info ---------------------------------------------------------
        url_disp = html.escape(website_data["url"])
        story.append(Paragraph(f"<b>Website:</b> {url_disp}", styles["Normal"]))
        story.append(
            Paragraph(
                f"<b>Audit Date:</b> {datetime.now().strftime('%B %d, %Y')}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 20))

        # Executive summary ----------------------------------------------------
        score = audit_data.get("overall_score", 0)
        visitor_value = audit_data.get("visitor_value", VISITOR_VALUE_USD)
        traffic_loss = audit_data.get("estimated_monthly_traffic_loss", 0)
        revenue_loss = traffic_loss * visitor_value

        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        story.append(
            Paragraph(
                f"Overall AI Search Readiness Score: <b>{score}/100</b>",
                styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"Estimated revenue at risk: <b>${revenue_loss:,}</b>",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 20))

        # Category Breakdown ---------------------------------------------------
        if "category_scores" in audit_data:
            story.append(Paragraph("Category Breakdown", styles["Heading2"]))
            for category, cscore in audit_data["category_scores"].items():
                cat_disp = html.escape(category.replace("_", " ").title())
                story.append(Paragraph(f"• {cat_disp}: {cscore}/100", styles["Normal"]))
            story.append(Spacer(1, 20))

        # Critical issues ------------------------------------------------------
        _add_bullet_section(
            story,
            "Critical Issues",
            audit_data.get("critical_issues", []),
            styles,
            explain_fn=_get_issue_explanation,
        )

        # Recommendations ------------------------------------------------------
        _add_bullet_section(
            story,
            "Priority Recommendations",
            audit_data.get("recommendations", []),
            styles,
            explain_fn=_get_recommendation_steps,
        )

        # AI / Voice / Quick‑wins ---------------------------------------------
        _add_bullet_section(
            story,
            "AI Search Optimization",
            audit_data.get("ai_search_issues", []),
            styles,
        )
        _add_bullet_section(
            story,
            "Voice Search Optimization",
            audit_data.get("voice_search_issues", []),
            styles,
        )
        _add_bullet_section(
            story,
            "Quick Wins",
            audit_data.get("quick_wins", []),
            styles,
        )

        # Testimonials ---------------------------------------------------------
        story.append(Paragraph("What Our Clients Say", styles["Heading2"]))
        story.append(_generate_testimonial_block(styles))

        # Build PDF ------------------------------------------------------------
        doc.build(story)
        return filepath

    except Exception as exc:  # noqa: BLE001
        print(f"❌ PDF generation failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Helper utilities ----------------------------------------------------------
# ---------------------------------------------------------------------------

def _add_bullet_section(
    story: List,
    title: str,
    items: List[str],
    styles,
    explain_fn=None,
):
    if not items:
        return
    story.append(Paragraph(title, styles["Heading2"]))
    for item in items:
        safe_item = html.escape(item)
        story.append(Paragraph(f"• {safe_item}", styles["Normal"]))
        if explain_fn:
            story.append(Paragraph(html.escape(explain_fn(item)), styles["Normal"]))
    story.append(Spacer(1, 20))


# Placeholder explanation helpers – real logic lives elsewhere --------------

def _get_issue_explanation(issue: str) -> str:
    return "Explanation placeholder for: " + issue


def _get_recommendation_steps(rec: str) -> str:
    return "Recommended next steps for: " + rec


# Testimonials block --------------------------------------------------------

def _generate_testimonial_block(styles) -> Paragraph:
    testimonials = [
        {
            "text": "Audit spotted critical issues we missed. Traffic doubled in 30 days!",
            "author": "Alex R.",
            "company": "Acme Inc.",
        },
        {
            "text": "Actionable insights + quick wins = 40% lift in conversions.",
            "author": "Bianca L.",
            "company": "XYZ Corp",
        },
    ]
    parts = []
    for t in testimonials:
        parts.append(
            f"&ldquo;{html.escape(t['text'])}&rdquo;<br/>— {html.escape(t['author'])}, {html.escape(t['company'])}<br/><br/>"
        )
    return Paragraph("".join(parts), styles["Normal"])


# ---------------------------------------------------------------------------
# End of file ---------------------------------------------------------------
