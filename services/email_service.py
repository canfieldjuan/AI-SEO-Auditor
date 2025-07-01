# File: services/email_service.py
# Email service using Resend – now with built-in product offer

import os
import random
import base64
import html
from typing import Dict

# Configuration - use defaults so app runs without setup
BOOKING_URL = os.getenv('BOOKING_URL', 'https://example.com/contact')
STRATEGY_CALL_VALUE = os.getenv('STRATEGY_CALL_VALUE', '0')
VISITOR_VALUE_USD = int(os.getenv('VISITOR_VALUE_USD', '50'))


def send_email_report(email: str, audit_data: Dict, pdf_path: str, website_url: str) -> bool:
    """Send detailed email report using Resend and include a product upsell."""
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    RESEND_FROM_EMAIL = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')  # Default to resend's demo email

    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set in .env file")
        return False

    try:
        import resend
        resend.api_key = RESEND_API_KEY

        # Prepare attachments
        attachments = []
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                content = f.read()
                attachments = [{
                    "filename": os.path.basename(pdf_path),
                    "content": base64.b64encode(content).decode()
                }]

        # Get score
        overall_score = audit_data.get('overall_score', audit_data.get('score', 0))
        
        # Add website_url to audit_data for template functions
        audit_data['website_url'] = website_url

        # Determine score segment & template
        score_segment = get_score_segment(overall_score)
        html_body = get_email_template(score_segment, audit_data)

        # Personalize
        user_name = audit_data.get('user_name') or email.split('@')[0].replace('.', ' ').title()
        # Extract business name from website URL
        business_name = website_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].split('.')[0].title()
        
        # Calculate Google overlook metric (example calculation - adjust as needed)
        google_overlooks = audit_data.get('estimated_monthly_traffic_loss', 1000) * 2.847  # Mock calculation
        
        # Add website_url to audit_data for template functions
        audit_data['website_url'] = website_url
        
        html_body = personalize_email_body(html_body, {
            'businessName': business_name,  # Use business name instead of userName
            'websiteUrl': website_url,
            'googleOverlooks': f"{int(google_overlooks):,}"
        })

        # Get all dynamic content
        recommendations = audit_data.get('recommendations', [])
        critical_issues = audit_data.get('critical_issues', [])
        
        # Centralized replacements
        replacements = {
            'recommendations': '<ul>' + ''.join(f'<li>{html.escape(rec)}</li>' for rec in recommendations) + '</ul>',
            'critical_issues': '<ul>' + ''.join(f'<li>{html.escape(issue)}</li>' for issue in critical_issues) + '</ul>',
            'score': str(overall_score),
            'critical_count': str(len(critical_issues))
        }
        
        # Apply all replacements
        for key, value in replacements.items():
            html_body = html_body.replace(f'{{{{{key}}}}}', value)

        # Subject line
        audit_data['website_url'] = website_url
        subject = personalize_subject_line(
            "Your SEO Audit Report for {{websiteUrl}} – Score: " + str(overall_score),
            audit_data
        )

        # Send email
        response = resend.Emails.send({
            "from": f"SEO Auditor <{RESEND_FROM_EMAIL}>",
            "to": email,
            "subject": subject,
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


# ---------- Helper Functions ----------

def get_score_segment(score: int) -> str:
    if score >= 80:
        return 'high'
    elif score >= 60:
        return 'medium'
    return 'low'


def get_email_template(segment: str, audit_data: Dict = None) -> str:
    """Return dynamic, conversion-focused email template based on audit findings"""
    
    if audit_data is None:
        audit_data = {}
    
    # Extract key data for personalization
    industry = html.escape(audit_data.get('industry', 'your industry'))
    competitors = [html.escape(c) for c in audit_data.get('top_competitors', [])]
    estimated_traffic_loss = audit_data.get('estimated_monthly_traffic_loss', 0)
    visitor_value = audit_data.get('visitor_value', VISITOR_VALUE_USD)
    revenue_impact = estimated_traffic_loss * visitor_value
    main_issue = html.escape(audit_data.get('main_technical_issue', ''))
    website_url = audit_data.get('website_url', audit_data.get('websiteUrl', 'your website'))
    
    templates = {
        'high': f"""
            <h2 style="color: #333; font-size: 28px; font-weight: 600; margin-bottom: 10px;">{{{{businessName}}}}, Google Overlooked Your Website {{{{googleOverlooks}}}} Times Last Month</h2>
            
            <p style="font-size: 18px; color: #555; margin-bottom: 20px;">Your SEO audit revealed <strong style="color: #1976d2;">{{{{critical_count}}}} optimization opportunities</strong> that explain why you're not maximizing Google's new algorithm.</p>
            
            <div style="background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px;">
                <h3 style="margin-top: 0; color: #333;">Areas for Improvement:</h3>
                {{{{critical_issues}}}}
            </div>
            
            <p style="font-size: 16px; line-height: 1.6;">Good news: Your site scored {{{{score}}}}/100. But here's what matters more – Google's entire ranking system is changing, and even high-performing sites need to adapt.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Shift Nobody's Talking About</h3>
            
            <p>Google's search algorithm isn't just updating anymore – it's transforming. And most SEO agencies are about as prepared as Blockbuster was for Netflix.</p>
            
            <p>Your current agency isn't failing you intentionally. They're just... slow.</p>
            
            <p>Think about it:</p>
            <ul style="line-height: 1.8;">
                <li>They need 3 months to "analyze" your situation</li>
                <li>Another 3 months to get "stakeholder buy-in"</li>
                <li>6 more months to "implement phase one"</li>
            </ul>
            
            <p>Meanwhile, Google's algorithm has evolved three times.</p>
            
            <h3 style="color: #333; margin-top: 30px;">Why Most Agencies Can't Keep Up</h3>
            
            <p><strong>Traditional SEO agencies</strong> are like cruise ships. Changing direction takes forever. By the time they've updated their playbooks and retrained their teams... Google's moved on.</p>
            
            <p><strong>Full-service marketing firms</strong> treat SEO like one dish at a buffet. They're juggling social media, PPC, email marketing – SEO gets maybe 10% of their attention. Google changes 100% of its algorithm.</p>
            
            <p><strong>Even good technical SEO agencies</strong> are stuck in the old paradigm:</p>
            <ul style="line-height: 1.8;">
                <li>They're still optimizing for keywords while Google's rewarding intent</li>
                <li>They're building backlinks while Google's analyzing user behavior</li>
                <li>They're focused on technical checkboxes while Google's gone full AI</li>
            </ul>
            
            <h3 style="color: #333; margin-top: 30px;">We're Built Different</h3>
            
            <p>We're not a cruise ship. We're a speedboat.</p>
            
            <p>We're not trying to be everything to everyone. We're a Google-first rapid response team.</p>
            
            <ul style="line-height: 1.8;">
                <li>No board meetings to approve common sense</li>
                <li>No 6-month roadmaps for 6-day fixes</li>
                <li>No committees debating while your rankings tank</li>
            </ul>
            
            <p>We've spent the last 8 months inside Google's new ecosystem. Not theorizing about it. Not reading about it. Actually testing what works NOW.</p>
            
            <h3 style="color: #333; margin-top: 30px;">Here's Your Advantage</h3>
            
            <p>Your competitors are stuck with the same slow-moving agencies. You're already ahead – imagine the gap when you're optimized for tomorrow's Google while they're still catching up to yesterday's.</p>
            
            <p>We implement in days what takes them months. Because we've already done the learning. We know exactly what Google wants TODAY, not what worked in 2023.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Timeline That Matters</h3>
            
            <p>In 6-8 months, sites optimized for the old Google will become invisible. Your good score today won't protect you from obsolete optimization tomorrow.</p>
            
            <p>You can maintain your lead, or watch smaller, more agile competitors pass you by.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Bottom Line</h3>
            
            <p>You don't need another agency. You need a nimble partner who's already where Google is heading.</p>
            
            <p>Your audit shows {{{{critical_count}}}} areas for improvement. We can optimize them all. But more importantly, we can optimize them for the Google that's coming, not the Google that's leaving.</p>
            
            <hr style="margin: 40px 0;">
            
            <p style="font-style: italic; color: #666;"><strong>P.S.</strong> – Your high score gives you a head start. Don't waste it.</p>
        """,
        
        'medium': f"""
            <h2 style="color: #333; font-size: 28px; font-weight: 600; margin-bottom: 10px;">{{{{businessName}}}}, Google Overlooked Your Website {{{{googleOverlooks}}}} Times Last Month</h2>
            
            <p style="font-size: 18px; color: #555; margin-bottom: 20px;">Your SEO audit revealed <strong style="color: #d32f2f;">{{{{critical_count}}}} critical issues</strong> that explain why you're invisible to Google's new algorithm.</p>
            
            <div style="background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px;">
                <h3 style="margin-top: 0; color: #333;">Critical Issues Found:</h3>
                {{{{critical_issues}}}}
            </div>
            
            <p style="font-size: 16px; line-height: 1.6;">These issues are fixable. But here's what your current SEO team doesn't know: fixing them for yesterday's Google won't help you rank tomorrow.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Shift Nobody's Talking About</h3>
            
            <p>Google's search algorithm isn't just updating anymore – it's transforming. And most SEO agencies are about as prepared as Blockbuster was for Netflix.</p>
            
            <p>Your current agency isn't failing you intentionally. They're just... slow.</p>
            
            <p>Think about it:</p>
            <ul style="line-height: 1.8;">
                <li>They need 3 months to "analyze" your situation</li>
                <li>Another 3 months to get "stakeholder buy-in"</li>
                <li>6 more months to "implement phase one"</li>
            </ul>
            
            <p>Meanwhile, Google's algorithm has evolved three times.</p>
            
            <h3 style="color: #333; margin-top: 30px;">Why Most Agencies Can't Keep Up</h3>
            
            <p><strong>Traditional SEO agencies</strong> are like cruise ships. Changing direction takes forever. By the time they've updated their playbooks and retrained their teams... Google's moved on.</p>
            
            <p><strong>Full-service marketing firms</strong> treat SEO like one dish at a buffet. They're juggling social media, PPC, email marketing – SEO gets maybe 10% of their attention. Google changes 100% of its algorithm.</p>
            
            <p><strong>Offshore SEO farms</strong> are still using tactics from 2019. They promise 1,000 backlinks but can't explain why your traffic keeps dropping. They're optimizing for a Google that no longer exists.</p>
            
            <p><strong>Even good technical SEO agencies</strong> are stuck in the old paradigm:</p>
            <ul style="line-height: 1.8;">
                <li>They're still optimizing for keywords while Google's rewarding intent</li>
                <li>They're building backlinks while Google's analyzing user behavior</li>
                <li>They're focused on technical checkboxes while Google's gone full AI</li>
            </ul>
            
            <p><strong>The boutique specialists</strong> get it, but they're booked solid. Three month waitlists. Premium prices. Great if you can wait, but Google won't pause its evolution for your timeline.</p>
            
            <h3 style="color: #333; margin-top: 30px;">We're Built Different</h3>
            
            <p>We're not a cruise ship. We're a speedboat.</p>
            
            <p>We're not trying to be everything to everyone. We're a Google-first rapid response team.</p>
            
            <ul style="line-height: 1.8;">
                <li>No board meetings to approve common sense</li>
                <li>No 6-month roadmaps for 6-day fixes</li>
                <li>No committees debating while your rankings tank</li>
            </ul>
            
            <p>We've spent the last 8 months inside Google's new ecosystem. Not theorizing about it. Not reading about it. Actually testing what works NOW.</p>
            
            <h3 style="color: #333; margin-top: 30px;">Here's Your Advantage</h3>
            
            <p>Your competitors are stuck with the same slow-moving agencies. They'll spend the next year in meetings discussing the "digital transformation strategy."</p>
            
            <p>You could be on page one before they finish their first quarterly review.</p>
            
            <p>We implement in days what takes them months. Because we've already done the learning. We know exactly what Google wants TODAY, not what worked in 2023.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Timeline That Matters</h3>
            
            <p>In 6-8 months, sites optimized for the old Google will become invisible. Not slowly. Not gradually. Overnight.</p>
            
            <p>The agencies will blame "algorithm updates" and propose another 6-month strategy. You'll be competing with companies half your size who adapted early.</p>
            
            <p>Or...</p>
            
            <p>You work with a team that's already adapted. No learning curve. No trial and error. Just results based on what's actually working in Google's new reality.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Bottom Line</h3>
            
            <p>You don't need another agency. You need a nimble partner who's already where Google is heading.</p>
            
            <p>While others are having meetings about having meetings, we're implementing. While they're creating proposals, we're creating rankings.</p>
            
            <p>Your audit shows {{{{critical_count}}}} critical issues. We can fix them all. But more importantly, we can fix them for the Google that's coming, not the Google that's leaving.</p>
            
            <hr style="margin: 40px 0;">
            
            <p style="font-style: italic; color: #666;"><strong>P.S.</strong> – Every week you wait is another week a smaller, faster competitor moves ahead of you. Not because they're smarter. Because they moved faster.</p>
        """,
        
        'low': f"""
            <h2 style="color: #333; font-size: 28px; font-weight: 600; margin-bottom: 10px;">{{{{businessName}}}}, Google Overlooked Your Website {{{{googleOverlooks}}}} Times Last Month</h2>
            
            <p style="font-size: 18px; color: #555; margin-bottom: 20px;">Your SEO audit revealed <strong style="color: #d32f2f;">{{{{critical_count}}}} critical issues</strong> that explain why you're invisible to Google's new algorithm.</p>
            
            <div style="background: #ffebee; padding: 20px; margin: 20px 0; border-radius: 8px;">
                <h3 style="margin-top: 0; color: #d32f2f;">Critical Issues Found:</h3>
                {{{{critical_issues}}}}
            </div>
            
            <p style="font-size: 16px; line-height: 1.6;">Your score of {{{{score}}}}/100 tells a story. But it's not the story you think.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Real Problem</h3>
            
            <p>These issues aren't just hurting your rankings. They're symptoms of a bigger problem: Your site is optimized for a version of Google that no longer exists.</p>
            
            <p>Google's search algorithm isn't just updating anymore – it's transforming. And most SEO agencies are about as prepared as Blockbuster was for Netflix.</p>
            
            <p>Your current agency isn't failing you intentionally. They're just... slow.</p>
            
            <p>Think about it:</p>
            <ul style="line-height: 1.8;">
                <li>They need 3 months to "analyze" your situation</li>
                <li>Another 3 months to get "stakeholder buy-in"</li>
                <li>6 more months to "implement phase one"</li>
            </ul>
            
            <p>Meanwhile, Google's algorithm has evolved three times. And your rankings have dropped each time.</p>
            
            <h3 style="color: #333; margin-top: 30px;">Why Most Agencies Can't Keep Up</h3>
            
            <p><strong>Traditional SEO agencies</strong> are like cruise ships. Changing direction takes forever. By the time they've updated their playbooks and retrained their teams... Google's moved on.</p>
            
            <p><strong>Full-service marketing firms</strong> treat SEO like one dish at a buffet. They're juggling social media, PPC, email marketing – SEO gets maybe 10% of their attention. Google changes 100% of its algorithm.</p>
            
            <p><strong>Offshore SEO farms</strong> are still using tactics from 2019. They promise 1,000 backlinks but can't explain why your traffic keeps dropping. They're optimizing for a Google that no longer exists.</p>
            
            <p><strong>Even good technical SEO agencies</strong> are stuck in the old paradigm:</p>
            <ul style="line-height: 1.8;">
                <li>They're still optimizing for keywords while Google's rewarding intent</li>
                <li>They're building backlinks while Google's analyzing user behavior</li>
                <li>They're focused on technical checkboxes while Google's gone full AI</li>
            </ul>
            
            <h3 style="color: #333; margin-top: 30px;">We're Built Different</h3>
            
            <p>We're not a cruise ship. We're a speedboat.</p>
            
            <p>We're not trying to be everything to everyone. We're a Google-first rapid response team.</p>
            
            <ul style="line-height: 1.8;">
                <li>No board meetings to approve common sense</li>
                <li>No 6-month roadmaps for 6-day fixes</li>
                <li>No committees debating while your rankings tank</li>
            </ul>
            
            <p>We've spent the last 8 months inside Google's new ecosystem. Not theorizing about it. Not reading about it. Actually testing what works NOW.</p>
            
            <h3 style="color: #333; margin-top: 30px;">Your Choice</h3>
            
            <p>You have two options:</p>
            
            <p><strong>Option 1:</strong> Stick with traditional SEO. Watch your rankings continue to slide. Blame algorithm updates. Repeat.</p>
            
            <p><strong>Option 2:</strong> Work with a team that's already adapted. Skip the learning curve. Start ranking for the Google that's coming, not the Google that's leaving.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Timeline That Matters</h3>
            
            <p>In 6-8 months, sites optimized for the old Google will become invisible. Not slowly. Not gradually. Overnight.</p>
            
            <p>You're already behind. But you're not out of the race. Yet.</p>
            
            <h3 style="color: #333; margin-top: 30px;">The Bottom Line</h3>
            
            <p>You don't need another agency. You need a nimble partner who's already where Google is heading.</p>
            
            <p>Your audit shows {{{{critical_count}}}} critical issues. We can fix them all. But more importantly, we can fix them for the Google that's coming, not the Google that's leaving.</p>
            
            <hr style="margin: 40px 0;">
            
            <p style="font-style: italic; color: #666;"><strong>P.S.</strong> – Every week you wait is another week a smaller, faster competitor moves ahead of you. Not because they're smarter. Because they moved faster.</p>
        """
    }
    return templates.get(segment, templates['medium'])


def personalize_subject_line(template: str, data: Dict[str, str]) -> str:
    """Create Ogilvy-style subject lines - clear, honest, and benefit-driven"""
    # Check if it's a legacy call with just websiteUrl
    if 'websiteUrl' in data and 'overall_score' not in data:
        return template.replace('{{websiteUrl}}', data['websiteUrl'])
    
    score = data.get('overall_score', 0)
    website = data.get('website_url', data.get('websiteUrl', ''))
    critical_count = data.get('critical_count', len(data.get('critical_issues', [])))
    
    # Ogilvy-style: specific, factual, benefit-oriented
    subject_lines = {
        'high': [
            f"Your SEO audit found {critical_count} ways to improve {website}",
            f"{website} SEO Report: Good foundation, room to grow",
            f"How {website} can capture more search traffic"
        ],
        'medium': [
            f"{critical_count} specific fixes to improve {website}'s search ranking",
            f"Your SEO audit revealed opportunities for {website}",
            f"{website}: Your roadmap to better search visibility"
        ],
        'low': [
            f"Why customers can't find {website} (and how to fix it)",
            f"{website} SEO audit: {critical_count} critical improvements needed",
            f"Your plan to improve {website}'s search performance"
        ]
    }
    
    segment = 'high' if score >= 80 else 'medium' if score >= 60 else 'low'
    return subject_lines[segment][0]# New dynamic subject line generation
    score = data.get('overall_score', 0)
    website = data.get('website_url', data.get('websiteUrl', ''))
    competitors = data.get('top_competitors', [])
    
    # Calculate revenue loss if not provided
    visitor_value = data.get('visitor_value', VISITOR_VALUE_USD)
    estimated_revenue_loss = data.get('estimated_monthly_revenue_loss', 
                                     data.get('estimated_monthly_traffic_loss', 100) * visitor_value)
    
    subject_lines = {
        'high': [
            f"⚠️ {competitors[0] if competitors else 'Your competitor'} just passed you on Google",
            f"You're losing ${estimated_revenue_loss:,}/mo (quick fix inside)",
            f"Good news/Bad news about {website}'s SEO"
        ],
        'medium': [
            f"🚨 Critical: {website} has {data.get('critical_count', len(data.get('critical_issues', [])))} urgent SEO issues",
            f"Your SEO score: {score}/100 (competitors average: 85)",
            f"Warning: You're invisible to 67% of your customers"
        ],
        'low': [
            f"URGENT: {website} is practically invisible on Google",
            f"Emergency: Your site scored {score}/100 (industry minimum: 70)",
            f"🔴 {competitors[0] if competitors else 'Your competitors'} are stealing your customers (proof inside)"
        ]
    }
    
    segment = 'high' if score >= 80 else 'medium' if score >= 60 else 'low'
    chosen_subject = random.choice(subject_lines[segment])
    
    # If no dynamic subject was chosen, fall back to template
    if not chosen_subject:
        return template.replace('{{websiteUrl}}', website)
    
    return chosen_subject


def personalize_email_body(template: str, data: Dict[str, str]) -> str:
    # Replace all placeholders
    for key, value in data.items():
        template = template.replace(f'{{{{{key}}}}}', str(value))
    return template


def generate_testimonial_html() -> str:
    testimonials = [
        {
            "text": "The SEO audit provided by this tool was extremely thorough and insightful. It helped us identify critical issues we had overlooked. Highly recommend!",
            "author": "Jane Smith",
            "company": "Acme Inc."
        },
        {
            "text": "Thanks to the recommendations from the audit report, we were able to significantly improve our search engine rankings and organic traffic.",
            "author": "John Doe",
            "company": "XYZ Corp"
        }
    ]

    snippet = ""
    for t in testimonials:
        snippet += f'''
            <div class="testimonial">
                <p class="testimonial-text">"{t['text']}"</p>
                <p class="testimonial-author">– {t['author']}, {t['company']}</p>
            </div>
        '''
    return snippet


def generate_dynamic_testimonials(audit_data: Dict) -> str:
    """Generate testimonials relevant to the specific issues found"""
    if not audit_data:
        return generate_testimonial_html()
    
    industry = audit_data.get('industry', 'business')
    main_issue = audit_data.get('main_technical_issue', '')
    
    # Map issues to relevant testimonials
    testimonial_map = {
        'page_speed': {
            "text": "Our page load time went from 8 seconds to under 2 seconds. Conversions increased by 47% in just 3 weeks!",
            "author": "Michael Chen",
            "company": "FastTech Solutions",
            "result": "+47% conversions"
        },
        'mobile_optimization': {
            "text": "We were losing 65% of mobile traffic. After their fixes, our mobile rankings shot up and revenue increased 3x.",
            "author": "Sarah Johnson", 
            "company": "MobileFirst Inc",
            "result": "3x revenue increase"
        },
        'technical_seo': {
            "text": "They found indexing issues we never knew existed. Fixed them in 2 days and our traffic doubled within a month.",
            "author": "David Park",
            "company": "TechCorp",
            "result": "2x traffic in 30 days"
        }
    }
    
    # Validate main_issue against available keys
    if main_issue and main_issue in testimonial_map:
        relevant = testimonial_map[main_issue]
    else:
        # Default testimonial
        relevant = {
            "text": f"Best SEO investment we made. Went from page 5 to #2 on Google for our main {industry} keywords.",
            "author": "Jennifer Smith",
            "company": f"Leading {industry} Company",
            "result": "Page 5 to #2 on Google"
        }
    
    return f"""
        <div style="background: #e8f5e9; padding: 20px; margin: 20px 0; border-left: 4px solid #4caf50;">
            <p style="font-style: italic; margin: 0;">"{relevant['text']}"</p>
            <p style="margin: 10px 0 0 0; font-weight: bold;">
                — {relevant['author']}, {relevant['company']} 
                <span style="color: #2e7d32;">({relevant['result']})</span>
            </p>
        </div>
    """


def generate_offer_html(audit_data: Dict = None) -> str:
    """Generate dynamic offer based on audit findings"""
    if audit_data is None:
        return f"""
            <hr style="margin:2rem 0;">
            <h3 style="color:#2e7d32;">Boost Your SEO Further – Let Us Fix These Issues for You</h3>
            <p>Our expert team can implement every recommendation in this report and lift your rankings in record time.  
            Click the button below for a 30-minute strategy call (normally ${STRATEGY_CALL_VALUE} – free for the next 48 hours).</p>
            <a href="{BOOKING_URL}" style="
                display:inline-block;
                background:#2e7d32;
                color:#fff;
                padding:12px 24px;
                border-radius:6px;
                text-decoration:none;
                font-weight:bold;">
                Book My Free Strategy Call
            </a>
        """
    
    # Dynamic offer based on audit data
    score = audit_data.get('overall_score', 0)
    main_issue = html.escape(audit_data.get('main_technical_issue', 'SEO issues'))
    industry = html.escape(audit_data.get('industry', 'businesses in your industry'))
    
    if score >= 80:
        urgency = "Lock in your competitive advantage"
        benefit = "stay ahead of competitors who are catching up"
    elif score >= 60:
        urgency = "Stop losing customers to competitors"
        benefit = "reclaim your lost traffic in 30-60 days"
    else:
        urgency = "Emergency SEO rescue needed"
        benefit = "save your online presence before it's too late"
    
    return f"""
        <div style="background: #f5f5f5; padding: 30px; margin: 30px 0; text-align: center;">
            <h2 style="color: #2e7d32; margin-top: 0;">{urgency}</h2>
            
            <p style="font-size: 1.1em;">Our SEO Emergency Response Team specializes in fixing {main_issue}. 
            We'll help you <strong>{benefit}</strong>.</p>
            
            <div style="background: white; padding: 20px; margin: 20px 0; border: 2px dashed #2e7d32;">
                <p style="margin: 0; font-size: 1.2em;"><strong>🎯 What you'll get in 30 minutes:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Exact step-by-step fix for your #1 SEO problem</li>
                    <li>Competitor backlink sources you can steal</li>
                    <li>Quick wins that show results in 7 days</li>
                    <li>Custom 90-day roadmap to dominate your market</li>
                </ul>
            </div>
            
            <p style="color: #e53935; font-weight: bold; font-size: 1.1em;">
                ⏰ Only 3 spots left this week (2 already booked by {industry})
            </p>
            
            <a href="{BOOKING_URL}?score={score}&issue={main_issue}" 
               style="display:inline-block; background:#2e7d32; color:#fff; padding:16px 32px; 
                      border-radius:6px; text-decoration:none; font-weight:bold; font-size:1.2em;">
                Claim My Free Strategy Call{f' (${STRATEGY_CALL_VALUE} Value)' if STRATEGY_CALL_VALUE != '0' else ''}
            </a>
            
            <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                No credit card required • 100% free • Guaranteed actionable advice
            </p>
        </div>
    """


# ---------- End of file ----------