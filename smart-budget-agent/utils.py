import re

def extract_transaction_details(text, source, bank):
    pattern = r'(?:Rs\.?|INR|₹)\s?([\d,.]+).*?(?:debited|credited|spent).*?(?:at|in)\s(.+?)(?:\.|$)'
    match = re.search(pattern, text)
    if match:
        return {
            'source': source,
            'bank': bank,
            'amount': float(match.group(1).replace(',', '')),
            'merchant': match.group(2).strip()
        }
    return None
