# Fi Money MCP Development Server Setup Guide

This guide helps you set up and test the Artha Investment Agent with the Fi Money MCP development server for the hackathon.

## 🎯 Overview

The Fi Money MCP development server provides dummy financial data for testing without accessing real user accounts. It simulates various user scenarios with different investment profiles.

## 📋 Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- Go (for Fi Money MCP dev server)
- Firebase CLI
- Git

## 🚀 Setup Steps

### 1. Clone Fi Money MCP Development Server

```bash
# Clone the Fi Money MCP development server
git clone https://github.com/epiFi/fi-mcp-dev.git
cd fi-mcp-dev

# Run the development server
go run main.go
```

The server will start on `http://localhost:8080`

### 2. Setup Firebase Functions

```bash
# Navigate to your project directory
cd investment-agent-standalone

# Install Firebase CLI (if not installed)
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase project (if not done)
firebase init

# Install Python dependencies for functions
cd functions
pip install -r requirements.txt
cd ..
```

### 3. Configure Environment Variables

Create or update `functions/.env`:

```env
# Firebase Configuration
GOOGLE_CLOUD_PROJECT=artha-investment-agent
FIREBASE_PROJECT_ID=artha-investment-agent
GOOGLE_AI_API_KEY=your_gemini_api_key_here

# Fi Money MCP Server (Development)
FI_MONEY_MCP_SERVER_URL=http://localhost:8080
FI_MONEY_MCP_SERVER_TOKEN=dummy_token_for_dev

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
```

### 4. Start Firebase Emulators

```bash
# Start Firebase emulators
firebase emulators:start
```

This will start:
- Functions emulator on `http://localhost:5001`
- Firestore emulator on `http://localhost:8080`
- Firebase UI on `http://localhost:4000`

## 🧪 Testing Scenarios

The Fi Money MCP dev server provides various user scenarios. Here are the key test phone numbers:

| Phone Number | Scenario Description |
|--------------|---------------------|
| `2222222222` | All assets connected - Large MF portfolio (9 funds) |
| `3333333333` | All assets connected - Small MF portfolio (1 fund) |
| `7777777777` | Debt-Heavy Low Performer - Poor returns, high liabilities |
| `8888888888` | SIP Samurai - Regular SIP investor with moderate returns |
| `1313131313` | Balanced Growth Tracker - Well diversified portfolio |
| `2020202020` | Starter Saver - New investor with minimal investments |
| `1111111111` | No assets connected - Only savings account |
| `6666666666` | All assets except bank account |

## 🔧 API Testing

### Test User Profile Endpoint

```bash
curl -X POST http://localhost:5001/artha-investment-agent/us-central1/api/user/profile \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "2222222222"}'
```

### Test Investment Recommendations

```bash
curl -X POST http://localhost:5001/artha-investment-agent/us-central1/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "2222222222",
    "investment_amount": 50000,
    "investment_goal": "wealth creation",
    "time_horizon": "5 years"
  }'
```

### Test Demat Accounts

```bash
curl -X GET http://localhost:5001/artha-investment-agent/us-central1/api/demat/accounts
```

## 🐍 Python Test Script

Run the provided test script:

```bash
python test_firebase_functions.py
```

This script will:
1. Test Fi Money MCP server connection
2. Test Firebase Functions endpoints
3. Validate data flow between services

## 📊 Expected Data Structure

### Fi Money Response Format

```json
{
  "netWorthResponse": {
    "totalNetWorthValue": {
      "currencyCode": "INR",
      "units": "500000"
    },
    "assetValues": [...]
  },
  "mfSchemeAnalytics": {
    "schemeAnalytics": [...]
  },
  "accountDetailsBulkResponse": {
    "accountDetailsMap": {...}
  }
}
```

### Investment Recommendations Format

```json
{
  "success": true,
  "recommendations": [
    {
      "id": "rec_1",
      "name": "Nippon India ETF Nifty BeES",
      "symbol": "NIFTYBEES",
      "type": "etf",
      "exchange": "NSE",
      "allocation_percentage": 40,
      "recommended_amount": 20000,
      "rationale": "Broad market exposure through Nifty 50 index"
    }
  ]
}
```

## 🔍 Debugging Tips

### Check Fi Money Server Status

```bash
curl http://localhost:8080/health
```

### Check Firebase Functions Status

```bash
curl http://localhost:5001/artha-investment-agent/us-central1/api/health
```

### View Firebase Emulator Logs

The Firebase emulator will show logs in the terminal. Look for:
- Function initialization messages
- API request/response logs
- Error messages

### Common Issues

1. **Port Conflicts**: Make sure ports 5001, 8080, and 4000 are available
2. **Environment Variables**: Ensure all required env vars are set
3. **Dependencies**: Run `pip install -r requirements.txt` in functions directory
4. **API Keys**: Update Gemini AI API key in `.env` file

## 📱 Frontend Integration

For frontend integration, use these endpoints:

- **Base URL**: `http://localhost:5001/artha-investment-agent/us-central1/api`
- **User Profile**: `POST /user/profile`
- **Recommendations**: `POST /recommendations`
- **Demat Accounts**: `GET /demat/accounts`
- **Demat Redirect**: `POST /demat/redirect`

## 🚀 Deployment

For hackathon deployment:

```bash
# Deploy to Firebase
firebase deploy --only functions

# Or deploy specific function
firebase deploy --only functions:api
```

## 📞 Support

If you encounter issues:
1. Check the Fi Money MCP dev server logs
2. Verify Firebase emulator status
3. Review function logs in Firebase console
4. Test with different phone number scenarios

## 🎉 Success Criteria

Your setup is working correctly when:
- ✅ Fi Money MCP server responds to requests
- ✅ Firebase Functions start without errors
- ✅ User profile data is fetched successfully
- ✅ Investment recommendations are generated
- ✅ All test scenarios pass

Happy hacking! 🚀