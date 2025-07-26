#!/usr/bin/env python3
"""
Investment Agent CLI - Working Version
Based exactly on run_interactive.py but modified for CLI input
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    from investment_agent.agent import root_agent
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Part, UserContent
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed the required dependencies:")
    print("pip install google-adk google-genai python-dotenv")
    sys.exit(1)

def load_user_data(phone_number):
    """Load user data from test_data_dir."""
    user_data = {}
    test_data_dir = "fi-mcp-dev/test_data_dir"
    user_dir = os.path.join(test_data_dir, phone_number)
    
    if not os.path.exists(user_dir):
        print(f"❌ User directory not found: {user_dir}")
        return None
    
    # Load all JSON files in the user directory
    for filename in os.listdir(user_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(user_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    user_data[filename.replace('.json', '')] = data
                    print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    return user_data

def create_investment_query(user_data, phone_number, investment_amount):
    """Create a comprehensive investment query based on user data."""
    
    # Extract key financial information
    net_worth_data = user_data.get('fetch_net_worth', {})
    credit_data = user_data.get('fetch_credit_report', {})
    epf_data = user_data.get('fetch_epf_details', {})
    bank_data = user_data.get('fetch_bank_transactions', {})
    mf_data = user_data.get('fetch_mf_transactions', {})
    stock_data = user_data.get('fetch_stock_transactions', {})
    
    # Calculate totals
    total_assets = net_worth_data.get('totalAssets', 0)
    credit_score = credit_data.get('creditScore', 'N/A')
    epf_balance = epf_data.get('epfBalance', 0)
    
    # Asset breakdown
    asset_breakdown = []
    if net_worth_data.get('assetBreakdown'):
        for asset in net_worth_data['assetBreakdown']:
            asset_breakdown.append(f"  - {asset.get('type', 'Unknown')}: ₹{asset.get('value', 0):,.0f}")
    
    # Bank transaction analysis
    bank_summary = ""
    if bank_data.get('bankTransactions'):
        transactions = bank_data['bankTransactions']
        total_income = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'credit')
        total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'debit')
        bank_summary = f"""
**Banking Analysis:**
- Total Income (last period): ₹{total_income:,.0f}
- Total Expenses (last period): ₹{total_expenses:,.0f}
- Net Savings: ₹{total_income - total_expenses:,.0f}
- Transaction Count: {len(transactions)}"""
    
    # Mutual Fund portfolio details
    mf_summary = ""
    if mf_data.get('mfTransactions'):
        mf_transactions = mf_data['mfTransactions']
        total_mf_investment = sum(t.get('amount', 0) for t in mf_transactions if t.get('type') == 'buy')
        mf_schemes = list(set(t.get('schemeName', 'Unknown') for t in mf_transactions))
        mf_summary = f"""
**Mutual Fund Portfolio:**
- Total MF Investment: ₹{total_mf_investment:,.0f}
- Number of Schemes: {len(mf_schemes)}
- Active Schemes: {', '.join(mf_schemes[:3])}{'...' if len(mf_schemes) > 3 else ''}"""
    
    # Stock portfolio details
    stock_summary = ""
    if stock_data.get('stockTransactions'):
        stock_transactions = stock_data['stockTransactions']
        total_stock_investment = sum(t.get('amount', 0) for t in stock_transactions if t.get('type') == 'buy')
        stock_symbols = list(set(t.get('symbol', 'Unknown') for t in stock_transactions))
        stock_summary = f"""
**Stock Portfolio:**
- Total Stock Investment: ₹{total_stock_investment:,.0f}
- Number of Stocks: {len(stock_symbols)}
- Holdings: {', '.join(stock_symbols[:5])}{'...' if len(stock_symbols) > 5 else ''}"""
    
    # EPF details
    epf_summary = ""
    if epf_data:
        monthly_contribution = epf_data.get('monthlyContribution', 0)
        employer_contribution = epf_data.get('employerContribution', 0)
        epf_summary = f"""
