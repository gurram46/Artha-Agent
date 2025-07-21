#!/usr/bin/env python3
"""
Test personalized analysis with actual MCP data
"""

import asyncio
import json
from agents.analyst_agent.analyst import AnalystAgent
from core.fi_mcp.client import FinancialData

async def test_personalized_analysis():
    """Test with actual MCP sample data for personalized car purchase advice"""
    print("🎯 Testing Personalized Financial Analysis...")
    
    # Load actual MCP sample data
    try:
        with open('../mcp-docs/sample_responses/fetch_net_worth.json', 'r') as f:
            sample_data = json.load(f)
        print("✅ Loaded actual MCP sample data")
        
        # Print the actual user's financial situation
        total_net_worth = sample_data['netWorthResponse']['totalNetWorthValue']['units']
        savings = next((asset['value']['units'] for asset in sample_data['netWorthResponse']['assetValues'] 
                       if 'SAVINGS' in asset['netWorthAttribute']), '0')
        total_loans = sum(int(liability['value']['units']) for liability in sample_data['netWorthResponse'].get('liabilityValues', []))
        
        print(f"\n📊 User's Actual Financial Profile:")
        print(f"- Net Worth: ₹{total_net_worth}")
        print(f"- Liquid Savings: ₹{savings}")
        print(f"- Total Existing Loans: ₹{total_loans}")
        
    except Exception as e:
        print(f"❌ Error loading MCP data: {e}")
        return False
    
    # Create FinancialData object with actual MCP data
    financial_data = FinancialData(
        net_worth=sample_data,
        mutual_funds=sample_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', []),
        bank_accounts={},
        equity_holdings=[],
        credit_report={},
        epf_details={},
        transactions=[]
    )
    
    # Create analyst
    analyst = AnalystAgent()
    
    # Realistic car purchase query
    user_query = "can i buy a car worth 8 lakhs"
    print(f"\n📝 Query: {user_query}")
    print("\n🔄 Processing for personalized analysis...\n")
    
    try:
        async for update in analyst.process_user_query(user_query, financial_data):
            if update['type'] == 'thinking':
                print(f"💭 {update['stage']}: {update['content']}")
            elif update['type'] == 'response':
                response_content = update['response']['content']
                
                print("\n✅ Personalized Analysis Complete!")
                
                # Check for personalization indicators
                personalized_checks = {
                    'Uses actual net worth (₹8,68,721)': '868721' in response_content or '8,68,721' in response_content,
                    'Uses actual savings (₹4,36,355)': '436355' in response_content or '4,36,355' in response_content,
                    'Mentions existing loans (₹64,000)': '64000' in response_content or '64,000' in response_content,
                    'Specific calculations shown': 'calculate' in response_content.lower() or 'available for purchase' in response_content.lower(),
                    'Uses ₹ symbol': '₹' in response_content,
                    'Mentions user-specific amounts': any(amount in response_content for amount in ['84613', '211111', '200642'])
                }
                
                print(f"\n🎯 Personalization Check:")
                for check, passed in personalized_checks.items():
                    status = "✅" if passed else "❌"
                    print(f"{status} {check}")
                
                personalized_score = sum(personalized_checks.values())
                print(f"\n📈 Personalization Score: {personalized_score}/6")
                
                # Show first part of response
                print(f"\n📊 Response Preview:")
                print(f"{response_content[:1200]}...")
                
                if personalized_score >= 4:
                    print(f"\n🎉 SUCCESS: Analysis is personalized!")
                    return True
                else:
                    print(f"\n⚠️  NEEDS IMPROVEMENT: Analysis is still too generic")
                    return False
                
            elif update['type'] == 'error':
                print(f"❌ Error: {update['error']}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_personalized_analysis())
    if result:
        print("\n🏆 Personalized analysis working perfectly!")
    else:
        print("\n💡 Further improvements needed")