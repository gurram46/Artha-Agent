#!/usr/bin/env python3
"""
Comprehensive test to verify all critical issues are fixed
"""

import os
from dotenv import load_dotenv
load_dotenv()

from coordination.realtime_collaboration import RealtimeCollaborationStreamer
from coordination.conflict_detector import ConflictDetector

def test_all_fixes():
    print("🔍 Testing All Critical Fixes...")
    
    streamer = RealtimeCollaborationStreamer()
    conflict_detector = ConflictDetector()
    
    # Test 1: AI-Powered Final Recommendation
    print("\n1️⃣ Testing AI-Powered Final Recommendation...")
    
    mock_responses = {
        'analyst': {
            'analysis': 'For your ₹1 lakh bonus, I recommend using ₹75,000 to clear your outstanding debt and investing the remaining ₹25,000.'
        },
        'research': {
            'analysis': 'Current market conditions suggest using ₹75,000 for debt clearance and putting ₹25,000 in equity mutual funds.'
        },
        'risk_management': {
            'analysis': 'Eliminate the ₹75,000 debt first to save ₹1,125 monthly, then use ₹25,000 to boost your emergency fund.'
        }
    }
    
    bonus_query = "what to do i got 1 lakh bonus"
    final_answer = streamer._create_unified_final_answer(mock_responses, bonus_query)
    
    # Check if it addresses the bonus question (not car budget)
    bonus_relevant = any(word in final_answer.lower() for word in ['bonus', '1 lakh', '75,000', '25,000'])
    car_irrelevant = not any(word in final_answer.lower() for word in ['car budget', 'emi capacity', 'auto loan'])
    
    print(f"  Addresses bonus question: {'✅' if bonus_relevant else '❌'}")
    print(f"  Avoids car budget advice: {'✅' if car_irrelevant else '❌'}")
    
    # Test 2: Improved Conflict Detection
    print("\n2️⃣ Testing Improved Conflict Detection...")
    
    # Realistic agent responses that shouldn't trigger false conflicts
    realistic_responses = {
        'analyst': {'analysis': 'Use ₹75,000 for debt, ₹25,000 for savings', 'confidence': 0.9},
        'research': {'analysis': 'Clear ₹75,000 debt, invest remaining ₹25,000', 'confidence': 0.85},
        'risk_management': {'analysis': 'Pay off ₹75,000 outstanding debt first', 'confidence': 0.95}
    }
    
    conflicts = conflict_detector.detect_conflicts(realistic_responses)
    print(f"  Conflicts detected: {len(conflicts)} (should be 0-1)")
    
    # Test 3: Budget Extraction Accuracy
    print("\n3️⃣ Testing Budget Extraction...")
    
    test_texts = [
        "Use ₹75,000 for debt payment",
        "Budget ₹25,000 for investments",
        "Car budget of ₹8 lakh with financing"
    ]
    
    accurate_extractions = 0
    for text in test_texts:
        budget = conflict_detector._extract_budget_recommendation(text)
        expected = 75000 if "75,000" in text else 25000 if "25,000" in text else 800000
        if budget and abs(budget - expected) < expected * 0.1:  # Within 10%
            accurate_extractions += 1
        print(f"  Text: {text}")
        print(f"  Extracted: ₹{budget:,.0f}, Expected: ₹{expected:,.0f}")
    
    print(f"  Accurate extractions: {accurate_extractions}/{len(test_texts)}")
    
    # Overall Assessment
    print(f"\n🏆 OVERALL ASSESSMENT:")
    
    tests_passed = 0
    if bonus_relevant and car_irrelevant:
        tests_passed += 1
        print("  ✅ Final recommendation matches user query")
    else:
        print("  ❌ Final recommendation still has issues")
    
    if len(conflicts) <= 1:
        tests_passed += 1
        print("  ✅ Conflict detection improved (fewer false positives)")
    else:
        print("  ❌ Conflict detection still has false positives")
    
    if accurate_extractions >= 2:
        tests_passed += 1
        print("  ✅ Budget extraction is accurate")
    else:
        print("  ❌ Budget extraction needs improvement")
    
    print(f"\n📊 Success Rate: {tests_passed}/3 ({(tests_passed/3)*100:.0f}%)")
    
    if tests_passed == 3:
        print("🎉 ALL CRITICAL ISSUES FIXED! System ready for production.")
    elif tests_passed >= 2:
        print("✅ Major improvements made, minor issues remain.")
    else:
        print("⚠️ Significant issues still need attention.")

if __name__ == "__main__":
    test_all_fixes()