**EPF Details:**
- Current Balance: ₹{epf_balance:,.0f}
- Monthly Contribution: ₹{monthly_contribution:,.0f}
- Employer Contribution: ₹{employer_contribution:,.0f}"""
    
    # Credit profile
    credit_summary = ""
    if credit_data:
        credit_utilization = credit_data.get('creditUtilization', 'N/A')
        payment_history = credit_data.get('paymentHistory', 'N/A')
        credit_summary = f"""
**Credit Profile:**
- Credit Score: {credit_score}
- Credit Utilization: {credit_utilization}%
- Payment History: {payment_history}"""
    
    # Create comprehensive query with ALL financial data
    query = f"""
I am an Indian investor seeking personalized investment recommendations. Here is my COMPLETE financial profile based on real financial data:

**Personal Information:**
- Phone: {phone_number}
- Investment Amount: ₹{investment_amount:,.0f}

**Current Financial Position:**
- Total Net Worth: ₹{total_assets:,.0f}
- Credit Score: {credit_score}
- EPF Balance: ₹{epf_balance:,.0f}

**Asset Breakdown:**
{chr(10).join(asset_breakdown) if asset_breakdown else '  - No detailed asset breakdown available'}

{bank_summary}

{mf_summary}

{stock_summary}

{epf_summary}

{credit_summary}

**Raw Financial Data Summary:**
- Bank Transactions: {len(bank_data.get('bankTransactions', []))} records
- MF Transactions: {len(mf_data.get('mfTransactions', []))} records  
- Stock Transactions: {len(stock_data.get('stockTransactions', []))} records
- Net Worth Components: {len(net_worth_data.get('assetBreakdown', []))} assets

**Investment Requirements:**
Please conduct a comprehensive multi-agent analysis using your specialized sub-agents:

1. **DATA ANALYST ANALYSIS**: 
   - Research current Indian market conditions using Google search and Angel One APIs
   - Analyze sector performance, market trends, and economic indicators
   - Compare my existing holdings with market benchmarks
   - Identify growth opportunities in Indian markets

2. **RISK ANALYST EVALUATION**:
   - Assess my risk profile based on spending patterns and existing investments
   - Evaluate portfolio concentration risk from my current MF and stock holdings
   - Analyze my financial stability using bank transaction patterns
   - Recommend risk-appropriate investment allocation

3. **TRADING ANALYST STRATEGY**:
   - Develop specific investment strategies for the ₹{investment_amount:,.0f} amount
   - Recommend exact stocks, ETFs, and mutual funds with allocation percentages
   - Consider tax-efficient options (ELSS, PPF, etc.) based on my income level
   - Suggest diversification strategies to complement existing portfolio

4. **EXECUTION ANALYST PLANNING**:
   - Create detailed implementation plan with timeline
   - Recommend suitable investment platforms (Zerodha, Groww, Angel One, etc.)
   - Provide step-by-step execution guidance
   - Include monitoring and rebalancing recommendations

**Additional Context:**
- I prefer investments suitable for Indian markets
- Please consider tax implications under Indian tax laws
- Suggest both short-term and long-term investment strategies based on my cash flow
- Include emergency fund recommendations based on my expense patterns
- Factor in my existing MF and stock holdings for portfolio optimization

