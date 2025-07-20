#!/usr/bin/env python3
"""
Quick test to verify hardcoded patterns are removed
"""

import os
from dotenv import load_dotenv
load_dotenv()

from utils.data_loader import DataLoader
from agents.analyst_agent.analyst import AnalystAgent

def quick_test():
    print("🔍 Quick Test: Verifying Hardcoded Patterns Removed...")
    
    loader = DataLoader()
    analyst = AnalystAgent(loader)
    
    # Test with bonus query that was showing hardcoded car responses
    query = "what to do i got 1 lakh bonus"
    result = analyst.analyze(query, "test_user")
    response = result.get('analysis', '')
    
    print(f"Query: {query}")
    print(f"Response: {response}")
    
    # Check for old hardcoded patterns
    old_patterns = [
        "Recommended Car Budget", 
        "Monthly EMI Capacity",
        "8.5-9.5% auto loan rates",
        "₹8-12 lakh car purchase"
    ]
    
    found_patterns = [pattern for pattern in old_patterns if pattern in response]
    
    print(f"\n🔍 Hardcoded car patterns found: {len(found_patterns)}")
    for pattern in found_patterns:
        print(f"  ❌ Found: {pattern}")
    
    # Check if response addresses the actual query
    bonus_relevant = any(word in response.lower() for word in ['bonus', '1 lakh', 'windfall', 'extra'])
    car_relevant = any(word in response.lower() for word in ['car', 'vehicle', 'auto', 'emi'])
    
    print(f"\n📝 Response Relevance:")
    print(f"  Addresses bonus question: {'✅' if bonus_relevant else '❌'}")
    print(f"  Mentions cars (should be no): {'❌' if car_relevant else '✅'}")
    
    if len(found_patterns) == 0 and bonus_relevant and not car_relevant:
        print(f"\n🎉 SUCCESS: Hardcoded patterns removed, response is relevant!")
    else:
        print(f"\n⚠️ STILL ISSUES: Some hardcoded patterns or irrelevant content detected")

if __name__ == "__main__":
    quick_test()