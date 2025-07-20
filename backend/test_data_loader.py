#!/usr/bin/env python3
"""
Test script to verify MCP data loading functionality
"""

from utils.data_loader import DataLoader

def test_data_loader():
    print("🔍 Testing MCP Data Loader...")
    
    # Initialize data loader
    loader = DataLoader()
    
    # Check if data is available
    print(f"Data available: {loader.is_data_available()}")
    
    # Get data summary
    summary = loader.get_data_summary()
    print(f"Data summary: {summary}")
    
    # Test financial data loading
    financial_data = loader.get_user_financial_data("test_user")
    print(f"Financial data keys: {list(financial_data.keys())}")
    
    # Check specific data
    if financial_data.get('net_worth'):
        net_worth = financial_data['net_worth']
        print(f"Net worth data available: {bool(net_worth)}")
        if net_worth.get('netWorthResponse'):
            print(f"Net worth response available: {bool(net_worth['netWorthResponse'])}")
            if net_worth['netWorthResponse'].get('assetValues'):
                assets = net_worth['netWorthResponse']['assetValues']
                print(f"Number of assets: {len(assets)}")
                for asset in assets[:3]:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {}).get('units', 'N/A')
                    print(f"  - {asset_type}: ₹{value}")
    
    if financial_data.get('credit_report'):
        credit = financial_data['credit_report']
        print(f"Credit report data available: {bool(credit)}")
    
    if financial_data.get('mf_transactions'):
        mf = financial_data['mf_transactions']
        print(f"MF transactions data available: {bool(mf)}")
        
    if financial_data.get('epf_details'):
        epf = financial_data['epf_details']
        print(f"EPF details data available: {bool(epf)}")

if __name__ == "__main__":
    test_data_loader()