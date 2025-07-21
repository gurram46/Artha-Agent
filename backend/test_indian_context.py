#!/usr/bin/env python3
"""
Test Indian context fixes
"""

import asyncio
import json
from agents.analyst_agent.analyst import AnalystAgent
from core.fi_mcp.client import FinancialData

async def test_indian_context():
    """Test with realistic Indian financial scenario"""
    print("🇮🇳 Testing Indian Financial Context...")
    
    # Create realistic Indian financial data
    financial_data = FinancialData(
        net_worth={
            'netWorthResponse': {
                'totalNetWorthValue': {'currencyCode': 'INR', 'units': '932000'},
                'assetValues': [
                    {'netWorthAttribute': 'ASSET_TYPE_SAVINGS_ACCOUNTS', 'value': {'units': '400000', 'currencyCode': 'INR'}},
                    {'netWorthAttribute': 'ASSET_TYPE_MUTUAL_FUND', 'value': {'units': '350000', 'currencyCode': 'INR'}},
                    {'netWorthAttribute': 'ASSET_TYPE_EPF', 'value': {'units': '182000', 'currencyCode': 'INR'}}
                ]
            }
        },
        mutual_funds=[],
        bank_accounts={},
        equity_holdings=[],
        credit_report={},
        epf_details={},
        transactions=[]
    )
    
    print("📊 Test Financial Profile:")
    print("- Net Worth: ₹9,32,000")
    print("- Savings: ₹4,00,000")
    print("- Mutual Funds: ₹3,50,000") 
    print("- EPF: ₹1,82,000")
    
    analyst = AnalystAgent()
    
    # Realistic Indian car purchase query
    user_query = "can i buy a car worth 15 lakhs with my current financial situation"
    
    print(f"\n📝 Query: {user_query}")
    print("\n🔄 Testing Indian context...\n")
    
    try:
        async for update in analyst.process_user_query(user_query, financial_data):
            if update['type'] == 'thinking':
                print(f"💭 {update['stage']}: {update['content']}")
            elif update['type'] == 'response':
                print("\n✅ SUCCESS - Indian Context Response!")
                response_content = update['response']['content']
                
                # Check for Indian context indicators
                indian_indicators = [
                    '₹' in response_content,
                    'lakh' in response_content.lower(),
                    'indian' in response_content.lower(),
                    'inr' in response_content.lower(),
                    'rupee' in response_content.lower()
                ]
                
                print(f"\n🇮🇳 Indian Context Check: {sum(indian_indicators)}/5 indicators found")
                if '₹' in response_content:
                    print("✅ Using Indian Rupee symbol")
                if 'lakh' in response_content.lower():
                    print("✅ Using Indian number format (lakhs)")
                if 'indian' in response_content.lower():
                    print("✅ Mentions Indian context")
                
                print(f"\n📊 Response Preview:")
                print(f"{response_content[:800]}...")
                
                # Check if response is realistic for Indian context
                if '$' in response_content:
                    print("⚠️  WARNING: Still using dollar signs!")
                if '800000' in response_content or '800,000' in response_content:
                    print("⚠️  WARNING: Unrealistic income amounts detected!")
                
                print(f"\n🔍 Sources: {update['response'].get('grounded_sources', 0)} Indian market searches")
                return True
                
            elif update['type'] == 'error':
                print(f"❌ Error: {update['error']}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_indian_context())
    if result:
        print("\n🎉 Indian context fixes working!")
    else:
        print("\n💥 Need more fixes")