# File: tests/test_api.py

import unittest
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.email_service import get_score_segment, personalize_subject_line, personalize_email_body, generate_testimonial_html
from services.report_generator import get_issue_explanation, get_recommendation_steps

class TestEmailService(unittest.TestCase):
    def test_get_score_segment(self):
        self.assertEqual(get_score_segment(95), 'high')
        self.assertEqual(get_score_segment(70), 'medium')
        self.assertEqual(get_score_segment(45), 'low')

    def test_personalize_subject_line(self):
        subject_template = "Your SEO Audit Report for {{websiteUrl}} - Score: 85"
        website_url = "https://www.example.com"
        personalized_subject = personalize_subject_line(subject_template, {'websiteUrl': website_url})
        self.assertEqual(personalized_subject, "Your SEO Audit Report for https://www.example.com - Score: 85")

    def test_personalize_email_body(self):
        body_template = "Hi {{userName}}, here is your SEO audit report."
        user_name = "John Smith"
        personalized_body = personalize_email_body(body_template, {'userName': user_name})
        self.assertEqual(personalized_body, "Hi John Smith, here is your SEO audit report.")

    def test_generate_testimonial_html(self):
        testimonial_html = generate_testimonial_html()
        self.assertIn('<div class="testimonial">', testimonial_html)
        self.assertIn('<p class="testimonial-text">', testimonial_html)
        self.assertIn('<p class="testimonial-author">', testimonial_html)

class TestReportGenerator(unittest.TestCase):
    def test_get_issue_explanation(self):
        issue = "Missing meta description"
        explanation = get_issue_explanation(issue)
        self.assertIn("meta description", explanation)
        self.assertIn("search engines", explanation)

    def test_get_recommendation_steps(self):
        recommendation = "Implement schema markup for better AI understanding"
        steps = get_recommendation_steps(recommendation)
        self.assertIn("Identify the main entities", steps)
        self.assertIn("Map them to appropriate Schema.org types", steps)
        self.assertIn("Add JSON-LD structured data", steps)

class TestSEOAuditorAPI(unittest.TestCase):
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    # ... existing API tests ...

if __name__ == '__main__':
    unittest.main()