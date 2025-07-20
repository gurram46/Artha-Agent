#!/usr/bin/env python3
"""
Test script to verify agents now provide natural, non-hardcoded responses
"""

import os
from dotenv import load_dotenv
load_dotenv()

from utils.data_loader import DataLoader
from agents.analyst_agent.analyst import AnalystAgent
from agents.research_agent.research import ResearchAgent  
from agents.risk_management_agent.risk_manager import RiskManagementAgent

def test_response_diversity():
    print("🔍 Testing Response Diversity and Natural Language...")
    
    # Initialize components
    loader = DataLoader()
    analyst = AnalystAgent(loader)
    research = ResearchAgent(loader)
    risk = RiskManagementAgent(loader)
    
    # Test different queries to ensure responses vary
    test_queries = [
        "what to do i got 1 lakh bonus",
        "should i buy a car worth 5 lakhs", 
        "how to invest 50000 rupees",
        "what is my portfolio performance",
        "can i afford a house"
    ]
    
    print("=" * 80)
    print("TESTING ANALYST AGENT RESPONSE VARIETY")
    print("=" * 80)
    
    analyst_responses = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = analyst.analyze(query, "test_user")
        response = result.get('analysis', '')
        analyst_responses.append(response)
        
        # Check for hardcoded patterns
        hardcoded_patterns = [
            "Your ₹285,255 in liquid assets",
            "provides a robust 3.8x coverage", 
            "₹75,000 outstanding debt",
            "bleeding ₹13,500 annually"
        ]
        
        pattern_count = sum(1 for pattern in hardcoded_patterns if pattern in response)
        print(f"   Hardcoded patterns found: {pattern_count}/4")
        print(f"   Opening: {response[:100]}...")
        
    # Check for response uniqueness
    unique_openings = set(resp[:50] for resp in analyst_responses)
    print(f"\n📊 Analyst Response Diversity: {len(unique_openings)}/{len(test_queries)} unique openings")
    
    print("\n" + "=" * 80)
    print("TESTING RESEARCH AGENT RESPONSE VARIETY") 
    print("=" * 80)
    
    research_responses = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = research.analyze(query, "test_user")
        response = result.get('analysis', '')
        research_responses.append(response)
        
        # Check for hardcoded patterns
        hardcoded_patterns = [
            "Given the current market dynamics",
            "8.5-9.5% auto loan rates",
            "leverage the highly favorable",
            "current market conditions"
        ]
        
        pattern_count = sum(1 for pattern in hardcoded_patterns if pattern in response)
        print(f"   Hardcoded patterns found: {pattern_count}/4") 
        print(f"   Opening: {response[:100]}...")
        
    unique_openings = set(resp[:50] for resp in research_responses)
    print(f"\n📊 Research Response Diversity: {len(unique_openings)}/{len(test_queries)} unique openings")
    
    print("\n" + "=" * 80)
    print("TESTING RISK AGENT RESPONSE VARIETY")
    print("=" * 80)
    
    risk_responses = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = risk.analyze(query, "test_user") 
        response = result.get('analysis', '')
        risk_responses.append(response)
        
        # Check for hardcoded patterns
        hardcoded_patterns = [
            "most critical financial move",
            "immediately eliminate the ₹75,000",
            "bleeding ₹13,500 annually",
            "dangerous financial leverage"
        ]
        
        pattern_count = sum(1 for pattern in hardcoded_patterns if pattern in response)
        print(f"   Hardcoded patterns found: {pattern_count}/4")
        print(f"   Opening: {response[:100]}...")
        
    unique_openings = set(resp[:50] for resp in risk_responses)
    print(f"\n📊 Risk Response Diversity: {len(unique_openings)}/{len(test_queries)} unique openings")
    
    # Overall assessment
    total_unique = len(set(resp[:50] for resp in analyst_responses + research_responses + risk_responses))
    total_responses = len(test_queries) * 3
    
    print(f"\n🏆 OVERALL ASSESSMENT:")
    print(f"Total unique response openings: {total_unique}/{total_responses}")
    print(f"Diversity score: {(total_unique/total_responses)*100:.1f}%")
    
    if total_unique > (total_responses * 0.8):
        print("✅ EXCELLENT: High response diversity - natural language achieved!")
    elif total_unique > (total_responses * 0.6):
        print("⚠️ GOOD: Some diversity but room for improvement")
    else:
        print("❌ POOR: Still showing hardcoded patterns")

if __name__ == "__main__":
    test_response_diversity()