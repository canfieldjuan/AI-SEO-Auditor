# File: services/web_scraper.py
# Web scraping service for extracting website data and metadata

import requests
from bs4 import BeautifulSoup
import json
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
        
        # Extract comprehensive website data
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
            'page_speed': None,  # Would need PageSpeed API
            'mobile_friendly': None,  # Would need Mobile-Friendly Test API
            'ssl_certificate': url.startswith('https://'),
            'content_text': soup.get_text()[:5000],  # First 5000 chars for AI analysis
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
        
        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            website_data['meta_keywords'] = meta_keywords.get('content', '')
        
        # Extract canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            website_data['canonical_url'] = canonical.get('href', '')
        
        # Extract Open Graph data
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            website_data['open_graph'][tag.get('property')] = tag.get('content')
        
        # Extract Twitter Card data
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            website_data['twitter_cards'][tag.get('name')] = tag.get('content')
        
        # Count links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href.startswith('http') and url not in href:
                website_data['external_links'] += 1
            elif href.startswith('/') or url in href:
                website_data['internal_links'] += 1
        
        # Extract structured data
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                data = json.loads(script.string)
                website_data['structured_data'].append(data)
                if isinstance(data, dict) and '@type' in data:
                    website_data['schema_types'].append(data['@type'])
            except:
                pass
        
        return website_data
        
    except Exception as e:
        return {'error': str(e)}