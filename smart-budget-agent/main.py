import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

from gmail_parser import fetch_canara_emails
from sms_parser import fetch_sms_transactions

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🌐 Load environment variables
load_dotenv()

# 🔐 Initialize Firebase
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# 🔍 Connect to Firestore
db = firestore.client()

# 📬 Setup Gmail API client
def setup_gmail_service():
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")  # fallback if not set in .env
    creds = Credentials.from_authorized_user_file(token_path, scopes)
    return build('gmail', 'v1', credentials=creds)

service = setup_gmail_service()

# 💾 Load last SMS cursor (timestamp or message ID)
def load_last_sms_cursor():
    doc_ref = db.collection("meta").document("sms_cursor")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("last_cursor")
    return None  # if no previous cursor, start fresh

# 🧭 Save updated SMS cursor
def save_sms_cursor(cursor):
    db.collection("meta").document("sms_cursor").set({"last_cursor": cursor})

# 📨 Fetch Gmail transactions
email_txns = fetch_canara_emails(service)

# 📲 Fetch SMS transactions (with cursor)
sms_cursor = load_last_sms_cursor()
sms_txns, new_cursor = fetch_sms_transactions(sms_cursor)  # <-- pass cursor now

# 🔗 Merge both sources
all_txns = email_txns + sms_txns

# 🧠 Save each transaction to Firestore
for txn in all_txns:
    txn['date'] = str(date.today())
    db.collection("transactions").add(txn)
    db.collection("smart-budget-agent").add(txn)
    print(f"✅ Saved to Firestore: {txn}")

# 🔄 Save updated SMS cursor for next run
if new_cursor:
    save_sms_cursor(new_cursor)
