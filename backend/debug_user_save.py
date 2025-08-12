#!/usr/bin/env python3
"""
Debug script to test user profile saving
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_models import save_user_profile

def test_user_save():
    """Test the user profile saving function"""
    test_data = {
        "personalInfo": {
            "fullName": "Test User",
            "email": "test@example.com",
            "phoneNumber": "1234567890",
            "dateOfBirth": "1990-01-01",
            "occupation": "Developer"
        },
        "professionalInfo": {
            "occupation": "Developer",
            "annualIncome": "50-100L"
        },
        "investmentPreferences": {
            "riskTolerance": "moderate",
            "investmentGoals": ["wealth building"]
        }
    }
    
    try:
        print("Testing user profile saving...")
        user_id = save_user_profile(test_data)
        print(f"✅ Success! User ID: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_user_save()