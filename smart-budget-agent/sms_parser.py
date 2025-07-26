import re
from utils import extract_transaction_details

def fetch_sms_transactions(cursor=None):
    # Simulated transaction data
    dummy_sms = [
        {"vendor": "Canara Bank", "amount": 1200, "category": "Fuel"},
        {"vendor": "HDFC Bank", "amount": 850, "category": "Groceries"},
        {"vendor": "SBI ATM", "amount": 5000, "category": "Withdrawal"}
    ]

    # Simulate new cursor for next run
    new_cursor = "mock_cursor_20250725"
    
    return dummy_sms, new_cursor


def detect_bank(address):
    if 'SBI' in address: return 'SBI'
    if 'HDFC' in address: return 'HDFC'
    return 'Unknown'
