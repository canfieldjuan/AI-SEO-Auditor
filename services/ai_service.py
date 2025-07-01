# File: services/ai_service.py
# AI service with OpenAI and OpenRouter fallback

import openai
import requests
import json
from typing import Dict
from config.settings import OPENAI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def analyze_with_ai(website_data: Dict) -> Dict:
    """Use AI to analyze website content for AI search optimization"""
    
    prompt = f"""
    Analyze this website for AI search optimization and provide a comprehensive SEO audit.
    
    Website Data:
    URL: {website_data.get('url', 'N/A')}
    Title: {website_data.get('title', 'N/A')}
    Meta Description: {website_data.get('meta_description', 'N/A')}
    H1 Tags: {website_data.get('h1_tags', [])}
    Content Length: {website_data.get('content_length', 0)} characters
    Has Schema: {website_data.get('has_schema', False)}
    Schema Types: {website_data.get('schema_types', [])}
    Images without Alt: {website_data.get('images_without_alt', 0)}/{website_data.get('images', 0)}
    SSL Certificate: {website_data.get('ssl_certificate', False)}
    
    Content Sample: {website_data.get('content_text', '')[:2000]}
    
    Provide analysis in this JSON format:
    {{
        "overall_score": 0-100,
        "category_scores": {{
            "technical_seo": 0-100,
            "content_quality": 0-100,
            "ai_readiness": 0-100,
            "voice_search": 0-100,
            "schema_markup": 0-100
        }},
        "critical_issues": [
            "Specific critical issues found (list 3-5 major problems)"
        ],
        "warnings": [
            "Important issues to address"
        ],
        "recommendations": [
            "Specific actionable recommendations (list 3-5 key fixes)"
        ],
        "ai_search_issues": [
            "Issues specifically related to AI search visibility"
        ],
        "voice_search_issues": [
            "Issues specifically related to voice search optimization"
        ],
        "quick_wins": [
            "Easy fixes that can be implemented quickly"
        ],
        "detailed_analysis": {{
            "title_analysis": "Analysis of title tag",
            "content_analysis": "Analysis of content quality and structure",
            "schema_analysis": "Analysis of structured data implementation",
            "ai_readiness_analysis": "How well the site works with AI search"
        }},
        "estimated_monthly_traffic_loss": 1000-10000 (estimate based on issues severity),
        "industry": "detected industry (e.g., e-commerce, technology, healthcare, etc.)",
        "main_technical_issue": "primary issue category (e.g., page_speed, mobile_optimization, technical_seo, content_quality)",
        "top_competitors": ["competitor1.com", "competitor2.com"] (infer 2-3 based on industry),
        "visitor_value": 50 (estimated $ value per visitor based on industry)
    }}
    
    Focus on:
    1. AI search visibility (ChatGPT, Perplexity, Google AI Overviews)
    2. Voice search optimization
    3. Schema markup and structured data
    4. Content that answers questions naturally
    5. Technical SEO fundamentals
    6. Semantic content structure
    
    For estimated_monthly_traffic_loss:
    - Score 80-100: estimate 500-2000 lost visitors
    - Score 60-79: estimate 2000-5000 lost visitors  
    - Score 40-59: estimate 5000-10000 lost visitors
    - Score 0-39: estimate 10000+ lost visitors
    
    For industry detection, analyze the content and determine the primary business sector.
    
    For main_technical_issue, identify the most severe problem category affecting the site.
    """
    
    # Try OpenAI first
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert SEO auditor specializing in AI search optimization. Provide detailed, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        ai_analysis = json.loads(response.choices[0].message.content)
        return ai_analysis
        
    except Exception as openai_error:
        print(f"OpenAI failed: {openai_error}, trying OpenRouter...")
        
        # Fallback to OpenRouter
        try:
            return analyze_with_openrouter(prompt)
        except Exception as openrouter_error:
            print(f"OpenRouter also failed: {openrouter_error}")
            # Return fallback analysis if both AI services fail
            return generate_fallback_analysis(website_data)

def analyze_with_openrouter(prompt: str) -> Dict:
    """Use OpenRouter as fallback AI service"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4",  # Use same model through OpenRouter
        "messages": [
            {"role": "system", "content": "You are an expert SEO auditor specializing in AI search optimization. Provide detailed, actionable insights."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )
    
    response.raise_for_status()
    result = response.json()
    
    ai_analysis = json.loads(result['choices'][0]['message']['content'])
    return ai_analysis

def generate_fallback_analysis(website_data: Dict) -> Dict:
    """Generate basic analysis if both AI services fail"""
    issues = []
    recommendations = []
    score = 70  # Default score
    
    # Basic checks
    if not website_data.get('title'):
        issues.append("Missing title tag")
        recommendations.append("Add a unique, descriptive title tag to your homepage")
        score -= 10
    
    if not website_data.get('meta_description'):
        issues.append("Missing meta description")
        recommendations.append("Add compelling meta descriptions to all pages")
        score -= 10
    
    if not website_data.get('has_schema'):
        issues.append("No structured data found")
        recommendations.append("Implement schema markup for better AI understanding")
        score -= 15
    
    if website_data.get('images_without_alt', 0) > 0:
        issues.append(f"{website_data['images_without_alt']} images missing alt text")
        recommendations.append("Add descriptive alt text to all images")
        score -= 5
    
    if not website_data.get('ssl_certificate'):
        issues.append("No SSL certificate detected")
        recommendations.append("Install SSL certificate for secure browsing")
        score -= 10
    
    # Determine main technical issue based on what we found
    main_issue = "technical_seo"  # default
    if not website_data.get('has_schema'):
        main_issue = "schema_markup"
    elif not website_data.get('ssl_certificate'):
        main_issue = "security"
    
    # Estimate traffic loss based on score
    if score >= 80:
        traffic_loss = 1000
    elif score >= 60:
        traffic_loss = 3000
    elif score >= 40:
        traffic_loss = 7000
    else:
        traffic_loss = 12000
    
    return {
        "overall_score": max(0, score),
        "category_scores": {
            "technical_seo": max(0, score - 5),
            "content_quality": max(0, score),
            "ai_readiness": max(0, score - 20),
            "voice_search": max(0, score - 15),
            "schema_markup": 30 if website_data.get('has_schema') else 0
        },
        "critical_issues": issues[:5],  # Limit to 5
        "warnings": [],
        "recommendations": recommendations[:5],  # Limit to 5
        "ai_search_issues": ["Limited AI search visibility due to missing structured data"],
        "voice_search_issues": ["Content not optimized for conversational queries"],
        "quick_wins": ["Add missing alt text to images", "Implement basic schema markup"],
        "detailed_analysis": {
            "title_analysis": "Basic title analysis completed",
            "content_analysis": "Basic content analysis completed",
            "schema_analysis": "Schema markup analysis completed",
            "ai_readiness_analysis": "Basic AI readiness assessment completed"
        },
        # New fields for email
        "estimated_monthly_traffic_loss": traffic_loss,
        "industry": "general business",  # Default fallback
        "main_technical_issue": main_issue,
        "top_competitors": ["competitor1.com", "competitor2.com"],  # Generic fallback
        "visitor_value": 50  # Default $50 per visitor
    }