from googleapiclient.discovery import build
from utils import extract_transaction_details

def fetch_canara_emails(service):
    query = 'from:(noreply@canarabank.in) subject:(transaction OR debit OR purchase) newer_than:7d'
    results = service.users().messages().list(userId='me', q=query).execute()
    emails = []

    for msg in results.get('messages', []):
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = message.get('snippet', '')
        transaction = extract_transaction_details(snippet, source='gmail', bank='Canara')
        if transaction:
            emails.append(transaction)
    return emails
