#!/usr/bin/env python3
"""
Test AI-powered final recommendation generation
"""

import os
from dotenv import load_dotenv
load_dotenv()

from coordination.realtime_collaboration import RealtimeCollaborationStreamer

def test_ai_final_answer():
    print("🔍 Testing AI-Powered Final Recommendation...")
    
    streamer = RealtimeCollaborationStreamer()
    
    # Mock agent responses for car budget question
    mock_responses = {
        'analyst': {
            'analysis': 'Based on your financial data, you could comfortably budget for a car in the ₹6-9 lakh range with financing, or ₹2.5-4 lakh if paying cash. Your liquid assets of ₹285,255 provide excellent down payment flexibility.'
        },
        'research': {
            'analysis': 'Current auto loan rates of 8.5-9.5% make financing attractive. I recommend a ₹7-8 lakh car with strategic financing to preserve your equity investments.'
        },
        'risk_management': {
            'analysis': 'Focus on total cost of ownership. Work backward from a comfortable monthly EMI. Protect your emergency fund and consider 20-40% down payment for lower EMIs.'
        }
    }
    
    user_query = "what is my budget if i want to buy a car"
    
    # Test the AI-powered final answer
    final_answer = streamer._create_unified_final_answer(mock_responses, user_query)
    
    print(f"User Query: {user_query}")
    print(f"\nAI-Generated Final Answer:")
    print("=" * 80)
    print(final_answer)
    print("=" * 80)
    
    # Check if the answer addresses the car budget question
    car_relevant = any(word in final_answer.lower() for word in ['car', 'budget', 'lakh', 'vehicle'])
    debt_irrelevant = 'clear ₹75,000 debt' not in final_answer
    specific_amounts = any(amount in final_answer for amount in ['₹6', '₹7', '₹8', '₹9'])
    
    print(f"\n📊 Quality Assessment:")
    print(f"  Addresses car budget: {'✅' if car_relevant else '❌'}")
    print(f"  Avoids irrelevant debt advice: {'✅' if debt_irrelevant else '❌'}")  
    print(f"  Includes specific amounts: {'✅' if specific_amounts else '❌'}")
    
    if car_relevant and debt_irrelevant and specific_amounts:
        print(f"\n🎉 SUCCESS: AI correctly synthesized car budget recommendations!")
    else:
        print(f"\n⚠️ NEEDS IMPROVEMENT: Final answer not fully matching query")

if __name__ == "__main__":
    test_ai_final_answer()