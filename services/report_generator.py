# File: services/report_generator.py
# PDF report generation service for SEO audit results

import os
import urllib.parse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from typing import Dict
from config.settings import REPORTS_DIR

def generate_pdf_report(audit_data: Dict, website_data: Dict) -> str:
    """Generate comprehensive PDF report"""
    filename = f"audit_{urllib.parse.quote(website_data['url'].replace('https://', '').replace('http://', '').replace('/', '_'))}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    # Create reports directory if it doesn't exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#764ba2')
    )
    story.append(Paragraph("AI SEO Audit Report", title_style))
    story.append(Spacer(1, 20))
    
    # Website info
    story.append(Paragraph(f"<b>Website:</b> {website_data['url']}", styles['Normal']))
    story.append(Paragraph(f"<b>Audit Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(f"Overall AI Search Readiness Score: <b>{audit_data['overall_score']}/100</b>", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Category Scores
    if 'category_scores' in audit_data:
        story.append(Paragraph("Category Breakdown", styles['Heading2']))
        for category, score in audit_data['category_scores'].items():
            story.append(Paragraph(f"• {category.replace('_', ' ').title()}: {score}/100", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Critical Issues
    if audit_data.get('critical_issues'):
        story.append(Paragraph("Critical Issues", styles['Heading2']))
        for issue in audit_data['critical_issues']:
            story.append(Paragraph(f"• {issue}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Recommendations
    if audit_data.get('recommendations'):
        story.append(Paragraph("Priority Recommendations", styles['Heading2']))
        for rec in audit_data['recommendations']:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # AI Search Specific Issues
    if audit_data.get('ai_search_issues'):
        story.append(Paragraph("AI Search Optimization", styles['Heading2']))
        for issue in audit_data['ai_search_issues']:
            story.append(Paragraph(f"• {issue}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Voice Search Issues
    if audit_data.get('voice_search_issues'):
        story.append(Paragraph("Voice Search Optimization", styles['Heading2']))
        for issue in audit_data['voice_search_issues']:
            story.append(Paragraph(f"• {issue}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Quick Wins
    if audit_data.get('quick_wins'):
        story.append(Paragraph("Quick Wins", styles['Heading2']))
        for win in audit_data['quick_wins']:
            story.append(Paragraph(f"• {win}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    doc.build(story)
    return filepath