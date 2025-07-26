#!/usr/bin/env python3
"""
Test script to see actual investment agent output
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

async def test_agent():
    """Test the investment agent with sample data"""
    
    # Load environment variables
    load_dotenv()
    
    print("🧪 Testing Investment Agent Output")
    print("=" * 50)
    
    # Use a test user
    phone_number = "1111111111"  # Known test user
    investment_amount = 50000
    
    print(f"📱 Test User: {phone_number}")
    print(f"💰 Investment Amount: ₹{investment_amount:,.0f}")
    
    # Load user data
    user_data = load_user_data(phone_number)
    if not user_data:
        print("❌ Failed to load user data")
        return
    
    print(f"✅ Loaded {len(user_data)} data files")
    
    # Create a simple test query
    test_query = f"""
I am an Indian investor with ₹{investment_amount:,.0f} to invest. 

Based on my comprehensive financial data from Fi Money (including bank transactions, mutual fund holdings, stock portfolio, EPF details, credit profile, and net worth analysis), please provide:

1. **Data Analyst**: Use Google Search and Angel One APIs to research current Indian market conditions and specific investment opportunities
2. **Risk Analyst**: Assess my risk profile based on my actual financial data
3. **Trading Analyst**: Recommend specific stocks, ETFs, and mutual funds with exact allocation
4. **Execution Analyst**: Provide detailed implementation plan

Please ensure all sub-agents use my actual financial data and provide specific, actionable recommendations with current market data from Angel One APIs.
"""
    
    try:
        # Create runner
        runner = InMemoryRunner(agent=root_agent)
        
        # Create session
        session = runner.session_service.create_session(
            app_name=runner.app_name, 
            user_id="test_user"
        )
        
        print(f"\n🤖 Starting Investment Agent Analysis...")
        print("=" * 50)
        
        # Send query
        content = UserContent(parts=[Part(text=test_query)])
        
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
        
        print(f"\n\n" + "=" * 50)
        print("✅ Agent Analysis Complete!")
        print(f"📊 Total Response Length: {len(full_response)} characters")
        
        # Check if response contains specific indicators
        indicators = {
            "Angel One API used": "angel_one" in full_response.lower() or "market data" in full_response.lower(),
            "Google Search used": "search" in full_response.lower() or "research" in full_response.lower(),
            "Fi Money data used": "bank transaction" in full_response.lower() or "mutual fund" in full_response.lower(),
            "Specific recommendations": any(term in full_response.lower() for term in ["tcs", "hdfc", "icici", "sbi", "nifty"]),
            "Sub-agents called": "analyst" in full_response.lower()
        }
        
        print("\n📋 Analysis Indicators:")
        for indicator, found in indicators.items():
            status = "✅" if found else "❌"
            print(f"   {status} {indicator}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())