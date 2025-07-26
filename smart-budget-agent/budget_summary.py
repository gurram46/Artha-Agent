from datetime import datetime
from collections import defaultdict

# 💡 Suggested category-wise budget limits
CATEGORY_LIMITS = {
    "Groceries": 1500,
    "Transportation": 1000,
    "Entertainment": 300,
    "Bank Debit": 2500,
    "Google Pay": 400,
    "Utilities": 350,
    "Dining": 1000,
    "Shopping": 2000,
}

def generate_monthly_analysis(db, collection_name):
    print("\n🔍 Monthly Budget Analysis\n" + "="*60)

    # 🔄 Fetch transaction documents
    docs = db.collection(collection_name).stream()
    monthly_totals = defaultdict(lambda: defaultdict(float))
    current_month = datetime.now().strftime('%Y-%m')

    for doc in docs:
        tx = doc.to_dict()
        try:
            tx_date = datetime.strptime(tx.get('date', ''), '%d/%m/%Y')
            month_key = tx_date.strftime('%Y-%m')
            category = tx.get('category', 'Uncategorized')
            amount = float(tx.get('amount', 0))
            monthly_totals[month_key][category] += amount
        except Exception:
            continue  # Skip malformed entries

    if current_month not in monthly_totals:
        print(f"📅 No transactions found for current month: {current_month}")
        return

    print(f"📆 Current Month: {current_month}")
    for category, total in monthly_totals[current_month].items():
        limit = CATEGORY_LIMITS.get(category, 5000)  # fallback limit
        usage_pct = round((total / limit) * 100, 1)

        print(f"\n📊 Category: {category}")
        print(f"   • Spent: ₹{total:.2f}")
        print(f"   • Limit: ₹{limit}")
        print(f"   • Usage: {usage_pct}%")

        # 🧠 Advice logic
        if usage_pct >= 100:
            print("   ⚠️ Over budget! Consider reducing future spend.")
        elif usage_pct >= 80:
            print("   🚨 Approaching limit. Be cautious this week.")
        elif usage_pct <= 40:
            print("   ✅ Excellent! You're well below budget.")
        else:
            print("   👍 You're within budget. Keep up the balance!")

    print("\n✨ Monthly summary complete\n" + "="*60)
