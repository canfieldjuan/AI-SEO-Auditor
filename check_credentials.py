#!/usr/bin/env python
"""
Validate Gmail app password format and test authentication
"""

import os
import re
from dotenv import load_dotenv

# Force reload
load_dotenv(override=True)

print("🔍 Gmail App Password Validator\n")

# Read from .env
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASS = os.getenv('EMAIL_PASS', '')

print(f"Current EMAIL_USER: {EMAIL_USER}")
print(f"Current EMAIL_PASS: {EMAIL_PASS}")
print(f"Password length: {len(EMAIL_PASS)} characters")

# Validate email
email_issues = []
if 'your-' in EMAIL_USER:
    email_issues.append("Remove 'your-' prefix from email")
if '@' not in EMAIL_USER:
    email_issues.append("Invalid email format")
if EMAIL_USER != EMAIL_USER.strip():
    email_issues.append("Email has extra spaces")

# Validate password
pass_issues = []
if len(EMAIL_PASS) == 0:
    pass_issues.append("Password is empty")
elif len(EMAIL_PASS) < 16:
    pass_issues.append(f"Password too short ({len(EMAIL_PASS)} chars, should be 16)")
elif len(EMAIL_PASS) > 19:  # 16 chars + 3 spaces
    pass_issues.append(f"Password too long ({len(EMAIL_PASS)} chars)")

# Check for common issues
if EMAIL_PASS.startswith('"') or EMAIL_PASS.endswith('"'):
    pass_issues.append("Remove quotes from password")
if EMAIL_PASS.startswith("'") or EMAIL_PASS.endswith("'"):
    pass_issues.append("Remove quotes from password")

print("\n📋 Validation Results:")
if email_issues:
    print("❌ Email issues:")
    for issue in email_issues:
        print(f"   - {issue}")
else:
    print("✅ Email format is correct")

if pass_issues:
    print("❌ Password issues:")
    for issue in pass_issues:
        print(f"   - {issue}")
else:
    print("✅ Password format looks correct")

if not email_issues and not pass_issues:
    print("\n🔐 Testing authentication with Gmail...")
    import smtplib
    
    # Try both with and without spaces
    passwords_to_try = [
        EMAIL_PASS,  # As is
        EMAIL_PASS.replace(' ', ''),  # Without spaces
        ' '.join([EMAIL_PASS[i:i+4] for i in range(0, 16, 4)])  # With spaces
    ]
    
    for i, pwd in enumerate(passwords_to_try):
        if i == 0:
            print(f"\nTrying password as-is...")
        elif i == 1:
            print(f"Trying without spaces...")
        else:
            print(f"Trying with standard spacing...")
            
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_USER, pwd)
            server.quit()
            print(f"✅ SUCCESS! Authentication worked!")
            
            if i == 1:
                print(f"\n📝 Update your .env file:")
                print(f"EMAIL_PASS={pwd}")
            elif i == 2:
                print(f"\n📝 Update your .env file:")
                print(f"EMAIL_PASS={pwd}")
                
            break
            
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Failed")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("\n⚠️  All authentication attempts failed!")
        print("\nYou need a NEW app password:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Delete old 'SEO Auditor' entries")
        print("3. Generate a fresh app password")
        print("4. Update .env with the new password")

print("\n📌 Correct .env format:")
print("EMAIL_USER=canfieldjuan24@gmail.com")
print("EMAIL_PASS=abcd efgh ijkl mnop  (your actual 16-char password)")