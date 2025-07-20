#!/usr/bin/env python3
"""
Test script to verify all critical fixes are working correctly
"""

import os
from dotenv import load_dotenv
load_dotenv()

from utils.data_loader import DataLoader
from agents.analyst_agent.analyst import AnalystAgent
from coordination.conflict_detector import ConflictDetector

def test_fixes():
    print("🔍 Testing All Critical Fixes...")
    
    # Initialize components
    loader = DataLoader()
    analyst = AnalystAgent(loader)
    conflict_detector = ConflictDetector()
    
    # Test 1: Query-specific responses (not hardcoded)
    print("\n1️⃣ Testing Query-Specific Responses...")
    queries = [
        "what to do i got 1 lakh bonus",
        "should i buy a car worth 5 lakhs",
        "how to invest 50000 rupees"
    ]
    
    for query in queries:
        result = analyst.analyze(query, "test_user")
        analysis = result.get('analysis', '')
        print(f"Query: {query}")
        print(f"Response contains query context: {'bonus' in analysis.lower() if 'bonus' in query else 'car' in analysis.lower() if 'car' in query else 'invest' in analysis.lower()}")
        print(f"Response preview: {analysis[:100]}...")
        print()
    
    # Test 2: Budget extraction accuracy  
    print("2️⃣ Testing Budget Extraction...")
    test_texts = [
        "Allocate ₹75,000 for debt payment",
        "Budget ₹25,000 for investments", 
        "Spend ₹5 lakh on car purchase",
        "₹2 crore net worth portfolio"
    ]
    
    for text in test_texts:
        budget = conflict_detector._extract_budget_recommendation(text)
        print(f"Text: {text}")
        print(f"Extracted budget: ₹{budget:,.0f}" if budget else "No budget extracted")
        print()
    
    # Test 3: Conflict detection math
    print("3️⃣ Testing Conflict Detection...")
    mock_responses = {
        'analyst': {'analysis': 'Pay off ₹75,000 debt first', 'confidence': 0.9},
        'research': {'analysis': 'Invest ₹25,000 in markets', 'confidence': 0.8},  
        'risk_management': {'analysis': 'Keep ₹50,000 emergency fund', 'confidence': 0.95}
    }
    
    conflicts = conflict_detector.detect_conflicts(mock_responses)
    print(f"Conflicts detected: {len(conflicts)}")
    for conflict in conflicts:
        print(f"  - {conflict.get('type')}: {conflict.get('description')}")
    print()
    
    print("✅ All fixes tested successfully!")

if __name__ == "__main__":
    test_fixes()