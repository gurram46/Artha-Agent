#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import time
import random
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress specific warnings about function calls
warnings.filterwarnings("ignore", message=".*non-text parts.*function_call.*")
warnings.filterwarnings("ignore", message=".*function_call.*")
warnings.filterwarnings("ignore", message=".*Warning.*non-text parts.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*function_call.*")

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from investment_agent.agent import root_agent
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Part, UserContent
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed the required dependencies:")
    print("pip install google-adk google-genai python-dotenv")
    sys.exit(1)

def load_user_data(phone_number):
    """Load user data from JSON files in the test_data_dir"""
    user_dir = os.path.join("fi-mcp-dev", "test_data_dir", phone_number)
    
    if not os.path.exists(user_dir):
        print(f"❌ User data not found for phone number: {phone_number}")
        return None
    
    user_data = {}
    
    # Load all JSON files in the user directory
    for filename in os.listdir(user_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(user_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Use filename (without .json) as key
                    key = filename.replace('.json', '')
                    user_data[key] = data
                    print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    return user_data

def create_investment_query(user_data: dict, phone_number: str, investment_amount: float) -> str:
    """Create a comprehensive investment query from user data"""
    
    # Extract net worth information
    net_worth_data = user_data.get('fetch_net_worth', {})
    net_worth_response = net_worth_data.get('netWorthResponse', {})
    
    # Calculate total assets
    total_assets = 0
    asset_breakdown = []
    
    for asset_type, value in net_worth_response.items():
        if isinstance(value, (int, float)) and value > 0:
            total_assets += value
            asset_breakdown.append(f"  - {asset_type.replace('ASSET_TYPE_', '').replace('_', ' ').title()}: ₹{value:,.0f}")
    
    # Extract credit information
    credit_data = user_data.get('fetch_credit_report', {})
    credit_score = credit_data.get('bureauScore', 'Not available')
    
    # Extract EPF information
    epf_data = user_data.get('fetch_epf_details', {})
    epf_balance = 0
    if epf_data and 'epfDetails' in epf_data:
        for epf_account in epf_data['epfDetails']:
            if 'pfBalance' in epf_account:
                pf_balance = epf_account['pfBalance']
                epf_balance += pf_balance.get('employeeShare', 0) + pf_balance.get('employerShare', 0)
    
    # Extract mutual fund information
    mf_data = user_data.get('fetch_mf_transactions', {})
    mf_holdings = len(mf_data.get('mfTransactions', [])) if mf_data else 0
    
    # Extract stock information  
    stock_data = user_data.get('fetch_stock_transactions', {})
    stock_holdings = len(stock_data.get('stockTransactions', [])) if stock_data else 0
    
    # Create comprehensive query
    query = f"""
I am an Indian investor seeking personalized investment recommendations. Here is my complete financial profile:

**Personal Information:**
- Phone: {phone_number}
- Investment Amount: ₹{investment_amount:,.0f}

**Current Financial Position:**
- Total Net Worth: ₹{total_assets:,.0f}
- Credit Score: {credit_score}
- EPF Balance: ₹{epf_balance:,.0f}

**Asset Breakdown:**
{chr(10).join(asset_breakdown) if asset_breakdown else '  - No detailed asset breakdown available'}

**Current Investment Portfolio:**
- Mutual Fund Holdings: {mf_holdings} schemes
- Stock Holdings: {stock_holdings} stocks
- EPF Contribution: ₹{epf_balance:,.0f}

**Investment Requirements:**
1. Recommend specific Indian stocks, ETFs, and mutual funds suitable for my profile
2. Provide exact allocation percentages for the ₹{investment_amount:,.0f} investment
3. Consider my existing portfolio and suggest diversification strategies
4. Include tax-efficient investment options (ELSS, PPF, etc.)
5. Recommend suitable investment platforms (Zerodha, Groww, etc.)
6. Provide risk analysis based on my current financial position

**Additional Context:**
- I prefer investments suitable for Indian markets
- Please consider tax implications under Indian tax laws
- Suggest both short-term and long-term investment strategies
- Include emergency fund recommendations if needed

Please provide a detailed, actionable investment plan with specific recommendations and reasoning.
"""
    
    return query

async def main():
    # Load environment variables
    load_dotenv()
    
    print("🏦 Fi Money Investment Agent - CLI Version")
    print("=" * 50)
    
    # List available test users
    test_data_dir = "fi-mcp-dev/test_data_dir"
    if os.path.exists(test_data_dir):
        users = [d for d in os.listdir(test_data_dir) if os.path.isdir(os.path.join(test_data_dir, d))]
        print(f"\n📋 Available test users ({len(users)}):")
        for i, user in enumerate(users, 1):
            print(f"   {i:2d}. {user}")
    else:
        print("❌ Test data directory not found!")
        return
    
    # Get user input
    print("\n" + "=" * 50)
    phone_number = input("📱 Enter phone number (from list above): ").strip()
    
    if phone_number not in users:
        print(f"❌ Invalid phone number. Please choose from: {', '.join(users)}")
        return
    
    try:
        investment_amount = float(input("💰 Enter investment amount (₹): "))
        if investment_amount <= 0:
            print("❌ Investment amount must be positive")
            return
    except ValueError:
        print("❌ Invalid investment amount")
        return
    
    print(f"\n🔍 Loading data for user: {phone_number}")
    print(f"💰 Investment amount: ₹{investment_amount:,.2f}")
    
    # Load user data
    user_data = load_user_data(phone_number)
    if not user_data:
        print("❌ Failed to load user data")
        return
    
    print(f"\n✅ Successfully loaded {len(user_data)} data files")
    
    # Create investment query (like simple_investment_app.py)
    query = create_investment_query(user_data, phone_number, investment_amount)
    
    print(f"\n📝 Investment query created")
    
    try:
        # Create an in-memory runner (exact pattern from run_interactive.py)
        runner = InMemoryRunner(agent=root_agent)
        
        print("✅ Runner created successfully")
        
        # Create a session (exact pattern from run_interactive.py)
        try:
            session = runner.session_service.create_session(
                app_name=runner.app_name, 
                user_id=phone_number
            )
            print("✅ Session created successfully")
        except Exception as session_error:
            print(f"❌ Session creation error: {session_error}")
            print(f"Session error type: {type(session_error)}")
            raise
        
        print("\n🤖 Generating investment recommendation...")
        print("This may take a moment...")
        
        print("\n" + "=" * 50)
        print("📊 INVESTMENT RECOMMENDATION")
        print("=" * 50)
        
        # Send the query to the agent (exact pattern from run_interactive.py)
        content = UserContent(parts=[Part(text=query)])
        
        # Capture the full response for invest now feature
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
        print("✅ Investment recommendation completed!")
        
        # Offer "Invest Now" functionality with demat broker selection
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
        error_msg = str(e)
        print(f"\n❌ Error generating recommendation: {error_msg}")
        
        # Check if it's an API overload error and provide suggestions
        if "503" in error_msg or "overloaded" in error_msg.lower() or "unavailable" in error_msg.lower():
            print("\n💡 API Overload Suggestions:")
            print("   1. Try again in a few minutes when API load is lower")
            print("   2. Consider upgrading to Vertex AI for better reliability")
            print("   3. Run: python switch_to_vertex_ai.py")
        elif "api_key" in error_msg.lower() or "missing key" in error_msg.lower():
            print("\n💡 API Key Suggestions:")
            print("   1. Check that your .env file contains GOOGLE_API_KEY")
            print("   2. Verify your Google AI API key is valid")
            print("   3. Consider switching to Vertex AI: python switch_to_vertex_ai.py")

def run_cli():
    """Main function to run the investment CLI."""
    
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
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_cli()