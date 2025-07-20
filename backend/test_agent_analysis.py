#!/usr/bin/env python3
"""
Test script to verify agent analysis with real MCP data
"""

import os
from dotenv import load_dotenv
load_dotenv()

from utils.data_loader import DataLoader
from agents.analyst_agent.analyst import AnalystAgent

def test_agent_analysis():
    print("🔍 Testing Agent Analysis with Real MCP Data...")
    
    # Initialize data loader and agent
    loader = DataLoader()
    analyst = AnalystAgent(loader)
    
    # Test query
    query = "How is my portfolio performing?"
    user_id = "test_user"
    
    print(f"Query: {query}")
    print(f"User ID: {user_id}")
    
    # Perform analysis
    result = analyst.analyze(query, user_id)
    
    print("\n📊 Analysis Result:")
    print(f"Agent: {result.get('agent_name', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Data Quality: {result.get('data_quality', 'N/A')}")
    
    # Check if real data was used
    analysis = result.get('analysis', '')
    print(f"\n🔍 Analysis Preview: {analysis[:200]}...")
    
    # Check for specific data points that indicate real data usage
    real_data_indicators = [
        '₹84613',   # Mutual fund value from data
        '₹211111',  # EPF value from data  
        '₹200642',  # Securities value from data
        '₹436355',  # Savings value from data
    ]
    
    found_indicators = [indicator for indicator in real_data_indicators if indicator in analysis]
    
    print(f"\n✅ Real Data Indicators Found: {len(found_indicators)}/4")
    for indicator in found_indicators:
        print(f"  - {indicator}")
    
    if len(found_indicators) > 0:
        print("🎉 SUCCESS: Agent is using real MCP financial data!")
    else:
        print("⚠️ WARNING: Agent may not be using real MCP data")
    
    # Check portfolio analysis
    portfolio_analysis = result.get('portfolio_analysis', {})
    if portfolio_analysis:
        print(f"\n📈 Portfolio Analysis: {portfolio_analysis}")

if __name__ == "__main__":
    test_agent_analysis()