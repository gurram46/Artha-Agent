# Artha AI - Fi Money MCP Integration

## 🎯 Overview
Artha AI now uses **Fi Money MCP (Model Context Protocol)** to access real financial data from users' connected accounts. This integration provides actual portfolio data, transaction history, credit scores, and EPF details for accurate, personalized financial advice.

## 🌟 Key Innovation: Real Data-Driven Advice

Instead of generic recommendations, Artha AI now provides:
- **Actual portfolio XIRR** from your mutual funds
- **Real credit score** and debt analysis
- **Live bank balances** for cash flow planning
- **EPF balance** for retirement projections
- **Transaction patterns** from your investment history

## 🏗️ Architecture with Fi MCP

```
User Query → Gemini Routing → Agent with Fi MCP Data → Personalized Advice
                                       ↓
                              Fetch Real Data:
                              - Net Worth
                              - Credit Report  
                              - EPF Details
                              - MF Transactions
```

## 📊 Fi MCP Tools Integration

### 1. **fetch_net_worth**
Provides comprehensive wealth snapshot:
```python
# Real data fetched
{
  "total_net_worth": 2500000,  # Actual net worth
  "mutual_funds": [
    {
      "scheme_name": "HDFC Top 100 Fund",
      "current_value": 150000,
      "invested_value": 100000,
      "xirr": 18.5  # Actual returns
    }
  ],
  "bank_accounts": [...],
  "epf_balance": 500000
}
```

### 2. **fetch_credit_report**
Real credit health analysis:
```python
{
  "credit_score": 780,  # Actual CIBIL/Experian score
  "active_accounts": 3,
  "credit_utilization": 22.5,  # Actual utilization %
  "total_outstanding": 50000
}
```

### 3. **fetch_epf_details**
Retirement corpus tracking:
```python
{
  "current_balance": 850000,
  "employee_contribution": 425000,
  "employer_contribution": 425000,
  "employment_history": [...]
}
```

### 4. **fetch_mf_transactions**
Investment behavior analysis:
```python
{
  "transactions": [
    {
      "date": "2024-01-15",
      "type": "BUY",
      "amount": 10000,
      "scheme": "Axis Bluechip Fund"
    }
  ]
}
```

## 🤖 How Agents Use Real Data

### Past Agent with Fi MCP
```python
# Before: Generic advice
"Based on typical returns, you should expect 12% annually"

# Now: Actual portfolio analysis
"Your portfolio has delivered 15.8% XIRR over the last 3 years.
Your best performer is Axis Bluechip (22% XIRR).
Your SIP discipline shows in 24 consistent monthly investments."
```

### Present Agent with Fi MCP
```python
# Before: Estimates
"You might be spending too much"

# Now: Real numbers
"Your current liquid cash is ₹2,50,000 across 3 accounts.
Credit utilization at 22% is healthy (below 30%).
Monthly SIP commitment of ₹35,000 leaves ₹45,000 surplus."
```

### Future Agent with Fi MCP
```python
# Before: Rule of thumb
"Save 20% for retirement"

# Now: Personalized projection
"Current trajectory: ₹3.2 Cr by retirement (including ₹85L EPF)
Gap to ₹5 Cr goal: ₹1.8 Cr
Required: Increase SIP by ₹12,000/month"
```

## 🚀 Setup Instructions

### 1. Environment Setup
```bash
# Add to .env
GEMINI_API_KEY=your-gemini-api-key
# Fi MCP endpoint is pre-configured
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
# Includes mcp client library
```

### 3. Connect Fi Money Accounts
Users must connect accounts in Fi Money app:
- Bank accounts for cash flow
- Mutual funds for investment analysis
- Credit cards for debt tracking
- EPF for retirement planning

## 🧪 Testing with Real Data

### Test Complete Analysis
```bash
curl -X POST http://localhost:5000/api/chat/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze my complete financial health"
  }'
```

