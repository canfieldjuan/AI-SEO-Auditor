#!/usr/bin/env python
"""Test the audit functionality directly"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_URL = "https://example.com"
TEST_EMAIL = "test@example.com"

print("Testing SEO Auditor API")
print("=" * 50)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: API test endpoint
print("\n2. Testing API test endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/test")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Audit endpoint
print("\n3. Testing audit endpoint...")
print(f"   URL: {TEST_URL}")
print(f"   Email: {TEST_EMAIL}")

try:
    response = requests.post(
        f"{BASE_URL}/api/audit",
        json={
            "url": TEST_URL,
            "email": TEST_EMAIL
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Score: {data.get('score')}")
        print(f"   Email sent: {data.get('email_sent')}")
        print(f"   Issues found: {len(data.get('issues', []))}")
        print(f"   Recommendations: {len(data.get('recommendations', []))}")
    else:
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("Testing complete!")