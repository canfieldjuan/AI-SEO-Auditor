# File: services/email_service.py
# Email service using Resend – dynamic audit report + product offer

import os
import random
import base64
import html
from typing import Dict, List

# ---------------------------------------------------------------------------
# Configuration (ENV **required**) ------------------------------------------------
# ---------------------------------------------------------------------------
BOOKING_URL: str = os.getenv("BOOKING_URL")
if not BOOKING_URL:
    raise ValueError("BOOKING_URL environment variable is required")

STRATEGY_CALL_VALUE: str = os.getenv("STRATEGY_CALL_VALUE", "297")
VISITOR_VALUE_USD: int = int(os.getenv("VISITOR_VALUE_USD", "50"))

# ---------------------------------------------------------------------------
# Public API -----------------------------------------------------------------
# ---------------------------------------------------------------------------

def send_email_report(email: str, audit_data: Dict, pdf_path: str, website_url: str) -> bool:
    """Generate a personalised SEO‑audit e‑mail and send it through Resend.

    Parameters
    ----------
    email : str
        Recipient address.
    audit_data : Dict
        Dict produced by the audit engine (scores, issues, etc.).
    pdf_path : str
        Optional path to a PDF report to attach.
    website_url : str
        Canonical site URL ­– used for subject lines & template replacements.
    """

    # --- Environment --------------------------------------------------------
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str | None = os.getenv("RESEND_FROM_EMAIL")

    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set in .env file")
        return False
    if not RESEND_FROM_EMAIL:
        print("❌ RESEND_FROM_EMAIL not set in .env file")
        return False

    # -----------------------------------------------------------------------
    try:
        import resend  # lazy import so the module remains optional when testing
        resend.api_key = RESEND_API_KEY
    except ImportError:
        print("❌ resend not installed. Run: pip install resend")
        return False

    # -----------------------------------------------------------------------
    # Attach PDF (if present) -------------------------------------------------
    attachments: List[Dict] = []
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            content: bytes = f.read()
        attachments.append({
            "filename": os.path.basename(pdf_path),
            "content": base64.b64encode(content).decode(),  # Resend expects base64
        })

    # -----------------------------------------------------------------------
    # Derive key metrics ------------------------------------------------------
    overall_score: int = audit_data.get("overall_score", audit_data.get("score", 0))
    score_segment: str = _get_score_segment(overall_score)
    critical_issues: List[str] = audit_data.get("critical_issues", [])
    recommendations: List[str] = audit_data.get("recommendations", [])
    critical_count: int = len(critical_issues)

    # Keep these values in audit_data for helper functions that expect them
    audit_data.setdefault("overall_score", overall_score)
    audit_data.setdefault("critical_count", critical_count)

    # -----------------------------------------------------------------------
    # Build HTML body --------------------------------------------------------
    html_body: str = _get_email_template(score_segment, audit_data)

    user_name: str = audit_data.get("user_name") or email.split("@")[0].replace(".", " ").title()

    testimonial_html: str = _generate_dynamic_testimonials(audit_data)
    offer_html: str = _generate_offer_html(audit_data)

    # Centralised placeholder replacement
    replacements: Dict[str, str] = {
        "userName":            html.escape(user_name),
        "testimonials":        testimonial_html,
        "product_offer":       offer_html,
        "recommendations":     "<ul>" + "".join(f"<li>{html.escape(r)}</li>" for r in recommendations) + "</ul>",
        "critical_issues":     "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in critical_issues) + "</ul>",
        "score":               str(overall_score),
        "critical_count":      str(critical_count),
    }

    for k, v in replacements.items():
        html_body = html_body.replace(f"{{{{{k}}}}}", v)

    # -----------------------------------------------------------------------
    # Subject line -----------------------------------------------------------
    audit_data["website_url"] = website_url  # normalise key for helper
    subject: str = _personalise_subject_line(audit_data)

    # -----------------------------------------------------------------------
    # Send via Resend ---------------------------------------------------------
    try:
        response = resend.Emails.send({
            "from": f"SEO Auditor <{RESEND_FROM_EMAIL}>",
            "to": email,
            "subject": subject,
            "html": html_body,
            "attachments": attachments,
        })
        print(f"✅ Email sent successfully to {email}")
        return True
    except Exception as exc:  # noqa: BLE001 – show all Resend errors
        print(f"❌ Resend error: {exc}")
        return False

