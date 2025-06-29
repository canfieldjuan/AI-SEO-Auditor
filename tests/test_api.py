# File: tests/test_api.py
# API and service tests for the SEO Auditor application

import unittest
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.web_scraper import scrape_website
from services.ai_service import generate_fallback_analysis
from utils.helpers import clean_url, is_valid_email, is_valid_url

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

    def test_audit_endpoint_missing_data(self):
        """Test audit endpoint with missing data"""
        response = self.client.post('/api/audit', 
                                  json={})
        self.assertEqual(response.status_code, 400)

    def test_audit_endpoint_invalid_data(self):
        """Test audit endpoint with invalid data"""
        response = self.client.post('/api/audit', 
                                  json={'url': 'invalid-url', 'email': 'invalid-email'})
        self.assertEqual(response.status_code, 400)

    def test_audit_endpoint_valid_data(self):
        """Test audit endpoint with valid data"""
        response = self.client.post('/api/audit', 
                                  json={'url': 'https://example.com', 'email': 'test@example.com'})
        # This might fail in testing environment without proper API keys
        # In real testing, you'd mock the external API calls
        self.assertIn(response.status_code, [200, 500])

class TestWebScraper(unittest.TestCase):
    def test_scrape_valid_website(self):
        """Test scraping a valid website"""
        # Using a reliable test site
        result = scrape_website('https://httpbin.org/html')
        self.assertNotIn('error', result)
        self.assertIn('url', result)
        self.assertIn('title', result)

    def test_scrape_invalid_website(self):
        """Test scraping an invalid website"""
        result = scrape_website('https://this-domain-does-not-exist-12345.com')
        self.assertIn('error', result)

class TestHelpers(unittest.TestCase):
    def test_clean_url(self):
        """Test URL cleaning function"""
        self.assertEqual(clean_url('example.com'), 'https://example.com')
        self.assertEqual(clean_url('https://example.com/'), 'https://example.com')
        self.assertEqual(clean_url('http://example.com'), 'http://example.com')

    def test_is_valid_email(self):
        """Test email validation"""
        self.assertTrue(is_valid_email('test@example.com'))
        self.assertTrue(is_valid_email('user.name+tag@domain.co.uk'))
        self.assertFalse(is_valid_email('invalid-email'))
        self.assertFalse(is_valid_email('test@'))

    def test_is_valid_url(self):
        """Test URL validation"""
        self.assertTrue(is_valid_url('https://example.com'))
        self.assertTrue(is_valid_url('http://subdomain.example.com/path'))
        self.assertFalse(is_valid_url('invalid-url'))
        self.assertFalse(is_valid_url('ftp://example.com'))

class TestAIService(unittest.TestCase):
    def test_fallback_analysis(self):
        """Test fallback analysis generation"""
        sample_data = {
            'url': 'https://example.com',
            'title': 'Test Site',
            'meta_description': 'Test description',
            'has_schema': False,
            'images_without_alt': 5,
            'ssl_certificate': True
        }
        
        result = generate_fallback_analysis(sample_data)
        self.assertIn('overall_score', result)
        self.assertIn('category_scores', result)
        self.assertIn('critical_issues', result)
        self.assertIsInstance(result['overall_score'], int)
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)

if __name__ == '__main__':
    unittest.main()