Please coordinate all sub-agents to provide a comprehensive, actionable investment plan with specific recommendations and detailed reasoning based on my actual financial data.
"""
    
    return query

async def interactive_chat():
    """Start an interactive chat session with the investment agent - EXACT COPY from run_interactive.py"""
    
    # Load environment variables
    load_dotenv()
    
    print("🏦 Investment Agent - CLI Mode (Working Version)")
    print("=" * 50)
    
    # Get CLI input first
    test_data_dir = "fi-mcp-dev/test_data_dir"
    if os.path.exists(test_data_dir):
        users = [d for d in os.listdir(test_data_dir) if os.path.isdir(os.path.join(test_data_dir, d))]
        print(f"\n📋 Available test users ({len(users)}):")
        for i, user in enumerate(users, 1):
            print(f"   {i:2d}. {user}")
    else:
        print("❌ Test data directory not found!")
        return False
    
    # Get user input
    print("\n" + "=" * 50)
    phone_number = input("📱 Enter phone number (from list above): ").strip()
    
    if phone_number not in users:
        print(f"❌ Invalid phone number. Please choose from: {', '.join(users)}")
        return False
    
    try:
        investment_amount = float(input("💰 Enter investment amount (₹): "))
        if investment_amount <= 0:
            print("❌ Investment amount must be positive")
            return False
    except ValueError:
        print("❌ Invalid investment amount")
        return False
    
    print(f"\n🔍 Loading data for user: {phone_number}")
    print(f"💰 Investment amount: ₹{investment_amount:,.2f}")
    
    # Load user data
    user_data = load_user_data(phone_number)
    if not user_data:
        print("❌ Failed to load user data")
        return False
    
    print(f"\n✅ Successfully loaded {len(user_data)} data files")
    
    # Create investment query
    investment_query = create_investment_query(user_data, phone_number, investment_amount)
    print(f"\n📝 Investment query created")
    
    try:
        # Create an in-memory runner using the investment_coordinator (root_agent)
        # This automatically orchestrates all sub-agents: data_analyst, risk_analyst, trading_analyst, execution_analyst
        runner = InMemoryRunner(agent=root_agent)
        
        # Create a session
        session = runner.session_service.create_session(
            app_name=runner.app_name, 
            user_id="cli_user"
        )
        
        print(f"✅ Investment agent started successfully!")
        print(f"🔄 Orchestrating sub-agents for comprehensive analysis...")
        print(f"   📊 Data Analyst - Market research & Angel One data")
        print(f"   ⚠️  Risk Analyst - Risk assessment & profile analysis")
        print(f"   📈 Trading Analyst - Investment strategy development")
        print(f"   🎯 Execution Analyst - Implementation planning")
        
        print("\n🤖 Generating comprehensive investment recommendation...")
        print("This may take a moment...")
        
        print("\n" + "=" * 50)
        print("📊 MULTI-AGENT INVESTMENT ANALYSIS")
        print("=" * 50)
        
        # Send the investment query to the investment coordinator
        # The coordinator will automatically delegate to appropriate sub-agents
        content = UserContent(parts=[Part(text=investment_query)])
        
        full_response = ""
        
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                chunk = event.content.parts[0].text
                print(chunk, end="", flush=True)
                full_response += chunk
        
        print("\n" + "=" * 50)
        print("✅ Multi-agent investment analysis completed!")
        print("📋 This recommendation includes:")
        print("   • Market data analysis from multiple sources")
        print("   • Personalized risk assessment")
        print("   • Strategic investment recommendations")
        print("   • Detailed execution plan")
        
        # Offer "Invest Now" functionality
        print("\n" + "🚀" * 25)
        print("READY TO INVEST NOW?")
        print("🚀" * 25)
        
        invest_choice = input("\n💰 Would you like to invest now through your demat account? (y/n): ").strip().lower()
        
        if invest_choice in ['y', 'yes']:
            try:
                # Import and use demat broker service
                from services.demat_broker_service import create_demat_broker_interface
                
                # Pass the full agent response for context
                recommendations = [full_response] if full_response else ["Investment recommendations generated"]
                
                # Launch demat broker selection interface
                create_demat_broker_interface(recommendations)
                
            except ImportError as e:
                print(f"❌ Demat broker service not available: {e}")
                print("💡 Please ensure all required dependencies are installed.")
            except Exception as e:
                print(f"❌ Error launching investment interface: {e}")
        else:
            print("\n📝 No problem! You can always invest later.")
            print("💡 Save these recommendations and execute them through your preferred broker when ready.")
            print("🏦 Supported brokers: Angel One, Zerodha, Groww, Upstox, IIFL, Paytm Money")
                
    except Exception as e:
        print(f"❌ Error starting investment agent: {e}")
        print("Please check your environment configuration and dependencies.")
        return False
    
    return True


def main():
    """Main function to run the interactive investment agent - EXACT COPY from run_interactive.py"""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Please create one based on .env.example")
        print("For local testing, you may need to set up Google Cloud credentials.")
        print()
        
        # Ask if user wants to continue anyway
        response = input("Do you want to continue anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Please set up your .env file and try again.")
            return
        
    try:
        # Run the async chat - EXACT COPY from run_interactive.py
        asyncio.run(interactive_chat())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()