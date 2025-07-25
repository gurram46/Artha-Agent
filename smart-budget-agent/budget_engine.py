import os
import smtplib
import ssl
from dotenv import load_dotenv
from email.message import EmailMessage

import firebase_admin
from firebase_admin import credentials, firestore

from gemini_engine import suggest_budget_tips

# 🚀 Load environment variables
load_dotenv()

# 🔌 Initialize Firebase
def get_db():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS in .env")

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    return firestore.client()

db = get_db()
COLLECTION = "smart-budget-agent"

# 🔧 Budget thresholds
budget_limits = {
    "Dining": 3000,
    "Groceries": 5000,
    "Google Pay": 3500,
    "Bank Debit": 2500
}

# 📬 Email sender
def send_email(category, spent, limit, tips=[]):
    sender = receiver = os.getenv("USER_EMAIL")
    password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender or not password:
        raise ValueError("Missing email credentials in .env")

    msg = EmailMessage()
    msg["Subject"] = f"Budget Alert: {category}"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(f"""
You’ve spent ₹{spent:,.2f} in {category}, over your limit of ₹{limit:,.2f}.

Smart Suggestions:
• {tips[0] if tips else "Track weekly spending"}
• {tips[1] if len(tips) > 1 else "Consider spending caps"}
""")

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
            s.login(sender, password)
            s.send_message(msg)
        print("📬 Alert email sent")
    except Exception as e:
        print("❌ Email error:", e)

# 🔍 Transaction analyzer
def analyze_transaction(txn):
    category = txn.get("category")
    amount = txn.get("amount", 0)

    if not category or amount is None:
        print("❌ Transaction missing required fields")
        return

    limit = budget_limits.get(category)
    if not limit:
        print(f"⚠️ Skipping uncategorized: {category}")
        return

    # 🧮 Calculate spend
    docs = list(db.collection(COLLECTION).where("category", "==", category).stream())
    prev_total = sum(d.to_dict().get("amount", 0) for d in docs)
    total = prev_total + amount
    usage = (total / limit) * 100

    print(f"\n📊 Category: {category}")
    print(f"Spent: ₹{total:,.2f} / ₹{limit:,.2f} ({usage:.1f}%)")

    if usage >= 100:
        print("🚨 Overspent")
        tips = suggest_budget_tips(category, total, limit, docs)
        send_email(category, total, limit, tips)
    elif usage >= 90:
        print("⚠️ Near limit")
    else:
        print("✅ Within Budget")




