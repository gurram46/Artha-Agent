#!/usr/bin/env python3
"""
Test script for AI-powered financial agents with Gemini 2.5 Flash
"""

import asyncio
import json
import sys
import os
from agents.analyst_agent.analyst import AnalystAgent
from core.fi_mcp.client import FinancialData

async def test_analyst_with_sample_data():
    """Test the analyst agent with sample MCP data"""
    print("🧪 Testing Analyst Agent with Gemini 2.5 Flash...")
    
    # Load complete sample data
    try:
        # Load all sample data files
        with open('../mcp-docs/sample_responses/fetch_net_worth.json', 'r') as f:
            sample_net_worth = json.load(f)
        
        with open('../mcp-docs/sample_responses/fetch_mf_transactions.json', 'r') as f:
            sample_transactions = json.load(f)
        
        with open('../mcp-docs/sample_responses/fetch_credit_report.json', 'r') as f:
            sample_credit = json.load(f)
        
        with open('../mcp-docs/sample_responses/fetch_epf_details.json', 'r') as f:
            sample_epf = json.load(f)
        
        print("✅ Sample data loaded successfully")
        
        # Create FinancialData object
        financial_data = FinancialData(
            net_worth=sample_net_worth,
            mutual_funds=sample_net_worth.get('mfSchemeAnalytics', {}).get('schemeAnalytics', []),
            bank_accounts=sample_net_worth.get('accountDetailsBulkResponse', {}).get('accountDetailsMap', {}),
            equity_holdings=[],
            credit_report=sample_credit,
            epf_details=sample_epf,
            transactions=sample_transactions.get('transactions', [])
        )
        
        print("\n📊 Financial Data Summary:")
        print(f"- Net Worth: ₹{sample_net_worth.get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', 'N/A')}")
        print(f"- Credit Score: {sample_credit.get('creditReports', [{}])[0].get('creditReportData', {}).get('score', {}).get('bureauScore', 'N/A')}")
        print(f"- EPF Balance: ₹{sample_epf.get('uanAccounts', [{}])[0].get('rawDetails', {}).get('overall_pf_balance', {}).get('current_pf_balance', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        print("Using minimal fallback data...")
        
        # Minimal fallback data
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
    
    # Create analyst agent
    print("\n🤖 Initializing Analyst Agent...")
    analyst = AnalystAgent()
    
    # Test query
    user_query = "what is my budget if i want to buy a car worth 20 lakhs"
    
    print(f"\n📝 User Query: {user_query}")
    print("\n🔄 Processing with Gemini 2.5 Flash + Google Search...\n")
    
    try:
        # Process the query
        async for update in analyst.process_user_query(user_query, financial_data):
            if update['type'] == 'thinking':
                print(f"💭 {update['stage']}: {update['content']}")
            elif update['type'] == 'response':
                print("\n✅ Analysis Complete!")
                print(f"\n📊 Response:\n{update['response']['content'][:1000]}...")
                print(f"\n🔍 Sources: {update['response'].get('grounded_sources', 0)} Google searches performed")
                print(f"⚡ Processing time: {update['response'].get('processing_time', 0):.1f}s")
                print(f"📈 Confidence: {update['response'].get('confidence_level', 0)*100:.0f}%")
                
                if update['response'].get('recommendations'):
                    print("\n💡 Key Recommendations:")
                    for rec in update['response']['recommendations'][:3]:
                        print(f"  • {rec}")
                        
            elif update['type'] == 'error':
                print(f"\n❌ Error: {update['error']}")
                print("\n🔍 Error Details:")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run comprehensive tests"""
    print("🚀 Artha AI Agent Test Suite - Gemini 2.5 Flash")
    print("=" * 50)
    
    await test_analyst_with_sample_data()
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted")
        sys.exit(0)