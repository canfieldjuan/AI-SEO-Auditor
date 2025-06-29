# File: services/email_service.py
# Email service for sending audit reports and notifications

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict
from config.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS

def send_email_report(email: str, audit_data: Dict, pdf_path: str, website_url: str) -> bool:
    """Send detailed email report"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = f"Your AI SEO Audit Results - {audit_data['overall_score']}/100"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #764ba2;">Your AI SEO Audit Results</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Overall Score: {audit_data['overall_score']}/100</h3>
                <p><strong>Website:</strong> {website_url}</p>
            </div>
            
            <h3>Critical Issues Found:</h3>
            <ul>
                {''.join([f'<li>{issue}</li>' for issue in audit_data.get('critical_issues', [])])}
            </ul>
            
            <h3>Priority Recommendations:</h3>
            <ul>
                {''.join([f'<li>{rec}</li>' for rec in audit_data.get('recommendations', [])])}
            </ul>
            
            <h3>AI Search Specific Issues:</h3>
            <ul>
                {''.join([f'<li>{issue}</li>' for issue in audit_data.get('ai_search_issues', [])])}
            </ul>
            
            <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Ready to Fix These Issues?</h3>
                <p>Our AI-Enhanced SEO specialists can help you implement these recommendations and dominate AI search results.</p>
                <p><a href="https://calendly.com/your-calendar" style="background: #764ba2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Book Your Free Strategy Call</a></p>
            </div>
            
            <p>Best regards,<br>
            The AI-Enhanced SEO Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Attach PDF report
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(pdf_path)}'
            )
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False