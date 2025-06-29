# File: services/seo_auditor.py
# Main SEO auditor service that orchestrates the audit process

import os
import logging
from typing import Dict
from services.web_scraper import scrape_website
from services.ai_service import analyze_with_ai
from services.report_generator import generate_pdf_report
from services.email_service import send_email_report
from models.database import save_audit_data

logger = logging.getLogger(__name__)

class SEOAuditor:
    def __init__(self):
        pass
    
    def run_full_audit(self, url: str, email: str) -> Dict:
        """Run complete SEO audit process"""
        try:
            logger.info(f'Starting audit for {url}')
            
            # Step 1: Scrape website
            website_data = scrape_website(url)
            if 'error' in website_data:
                raise Exception(f'Failed to analyze website: {website_data["error"]}')
            
            logger.info(f'Website scraped successfully for {url}')
            
            # Step 2: AI Analysis
            audit_data = analyze_with_ai(website_data)
            
            logger.info(f'AI analysis completed for {url}')
            
            # Step 3: Generate PDF Report
            pdf_path = generate_pdf_report(audit_data, website_data)
            
            logger.info(f'PDF report generated for {url}')
            
            # Step 4: Save to database
            save_audit_data(email, url, audit_data)
            
            logger.info(f'Audit data saved to database for {url}')
            
            # Step 5: Send email report
            email_sent = send_email_report(email, audit_data, pdf_path, url)
            
            if email_sent:
                logger.info(f'Email report sent successfully for {url}')
            else:
                logger.warning(f'Failed to send email report for {url}')
            
            # Prepare response data
            response_data = {
                'success': True,
                'score': audit_data.get('overall_score', 70),
                'issues': (audit_data.get('critical_issues', []) + 
                          audit_data.get('warnings', []) + 
                          audit_data.get('ai_search_issues', []))[:8],  # Limit to 8 issues for display
                'recommendations': audit_data.get('recommendations', [])[:5],  # Top 5 recommendations
                'pdf_path': f'reports/{os.path.basename(pdf_path)}',
                'categories': audit_data.get('category_scores', {}),
                'email_sent': email_sent,
                'quick_wins': audit_data.get('quick_wins', []),
                'voice_search_issues': audit_data.get('voice_search_issues', [])
            }
            
            logger.info(f'Audit completed successfully for {url} with score {response_data["score"]}')
            return response_data
            
        except Exception as e:
            logger.error(f'Audit failed for {url}: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_cached_report(self, email: str, cached_data: Dict, url: str) -> bool:
        """Send email report for cached audit data"""
        try:
            # Generate fresh PDF from cached data
            website_data = {'url': url}  # Minimal website data for PDF
            pdf_path = generate_pdf_report(cached_data, website_data)
            
            # Send email with cached data
            email_sent = send_email_report(email, cached_data, pdf_path, url)
            
            if email_sent:
                logger.info(f'Cached report sent successfully for {url}')
            else:
                logger.warning(f'Failed to send cached report for {url}')
            
            return email_sent
            
        except Exception as e:
            logger.error(f'Failed to send cached report for {url}: {str(e)}')
            return False