# ---------------------------------------------------------------------------
# Helper functions – kept *private* (underscored) ---------------------------
# ---------------------------------------------------------------------------

def _get_score_segment(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def _get_email_template(segment: str, audit_data: Dict | None = None) -> str:
    """Return a HTML template with placeholders."""

    if audit_data is None:
        audit_data = {}

    industry = html.escape(audit_data.get("industry", "your industry"))
    competitors = [html.escape(c) for c in audit_data.get("top_competitors", [])]
    estimated_traffic_loss = audit_data.get("estimated_monthly_traffic_loss", 0)
    visitor_value = audit_data.get("visitor_value", VISITOR_VALUE_USD)
    revenue_impact = estimated_traffic_loss * visitor_value

    main_issue = html.escape(audit_data.get("main_technical_issue", "SEO issues"))

    templates: Dict[str, str] = {
        "high": f"""
            <h2 style='color:#1e88e5;'>Hi {{userName}}, You're Outperforming 73% of {industry} Websites… but Money Is Leaking Out</h2>
            <p>While your site scored <strong>{{score}}/100</strong>, you miss about <strong>{estimated_traffic_loss:,} visitors/mo</strong>. That's roughly <strong>${revenue_impact:,}‑a‑month</strong> gone.</p>
            <div style='background:#fff3cd;padding:15px;border-left:4px solid #ffc107;margin:20px 0;'>
                🚨 {competitors[0] if competitors else 'A competitor'} just levelled‑up their SEO and is siphoning traffic that should be yours.
            </div>
            {{recommendations}}
            <h3>Good news</h3>
            <p>Most fixes are one‑hour jobs. Clients typically see <strong>+40% traffic in 60 days</strong>.</p>
            {{product_offer}}
            {{testimonials}}
        """,
        "medium": f"""
            <h2 style='color:#ffc107;'>{{userName}}, You're Bleeding {estimated_traffic_loss:,} Visitors Every Month</h2>
            <p>Your audit revealed <strong>{{critical_count}}</strong> critical SEO issues blocking first‑page rankings.</p>
            <div style='background:#ffebee;padding:15px;border-left:4px solid #e53935;margin:20px 0;'>
                At ${visitor_value} per visitor, that's roughly <strong>${revenue_impact:,}/mo</strong> heading to competitors.
            </div>
            <h3>Top issue: {main_issue}</h3>
            {{critical_issues}}
            {{recommendations}}
            {{product_offer}}
            {{testimonials}}
        """,
        "low": f"""
            <h2 style='color:#e53935;'>{{userName}}, Your Site Is Invisible to 97% of Customers</h2>
            <div style='background:#e53935;color:#fff;padding:20px;margin:20px 0;'>
                <strong>Brutal truth:</strong> You're losing about <strong>${revenue_impact:,}/mo</strong> right now.
            </div>
            <h3>{{critical_count}} severe problems detected</h3>
            {{critical_issues}}
            <p>Every day you wait, the gap widens.</p>
            {{product_offer}}
            {{testimonials}}
        """,
    }
    return templates.get(segment, templates["medium"])


def _personalise_subject_line(audit_data: Dict[str, str]) -> str:
    """Generate an urgency‑driven subject line."""
    score = audit_data.get("overall_score", 0)
    website = audit_data.get("website_url", audit_data.get("websiteUrl", ""))
    competitors = audit_data.get("top_competitors", [])

    visitor_value = audit_data.get("visitor_value", VISITOR_VALUE_USD)
    revenue_loss = audit_data.get("estimated_monthly_revenue_loss", audit_data.get("estimated_monthly_traffic_loss", 0) * visitor_value)

    subjects: Dict[str, List[str]] = {
        "high": [
            f"⚠️ {competitors[0] if competitors else 'Competitor'} just leap‑frogged you on Google",
            f"You're leaking ${revenue_loss:,}/mo – quick win inside",
            f"Good & bad news about {website}'s SEO",
        ],
        "medium": [
            f"🚨 {website} has {audit_data.get('critical_count', 0)} urgent SEO issues",
            f"Your SEO score: {score}/100 (peers average 85)",
            "Warning: 67% of your customers can't find you",
        ],
        "low": [
            f"URGENT: {website} is practically invisible on Google",
            f"Emergency – site scored {score}/100 (industry min 70)",
            "🔴 Competitors are stealing your customers (proof inside)",
        ],
    }
    segment = _get_score_segment(score)
    return random.choice(subjects[segment])


# ---------------------------------------------------------------------------
# Secondary helpers ---------------------------------------------------------
# ---------------------------------------------------------------------------

def _generate_testimonial_html(testimonials: List[Dict[str, str]]) -> str:
    blocks = []
    for t in testimonials:
        blocks.append(
            f"""
            <div class='testimonial'>
                <p style='font-style:italic'>&ldquo;{html.escape(t['text'])}&rdquo;</p>
                <p>— {html.escape(t['author'])}, {html.escape(t['company'])}</p>
            </div>
            """
        )
    return "\n".join(blocks)


def _generate_dynamic_testimonials(audit_data: Dict) -> str:
    """Return a single testimonial tuned to the main issue."""
    default_testimonials = [
        {
            "text": "Thorough audit – spotted issues we missed. Traffic up 2× in a month!",
            "author": "Jane Smith",
            "company": "Acme Inc.",
        },
        {
            "text": "Actionable and fast. Rankings jumped from page 5 to #2.",
            "author": "John Doe",
            "company": "XYZ Corp",
        },
    ]

    map_by_issue = {
        "page_speed": {
            "text": "Load time dropped from 8s to 1.9s – conversions up 47% in 3 weeks.",
            "author": "Michael Chen",
            "company": "FastTech",
        },
        "mobile_optimization": {
            "text": "Mobile traffic tripled after fixes – revenue 3×.",
            "author": "Sarah Johnson",
            "company": "MobileFirst",
        },
        "technical_seo": {
            "text": "Indexing issues solved in 48h – traffic doubled in 30 days.",
            "author": "David Park",
            "company": "TechCorp",
        },
    }

    main_issue = audit_data.get("main_technical_issue", "")
    chosen = map_by_issue.get(main_issue, random.choice(default_testimonials))

    return _generate_testimonial_html([chosen])


def _generate_offer_html(audit_data: Dict | None = None) -> str:
    """Return the upsell block – static fallback, dynamic when audit_data supplied."""
    if audit_data is None:
        return (
            "<hr><p>Want hands‑on help fixing these issues? <a href='" + BOOKING_URL + "'>Book your free 30‑min strategy call</a></p>"
        )

    score = audit_data.get("overall_score", 0)
    main_issue = html.escape(audit_data.get("main_technical_issue", "SEO issues"))

    if score >= 80:
        urgency, benefit = ("Lock in your advantage", "stay ahead while rivals play catch‑up")
    elif score >= 60:
        urgency, benefit = ("Stop bleeding traffic", "win back lost visitors in 60 days")
    else:
        urgency, benefit = ("Emergency SEO rescue", "save your online presence before it's too late")

    industry = html.escape(audit_data.get("industry", "your industry"))

    return f"""
        <div style='background:#f5f5f5;padding:30px;margin:30px 0;text-align:center;'>
            <h2 style='color:#2e7d32;margin-top:0;'>{urgency}</h2>
            <p>Our team fixes {main_issue} for {industry} sites. We'll help you <strong>{benefit}</strong>.</p>
            <a href='{BOOKING_URL}?score={score}&issue={main_issue}' style='display:inline-block;background:#2e7d32;color:#fff;padding:14px 28px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:1.1em;'>
                Claim My Free Strategy Call (${STRATEGY_CALL_VALUE} value)
            </a>
            <p style='font-size:0.9em;color:#666;margin-top:15px'>No card required • 30 min • Actionable advice</p>
        </div>
    """

# ---------------------------------------------------------------------------
# End of file ---------------------------------------------------------------
