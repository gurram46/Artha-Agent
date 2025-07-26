import os, re, base64, time
from dotenv import load_dotenv
from email import message_from_bytes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import firebase_admin
from firebase_admin import credentials, firestore
from budget_engine import analyze_transaction
from gemini_engine import suggest_budget_tips
from datetime import date

# 🔐 Load environment
load_dotenv()
COLLECTION = "smart-budget-agent"

# 🔧 Firebase
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 📩 Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN = 'oauth/token.json'
SECRETS = 'oauth/client_secret.json'

def authenticate_gmail():
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(SECRETS, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN, 'w') as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def extract_body(email_msg):
    body = email_msg.get_payload(decode=True)
    if body is None and email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                break
    return body.decode(errors="ignore") if body else ""

def parse_googlepay(body):
    amount = re.search(r"paid\s₹?\s?([\d,.]+)", body)
    merchant = re.search(r"Paid to[:\s]*([A-Za-z0-9 &\-]+)", body)
    date_match = re.search(r"on[:\s]*([0-9\-]+)", body)
    if not amount: return None
    return {
        "amount": float(amount.group(1).replace(",", "")),
        "merchant": merchant.group(1).strip() if merchant else "Unknown",
        "date": date_match.group(1).strip() if date_match else str(date.today()),
        "category": "Google Pay",
        "source": "Email",
        "timestamp": firestore.SERVER_TIMESTAMP
    }

def parse_canara(body):
    amt = re.search(r"(?:INR|Rs\.?)\s?([\d,]+)", body)
    date_match = re.search(r"(?:dated|on)\s+(\d{2}[/-]\d{2}[/-]\d{2,4})", body)
    account = re.search(r"(?:account|A/c)\s*([A-Z0-9\-]+)", body)
    if not amt: return None
    return {
        "amount": float(amt.group(1).replace(",", "")),
        "merchant": "Canara Bank",
        "date": date_match.group(1) if date_match else str(date.today()),
        "account": account.group(1) if account else "Unknown",
        "category": "Bank Debit",
        "source": "Email",
        "timestamp": firestore.SERVER_TIMESTAMP
    }

def process_emails():
    service = authenticate_gmail()
    query = '(from:googlepay OR from:canarabank) subject:(debit OR receipt)'
    msgs = service.users().messages().list(userId='me', q=query, maxResults=10).execute().get("messages", [])

    for msg in msgs:
        raw = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw_bytes = base64.urlsafe_b64decode(raw['raw'].encode('ASCII'))
        email_msg = message_from_bytes(raw_bytes)
        sender = email_msg.get('From', '').lower()
        body = extract_body(email_msg)

        if 'googlepay' in sender:
            txn = parse_googlepay(body)
        elif 'canarabank' in sender:
            txn = parse_canara(body)
        else:
            continue

        if txn:
            db.collection(COLLECTION).add(txn)
            time.sleep(1)
            analyze_transaction(txn)

def fetch_today_transactions():
    today_str = str(date.today())
    txns_ref = db.collection(COLLECTION)
    query = txns_ref.where("date", "==", today_str)
    return [doc.to_dict() for doc in query.stream()]

if __name__ == "__main__":
    print("📥 Starting receipt analysis...")
    
    transactions = fetch_today_transactions()
    
    from collections import defaultdict
    
    # 🧮 Organize by category
    category_totals = defaultdict(float)
    category_history = defaultdict(list)
    limit = {"Groceries": 5000, "Dining": 4000, "Bank Debit": 2000}  # example limits
    
    # 🔄 First pass — aggregate
    for txn in transactions:
        cat = txn["category"]
        category_totals[cat] += txn["amount"]
        category_history[cat].append(txn)
    
    # 📊 Second pass — analyze with full context
    for txn in transactions:
        cat = txn["category"]
        total = category_totals[cat]
        history = category_history[cat]
        budget_limit = limit.get(cat, 5000)
        
        analyze_transaction(txn)
        suggest_budget_tips(txn, total, budget_limit, history)
    
    print(f"✅ All transactions processed ({len(transactions)} total).")
