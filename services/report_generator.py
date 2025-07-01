# File: services/report_generator.py
# Enhanced PDF report generation - SIMPLE VERSION
# Just replace your existing report_generator.py with this

from __future__ import annotations
import os
import urllib.parse
import html
from datetime import datetime
from typing import Dict, List, Optional  # FIX: Added the missing import

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)

from config.settings import REPORTS_DIR

# Default visitor value if not in settings
VISITOR_VALUE_USD = 50


def generate_pdf_report(audit_data: Dict, website_data: Dict) -> Optional[str]:
    """Enhanced PDF report using only existing data"""
    
    # Build filename (same as before)
    slug = urllib.parse.quote(
        website_data["url"].replace("https://", "").replace("http://", "").rstrip("/"),
        safe="",
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_{slug}_{timestamp}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    try:
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Enhanced styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=28,
            textColor=colors.HexColor("#764ba2"),
            spaceAfter=30,
            alignment=1,  # Center
        )
        
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=18,
            textColor=colors.HexColor("#764ba2"),
            spaceAfter=20,
            spaceBefore=20,
        )
        
        # ENHANCED TITLE PAGE
        story.append(Paragraph("AI SEO AUDIT REPORT", title_style))
        story.append(Spacer(1, 30))
        
        # Executive Summary Box
        url_display = html.escape(website_data["url"])
        score = audit_data.get("overall_score", audit_data.get("score", 0))
        critical_count = len(audit_data.get("critical_issues", []))
        traffic_loss = audit_data.get("estimated_monthly_traffic_loss", 500)  # Default estimate
        revenue_loss = traffic_loss * VISITOR_VALUE_USD
        
        exec_data = [
            ["Website:", url_display],
            ["Audit Date:", datetime.now().strftime('%B %d, %Y')],
            ["Overall Score:", f"{score}/100"],
            ["Critical Issues:", str(critical_count)],
            ["Est. Monthly Traffic Loss:", f"{traffic_loss:,} visitors"],
            ["Est. Revenue Impact:", f"${revenue_loss:,}/month"],
        ]
        
        exec_table = Table(exec_data, colWidths=[2.5*inch, 3.5*inch])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(exec_table)
        story.append(Spacer(1, 30))
        
        # Score interpretation
        if score >= 80:
            interpretation = "Excellent - Your site is well-optimized for AI search"
            action = "Focus on maintaining your advantage and fine-tuning"
        elif score >= 60:
            interpretation = "Good - But missing key optimizations competitors use"
            action = "Implement our priority fixes to jump ahead"
        else:
            interpretation = "Critical - Your site is nearly invisible to AI search"
            action = "Urgent action needed to prevent further traffic loss"
            
        story.append(Paragraph(f"<b>Assessment:</b> {interpretation}", styles["Normal"]))
        story.append(Paragraph(f"<b>Recommended Action:</b> {action}", styles["Normal"]))
        
        story.append(PageBreak())
        
        # CATEGORY SCORES WITH INTERPRETATION
        story.append(Paragraph("Performance by Category", section_style))
        
        categories = audit_data.get("category_scores", audit_data.get("categories", {}))
        if categories:
            cat_data = [["Category", "Score", "Status", "Priority"]]
            
            for cat, score in categories.items():
                cat_name = cat.replace("_", " ").title()
                
                # Add status and priority based on score
                if score >= 80:
                    status = "Strong"
                    priority = "Maintain"
                elif score >= 60:
                    status = "Moderate"
                    priority = "Improve"
                else:
                    status = "Weak"
                    priority = "Critical"
                    
                cat_data.append([cat_name, f"{score}/100", status, priority])
            
            cat_table = Table(cat_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(cat_table)
        
        story.append(Spacer(1, 30))
        
        # PRIORITY ACTION PLAN (Quick Wins First)
        story.append(Paragraph("Priority Action Plan", section_style))
        story.append(Paragraph(
            "We've organized issues by impact and effort. Start with Quick Wins for immediate results:",
            styles["Normal"]
        ))
        story.append(Spacer(1, 15))
        
        # Quick Wins Section
        if audit_data.get("quick_wins"):
            story.append(Paragraph("<b>🎯 Quick Wins (Do These First!)</b>", styles["Normal"]))
            story.append(Paragraph("High impact, low effort - can be done in hours:", styles["Normal"]))
            story.append(Spacer(1, 10))
            
            for i, win in enumerate(audit_data["quick_wins"][:5], 1):
                story.append(Paragraph(f"{i}. {html.escape(win)}", styles["Normal"]))
                story.append(Paragraph(f"   <i>Estimated time: 30-60 minutes</i>", styles["Normal"]))
                story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        
        # Critical Issues with Details
        story.append(Paragraph("<b>⚠️ Critical Issues (Address Within 30 Days)</b>", styles["Normal"]))
        story.append(Spacer(1, 10))
        
        for i, issue in enumerate(audit_data.get("critical_issues", [])[:5], 1):
            story.append(Paragraph(f"<b>Issue {i}:</b> {html.escape(issue)}", styles["Normal"]))
            
            # Add helpful context based on issue type
            if "schema" in issue.lower():
                story.append(Paragraph(
                    "→ <i>Why it matters: AI systems use schema to understand your content. "
                    "Without it, you're invisible to AI-powered features.</i>",
                    styles["Normal"]
                ))
                story.append(Paragraph(
                    "→ <i>How to fix: Add JSON-LD structured data to your pages. "
                    "Use Google's Structured Data Testing Tool to validate.</i>",
                    styles["Normal"]
                ))
            elif "alt" in issue.lower():
                story.append(Paragraph(
                    "→ <i>Why it matters: AI can't 'see' images without alt text. "
                    "You're missing voice search and accessibility traffic.</i>",
                    styles["Normal"]
                ))
                story.append(Paragraph(
                    "→ <i>How to fix: Add descriptive alt text (5-15 words) to all images. "
                    "Include your target keywords naturally.</i>",
                    styles["Normal"]
                ))
            elif "h1" in issue.lower() or "heading" in issue.lower():
                story.append(Paragraph(
                    "→ <i>Why it matters: H1 tags tell AI the main topic of your page. "
                    "Missing H1s confuse AI about your content.</i>",
                    styles["Normal"]
                ))
                story.append(Paragraph(
                    "→ <i>How to fix: Add one clear H1 per page with your main keyword. "
                    "Keep it under 60 characters.</i>",
                    styles["Normal"]
                ))
            else:
                story.append(Paragraph(
                    "→ <i>Impact: This issue affects your visibility in AI search results.</i>",
                    styles["Normal"]
                ))
            
            story.append(Spacer(1, 15))
        
        story.append(PageBreak())
        
        # ESTIMATED IMPACT SECTION
        story.append(Paragraph("Expected Results Timeline", section_style))
        
        timeline_data = [
            ["Timeframe", "Actions", "Expected Results"],
            ["Week 1-2", "Complete Quick Wins", "+5-10% AI visibility"],
            ["Month 1", "Fix Critical Issues", "+15-25% search traffic"],
            ["Month 2-3", "Full Optimization", "+40-60% overall visibility"],
            ["Month 6", "Ongoing Refinement", "2-3x organic traffic"],
        ]
        
        timeline_table = Table(timeline_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(timeline_table)
        
        story.append(Spacer(1, 30))
        
        # AI & VOICE SEARCH SPECIFIC ISSUES
        if audit_data.get("ai_search_issues") or audit_data.get("voice_search_issues"):
            story.append(Paragraph("AI & Voice Search Optimization", section_style))
            
            if audit_data.get("ai_search_issues"):
                story.append(Paragraph("<b>AI Search Issues:</b>", styles["Normal"]))
                for issue in audit_data["ai_search_issues"][:3]:
                    story.append(Paragraph(f"• {html.escape(issue)}", styles["Normal"]))
                story.append(Spacer(1, 15))
            
            if audit_data.get("voice_search_issues"):
                story.append(Paragraph("<b>Voice Search Issues:</b>", styles["Normal"]))
                for issue in audit_data["voice_search_issues"][:3]:
                    story.append(Paragraph(f"• {html.escape(issue)}", styles["Normal"]))
        
        story.append(Spacer(1, 30))
        
        # NEXT STEPS SECTION
        story.append(Paragraph("Your Next Steps", section_style))
        
        next_steps = [
            "1. Start with the Quick Wins - these can be done today",
            "2. Schedule time to address Critical Issues (aim for 1-2 per week)",
            "3. Monitor your scores in Google Search Console",
            "4. Re-audit in 60 days to track improvement",
            "5. Consider professional help for complex technical issues"
        ]
        
        for step in next_steps:
            story.append(Paragraph(step, styles["Normal"]))
            story.append(Spacer(1, 5))
        
        # Build PDF
        doc.build(story)
        return filepath
        
    except Exception as exc:
        print(f"❌ PDF generation failed: {exc}")
        return None