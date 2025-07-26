import csv
import os
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from datetime import datetime

import firebase_admin


load_dotenv()

cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


COLLECTION_NAME = "smart-budget-agent"
EXPORT_FILE = "transaction_data.csv"

with open(EXPORT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["date", "category", "merchant", "amount", "weekday"])

    docs = db.collection(COLLECTION_NAME).stream()
    for doc in docs:
        tx = doc.to_dict()
        try:
            date_obj = datetime.strptime(tx.get("date", ""), "%d/%m/%Y")
            weekday = date_obj.strftime("%A")
            writer.writerow([
                tx.get("date", ""),
                tx.get("category", "Uncategorized"),
                tx.get("merchant", "Unknown"),
                tx.get("amount", 0.0),
                weekday
            ])
        except:
            continue
