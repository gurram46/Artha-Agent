#!/usr/bin/env python3
"""
Simple test for AI agents without interactive input
"""

import asyncio
import json
import os
import sys
from agents.analyst_agent.analyst import AnalystAgent
from core.fi_mcp.client import FinancialData

async def run_simple_test():
    """Test single query without interactive input"""
    print("🧪 Testing AI Agent with Gemini 2.5 Flash...")
    
    # Load sample data
    try:
        with open('../mcp-docs/sample_responses/fetch_net_worth.json', 'r') as f:
            sample_net_worth = json.load(f)
        
        financial_data = FinancialData(
            net_worth=sample_net_worth,
            mutual_funds=sample_net_worth.get('mfSchemeAnalytics', {}).get('schemeAnalytics', []),
            bank_accounts=sample_net_worth.get('accountDetailsBulkResponse', {}).get('accountDetailsMap', {}),
            equity_holdings=[],
            credit_report={},
            epf_details={},
            transactions=[]
        )
        
        print("✅ Sample data loaded")
        
    except Exception as e:
        print(f"⚠️ Using fallback data: {e}")
        financial_data = FinancialData(
            net_worth={
                'netWorthResponse': {
                    'totalNetWorthValue': {'currencyCode': 'INR', 'units': '500000'},
                    'assetValues': [
                        {'netWorthAttribute': 'ASSET_TYPE_SAVINGS_ACCOUNTS', 'value': {'units': '200000', 'currencyCode': 'INR'}},
                        {'netWorthAttribute': 'ASSET_TYPE_MUTUAL_FUND', 'value': {'units': '300000', 'currencyCode': 'INR'}}
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
    
    # Test single agent
    print("\n🤖 Creating Analyst Agent...")
    analyst = AnalystAgent()
    
    user_query = "can i buy a car now"
    print(f"📝 Query: {user_query}")
    print("\n🔄 Processing...\n")
    
    # Process query
    try:
        async for update in analyst.process_user_query(user_query, financial_data):
            if update['type'] == 'thinking':
                print(f"💭 {update['stage']}: {update['content']}")
            elif update['type'] == 'response':
                print("\n✅ SUCCESS!")
                print(f"📊 Response: {update['response']['content'][:500]}...")
                print(f"🔍 Sources: {update['response'].get('grounded_sources', 0)}")
                return True
            elif update['type'] == 'error':
                print(f"❌ Error: {update['error']}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return False

if __name__ == "__main__":
    result = asyncio.run(run_simple_test())
    if result:
        print("\n🎉 Test PASSED - AI agents are working!")
    else:
        print("\n💥 Test FAILED - Need more fixes")
    sys.exit(0 if result else 1)