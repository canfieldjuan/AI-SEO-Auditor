#!/usr/bin/env python
"""Test script to check all imports and dependencies"""

import sys

def test_import(module_name, item_name=None):
    """Test if a module can be imported"""
    try:
        if item_name:
            exec(f"from {module_name} import {item_name}")
            print(f"✓ {module_name}.{item_name}")
        else:
            exec(f"import {module_name}")
            print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ {module_name}: {type(e).__name__}: {e}")
        return False

print("Testing Python packages:")
print("-" * 40)
packages = [
    "flask",
    "flask_cors",
    "sqlite3",
    "json",
    "datetime",
    "os",
    "time",
    "threading",
]

for pkg in packages:
    test_import(pkg)

print("\nTesting project imports:")
print("-" * 40)
project_imports = [
    ("routes.api_routes", "api_bp"),
    ("models.database", "init_database"),
    ("models.database", "save_audit_data"),
    ("services.seo_auditor", "SEOAuditor"),
    ("services.web_scraper", "scrape_website"),
    ("services.ai_service", "analyze_with_ai"),
    ("services.report_generator", "generate_pdf_report"),
    ("services.email_service", "send_email_report"),
    ("services.cache_service", "cache"),
    ("utils.helpers", "clean_url"),
    ("utils.helpers", "is_valid_email"),
    ("utils.helpers", "is_valid_url"),
    ("utils.rate_limiter", "rate_limit"),
    ("utils.rate_limiter", "email_rate_limit"),
    ("utils.logging_config", "setup_logging"),
    ("utils.logging_config", "log_audit_request"),
    ("utils.logging_config", "log_audit_completion"),
    ("utils.logging_config", "log_error"),
    ("config.settings", "DATABASE_PATH"),
]

failed_imports = []
for module, item in project_imports:
    if not test_import(module, item):
        failed_imports.append((module, item))

if failed_imports:
    print(f"\n❌ {len(failed_imports)} imports failed")
    print("\nYou need to create these missing files/functions:")
    for module, item in failed_imports:
        print(f"  - {module}.py with {item}")
else:
    print("\n✅ All imports successful!")

print("\nChecking directories:")
print("-" * 40)
import os
dirs = ['static', 'routes', 'models', 'services', 'utils', 'config', 'reports', 'cache', 'logs']
for dir_name in dirs:
    if os.path.exists(dir_name):
        print(f"✓ {dir_name}/")
    else:
        print(f"✗ {dir_name}/ (missing)")

print("\nChecking key files:")
print("-" * 40)
files = [
    'static/index.html',
    'routes/__init__.py',
    'models/__init__.py',
    'services/__init__.py',
    'utils/__init__.py',
    'config/__init__.py',
]
for file_name in files:
    if os.path.exists(file_name):
        print(f"✓ {file_name}")
    else:
        print(f"✗ {file_name} (missing)")