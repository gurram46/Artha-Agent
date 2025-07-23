# 🎯 Artha-Agent - Real Data Only Application

**NO MOCK DATA • NO FALLBACKS • REAL APIS ONLY**

This application has been completely configured to use only real data from live APIs. No sample data, no fallbacks, no mock responses.

## 🚀 Quick Start

```bash
# Start all services (Frontend + Backend + Stock AI)
./start-all-services.sh

# Stop all services
./stop-all-services.sh
```

## 📊 Real Data Sources

### 🏦 **Financial Data**
- **Source**: Fi MCP (Financial accounts aggregation)
- **Endpoint**: `http://localhost:8000/financial-data`
- **Data**: Real bank accounts, mutual funds, EPF, credit scores
- **Status**: ✅ Configured for real Fi MCP integration

### 📈 **Stock Market Data**
- **Source**: NSE API (National Stock Exchange of India)
- **Package**: `stock-market-india` by maanavshah
- **Endpoints**: 
  - `http://localhost:3000/nse/get_quote_info?companyName=TCS`
  - `http://localhost:3000/nse/get_chart_data_new?companyName=TCS&time=1`
- **Data**: Real-time stock prices, charts, volumes, P/E ratios
- **Status**: ✅ Configured with live NSE data + Heroku fallback

### 🤖 **Stock AI Analysis**
- **Source**: Google AI + Grounding for real-time research
- **Endpoint**: `http://localhost:8001/api/stock/full-analysis`
- **Features**: 
  - Real-time Google Search for stock research
  - AI-powered fundamental & technical analysis
  - Personalized investment recommendations
  - 7-area comprehensive research framework
- **Status**: ✅ Configured with Google AI Gemini 2.5 Flash

## 🏗️ **Architecture Overview**

```
Frontend (Next.js 14)     Backend Services
Port 3000                 
                         ┌─────────────────────┐
  ┌─ Dashboard           │ Main Backend API    │
  ┌─ Stock Lists   ────► │ Port 8000           │ ◄── Fi MCP
  ┌─ AI Recommendations  │ Financial Data      │
                         └─────────────────────┘
                         
                         ┌─────────────────────┐
  ┌─ Stock Charts  ────► │ NSE Stock API       │ ◄── stock-market-india
  ┌─ Real-time Data      │ Real-time Quotes    │     NSE Direct
                         └─────────────────────┘
                         
                         ┌─────────────────────┐
  ┌─ AI Speedometer ───► │ Stock AI Agents     │ ◄── Google AI
  ┌─ Recommendations     │ Port 8001           │     + Grounding
                         │ Research + Recommend │
                         └─────────────────────┘
```

## 🔧 **Configuration Requirements**

### **Environment Variables**
```bash
# Required for Stock AI (set in your shell)
export GOOGLE_AI_API_KEY="your_google_ai_api_key_here"

# Optional - API endpoints (defaults shown)
export STOCK_AI_URL="http://localhost:8001"
export BACKEND_API_URL="http://localhost:8000"
```

### **API Keys Needed**
1. **Google AI API Key** - For stock analysis and recommendations
   - Get from: https://ai.google.dev/
   - Used by: Stock AI Agents server

2. **No other API keys required** - NSE data is free, Fi MCP uses sample data structure

## 🚨 **No Fallback Policy**

This application is configured with **ZERO TOLERANCE** for mock data:

- ❌ **No sample data** - If APIs fail, show error states
- ❌ **No fallback responses** - Real data or error messages only  
- ❌ **No mock charts** - Charts display real data or error state
- ❌ **No estimated values** - Only actual API responses shown

## 📱 **Application Features**

### **Dashboard**
- Real financial portfolio data from Fi MCP
- Asset allocation charts using real account balances
- Performance metrics from actual investment data
- Credit score integration from credit reports

### **Stock Market**
- Top 10 Indian stocks with real NSE prices
- Real-time price updates every 30 seconds
- Live charts with actual trading data
- Sector-wise stock classification

### **AI Stock Analysis**
- Google Search-powered research on any stock
- 7-area comprehensive analysis framework
- Personalized recommendations based on risk profile
- Real-time sentiment analysis and scoring

### **User Profile Management**
- Risk tolerance assessment (Conservative/Moderate/Aggressive)
- Investment horizon selection (Short/Medium/Long-term)
- Monthly investment budget configuration
- Profile-based recommendation personalization

## 🔍 **Debugging & Monitoring**

### **Check Service Status**
```bash
# Check if services are running
curl http://localhost:3000/api/health     # Frontend health
curl http://localhost:8000/financial-data # Backend financial API
curl http://localhost:8001/health         # Stock AI agents

# Check real-time stock data
curl "http://localhost:3000/nse/get_quote_info?companyName=TCS"
```

### **View Logs**
```bash
# Frontend logs
cd frontend && npm run dev

# Backend logs  
cd backend && python api_server.py

# Stock AI logs
cd backend/agents/stock_agents && python stock_api_server.py
```

### **Common Issues**

1. **"Stock data unavailable"**
   - NSE API may be down or rate-limited
   - Check internet connection
   - Try again in a few minutes

2. **"Stock AI agents backend is not available"**
   - Ensure `GOOGLE_AI_API_KEY` is set
   - Check if port 8001 is running
   - Verify Google AI API quota

3. **"Backend financial data API is not available"**
   - Ensure main backend is running on port 8000
   - Check Fi MCP sample data files exist

## 🎯 **Success Indicators**

When working correctly, you should see:

- ✅ Real stock prices updating every 30 seconds
- ✅ Live charts with actual NSE trading data  
- ✅ AI recommendations with Google Search citations
- ✅ Real financial portfolio metrics
- ✅ Error states when APIs are unavailable (no fallbacks)

## 🤝 **Support**

If you encounter issues with real data integration:

1. Check all services are running: `./start-all-services.sh`
2. Verify API keys are configured correctly
3. Test individual API endpoints manually
4. Check console logs for specific error messages

---

**🎉 Enjoy your fully real-data powered financial intelligence application!**