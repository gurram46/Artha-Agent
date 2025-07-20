#!/usr/bin/env python3
"""
Debug script to see exactly what data summary is being passed to AI
"""

import os
from dotenv import load_dotenv
load_dotenv()

from utils.data_loader import DataLoader
from agents.analyst_agent.analyst import AnalystAgent

def debug_data_summary():
    print("🔍 Debugging Data Summary Generation...")
    
    # Initialize data loader and agent
    loader = DataLoader()
    analyst = AnalystAgent(loader)
    
    # Get financial data
    financial_data = loader.get_user_financial_data("test_user")
    
    # Generate the same data summary that gets sent to AI
    data_summary = analyst._create_enhanced_data_summary(financial_data)
    
    print("📊 Data Summary Sent to AI:")
    print("=" * 80)
    print(data_summary)
    print("=" * 80)
    
    # Also check the raw financial data structure
    print("\n🔍 Raw Financial Data Structure:")
    print(f"Keys: {list(financial_data.keys())}")
    
    if financial_data.get('net_worth'):
        net_worth = financial_data['net_worth']
        print(f"Net Worth Keys: {list(net_worth.keys())}")
        
        if net_worth.get('netWorthResponse'):
            nw_response = net_worth['netWorthResponse']
            print(f"Net Worth Response Keys: {list(nw_response.keys())}")
            
            if nw_response.get('assetValues'):
                print(f"Number of Assets: {len(nw_response['assetValues'])}")
                for i, asset in enumerate(nw_response['assetValues']):
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {}).get('units', 'N/A')
                    print(f"  Asset {i+1}: {asset_type} = ₹{value}")

if __name__ == "__main__":
    debug_data_summary()