import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Firebase initialization
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_budget_alert(category, total, limit, merchants):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_APP_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER", sender)

    msg = MIMEMultipart()
    msg["Subject"] = f"🚨 Budget Alert: {category} Overspent"
    msg["From"] = sender
    msg["To"] = receiver

    body = f"""
    ⚠️ Budget Alert for {category}
    
    💰 Current Spend: ₹{total:,.2f}
    📊 Budget Limit: ₹{limit:,.2f}
    🔄 Over by: ₹{(total-limit):,.2f}
    📈 Usage: {(total/limit)*100:.1f}%
    
    🏪 Recent transactions at:
    {', '.join(set(merchants))}
    
    💡 Recommendations:
    • Set a daily limit of ₹{(limit/30):,.2f}
    • Consider reducing spending at frequent merchants
    • Track expenses more closely for the rest of the month
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("   • 📧 Budget alert email sent!")
    except Exception as e:
        print(f"   • ❌ Failed to send email alert: {str(e)}")

def suggest_budget_tips(txn, total, limit, history):
    category = txn.get("category", "Unknown")
    # Safely get merchant names, filtering out None values
    merchants = [tx.get("merchant", "Unknown") for tx in history if tx.get("merchant")]
    
    prompt = f"""
Category: {category}
Spent: ₹{total}, Limit: ₹{limit}
Frequent Merchants: {merchants}

Suggest 2 budget tips to reduce overspending in this category.
"""
    # Gemini call placeholder — insert API logic here
    print(f"\n💡 Budget Tips for {category}:")
    print(f"   • Current spend: ₹{total:,.2f} / ₹{limit:,.2f} ({(total/limit)*100:.1f}%)")
    if total > limit:
        print("   • ⚠️ Over budget!")
        print(f"   • Consider reducing spending at: {', '.join(set(merchants))}")
        print(f"   • Set a daily limit of ₹{(limit/30):,.2f} to stay on track")
        # Send email alert for over-budget categories
        send_budget_alert(category, total, limit, merchants)
    else:
        print("   • ✅ Within budget")
        print(f"   • Safe to spend: ₹{(limit-total):,.2f}")