### Response with Real Data
```json
{
  "analysis": {
    "summary": "Net worth of ₹25L with healthy 15.8% portfolio returns",
    "past_insights": {
      "portfolio_xirr": 15.8,
      "best_fund": "Axis Bluechip - 22% XIRR",
      "investment_consistency": "High - 24 months SIP"
    },
    "present_status": {
      "liquid_cash": 250000,
      "credit_score": 780,
      "monthly_surplus": 45000
    },
    "future_projection": {
      "retirement_corpus": 32000000,
      "on_track": true,
      "epf_included": true
    }
  },
  "data_source": "Fi Money MCP - Real Account Data"
}
```

## 📈 Data Quality Indicators

The system shows data completeness:
```json
{
  "data_completeness": {
    "bank_accounts": true,
    "mutual_funds": true,
    "credit_score": true,
    "epf": false,  // Not connected
    "percentage": 75,
    "recommendation": "Connect EPF for complete retirement planning"
  }
}
```

## 🔒 Security & Privacy

- **No data storage**: Real-time fetch only
- **Secure MCP protocol**: Encrypted communication
- **User consent**: Explicit account connection required
- **Read-only access**: Cannot modify accounts

## 🎯 Use Cases with Real Data

### 1. Portfolio Rebalancing
```
Query: "Should I rebalance my portfolio?"
Uses: Actual asset allocation, current XIRR by asset class
Result: "Your equity allocation at 85% exceeds target. Consider 15% debt allocation."
```

### 2. Loan Prioritization
```
Query: "Which loan should I pay off first?"
Uses: Real interest rates from credit report
Result: "Pay off Credit Card (18% APR) before Personal Loan (12% APR)"
```

### 3. Retirement Readiness
```
Query: "Can I retire at 50?"
Uses: Actual savings rate, EPF balance, portfolio returns
Result: "Current trajectory reaches ₹2.8 Cr by 50. Need ₹3.5 Cr. Feasible with ₹10k additional SIP."
```

## 🚨 Error Handling

When accounts aren't connected:
```json
{
  "error": "No mutual fund data available",
  "action_required": "Connect mutual fund accounts in Fi Money app",
  "partial_analysis": "Based on available bank data..."
}
```

## 📊 Advantages Over Generic Systems

| Feature | Generic Advisor | Artha AI with Fi MCP |
|---------|----------------|----------------------|
| Returns | Assumed 12% | Your actual 15.8% XIRR |
| Net Worth | User input | Live ₹25,00,000 |
| Credit Score | Unknown | Actual 780 |
| Cash Flow | Estimated | Real ₹2,50,000 liquid |
| EPF | Guessed | Exact ₹8,50,000 |

## 🔄 Data Refresh

- **Real-time**: Every query fetches latest data
- **No caching**: Always current information
- **Transaction sync**: Includes today's transactions

## 📱 Fi Money App Integration

Users need Fi Money app to:
1. Connect bank accounts
2. Import mutual fund portfolios
3. Link credit score
4. Connect EPF/NPS accounts

## 🎮 Advanced Features

### Transaction Pattern Analysis
```python
# Analyzes actual transaction history
"Your SIP discipline: 100% (24/24 months)
Average investment: ₹35,000/month
Lump sum pattern: Bonus months (Apr, Oct)"
```

### Credit Optimization
```python
# Uses real credit report data
"Reduce utilization from 22% to 10% = +15 score points
Close unused card (3 years old) = -5 points
Net benefit: +10 to reach 790"
```

### Goal-Based Planning
```python
# Projects using actual returns
"Home goal (₹50L in 5 years):
- Current savings rate: ₹35,000
- Your portfolio return: 15.8%
- Required: ₹58,000/month
- Gap: ₹23,000/month"
```

## 🚀 Future Enhancements

1. **Stock portfolio integration** (when Fi MCP adds support)
2. **US stock analysis** for Fi global investors
3. **NPS integration** for additional retirement planning
4. **Expense categorization** from bank transactions

## 💡 Best Practices

1. **Connect all accounts** for comprehensive analysis
2. **Regular syncing** ensures accurate advice
3. **Update goals** in user context for better projections
4. **Review data completeness** indicators

The Fi MCP integration transforms Artha AI from a generic advisor to your personal financial analyst with real, actionable insights based on your actual financial data!