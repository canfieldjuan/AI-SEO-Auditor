# Save this as services/web_scraper_fix.py
# Then rename your current web_scraper.py to ai_service.py
# Then rename this file to web_scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Dict

def scrape_website(url: str) -> Dict:
    """Scrape website content and metadata"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        website_data = {
            'url': url,
            'title': soup.find('title').get_text() if soup.find('title') else '',
            'meta_description': '',
            'h1_tags': [h1.get_text().strip() for h1 in soup.find_all('h1')],
            'h2_tags': [h2.get_text().strip() for h2 in soup.find_all('h2')],
            'h3_tags': [h3.get_text().strip() for h3 in soup.find_all('h3')],
            'images': len(soup.find_all('img')),
            'images_without_alt': len([img for img in soup.find_all('img') if not img.get('alt')]),
            'internal_links': 0,
            'external_links': 0,
            'content_length': len(soup.get_text()),
            'has_schema': bool(soup.find('script', {'type': 'application/ld+json'})),
            'schema_types': [],
            'ssl_certificate': url.startswith('https://'),
            'content_text': soup.get_text()[:5000],
            'meta_keywords': '',
            'canonical_url': '',
            'open_graph': {},
            'twitter_cards': {},
            'structured_data': []
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            website_data['meta_description'] = meta_desc.get('content', '')
        
        # Count links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href.startswith('http') and url not in href:
                website_data['external_links'] += 1
            elif href.startswith('/') or url in href:
                website_data['internal_links'] += 1
        
        return website_data
        
    except Exception as e:
        return {'error': str(e)}