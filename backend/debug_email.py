#!/usr/bin/env python3
"""
Debug email validation issue
"""

from email_validator import validate_email, EmailNotValidError

def test_email_validation():
    test_emails = [
        "testuser@example.com",
        "user@gmail.com",
        "test@test.com",
        "invalid-email",
        "@example.com"
    ]
    
    for email in test_emails:
        try:
            result = validate_email(email)
            print(f"✅ {email} -> Valid: {result.email}")
        except EmailNotValidError as e:
            print(f"❌ {email} -> Invalid: {e}")
        except Exception as e:
            print(f"🔥 {email} -> Error: {e}")

if __name__ == "__main__":
    print("Testing email validation...")
    test_email_validation()