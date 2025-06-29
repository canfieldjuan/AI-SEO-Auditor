# File: services/email_service.py
# Email service using Resend - simple and works!

import os
from typing import Dict

def send_email_report(email: str, audit_data: Dict, pdf_path: str, website_url: str) -> bool:
    """Send detailed email report using Resend"""
    
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set in .env file")
        return False
    
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        
        # Prepare attachments
        attachments = []
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                content = f.read()
                attachments = [{
                    "filename": os.path.basename(pdf_path),
                    "content": list(content)  # Convert bytes to list
                }]
        
        # Get score
        overall_score = audit_data.get('overall_score', audit_data.get('score', 0))
        
        # Create email HTML
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #764ba2;">Your AI SEO Audit Results</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Overall Score: {overall_score}/100</h3>
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
        
        # Send email
        response = resend.Emails.send({
            "from": "SEO Auditor <onboarding@resend.dev>",
            "to": email,
            "subject": f"Your AI SEO Audit Results - {overall_score}/100",
            "html": html_body,
            "attachments": attachments
        })
        
        print(f"✅ Email sent successfully to {email} via Resend!")
        return True
        
    except ImportError:
        print("❌ Resend not installed. Run: pip install resend")
        return False
    except Exception as e:
        print(f"❌ Resend error: {e}")
        return False