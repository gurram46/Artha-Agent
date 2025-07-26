# 🤝 Team Handover Guide - Investment Agent Project

Welcome to the Artha Investment Agent project! This guide will help you understand the project structure, setup requirements, and how to continue development.

## 📋 Project Overview

The **Artha Investment Agent** is an AI-powered investment advisor specifically designed for Indian financial markets. It integrates with:
- **Fi Money**: For real user financial data
- **Angel One APIs**: For live market data and investment execution
- **Google AI (Gemini)**: For intelligent investment recommendations

### 🔄 Complete User Journey
```
User Input → Fi Money Data → AI Analysis → Recommendations → Invest Now → Broker Execution
```

### 🚀 New: Invest Now Feature
After receiving recommendations, users can immediately execute investments through:
- **Angel One** (API Integration with live prices)
- **Zerodha, Groww, Upstox** (Web platform integration)
- **IIFL, Paytm Money** (Direct platform access)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│ Investment Agent │───▶│ Recommendations │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Sub-Agents    │
                    │                 │
                    │ • Data Analyst  │
                    │ • Trading       │
                    │ • Execution     │
                    │ • Risk Analyst  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Data Sources  │
                    │                 │
                    │ • Fi Money MCP  │
                    │ • Angel One API │
                    │ • Google Search │
                    └─────────────────┘
```

## 🚀 Invest Now Feature Implementation

### 📁 Key Files
- `services/broker_integration.py` - Main broker integration service
- `simple_investment_cli.py` - CLI with invest now functionality
- `test_invest_now.py` - Test script for the feature
- `demo_invest_now.py` - Complete demo of the feature

### 🏦 Broker Support
| Broker | Integration Type | Features |
|--------|------------------|----------|
| Angel One | API + Web | Live prices, basket orders, real-time data |
| Zerodha | Web Platform | Kite platform, manual execution guidance |
| Groww | Web Platform | User-friendly interface, step-by-step guide |
| Upstox | Web Platform | Pro platform, advanced tools |
| IIFL | Web Platform | Full-service broker, research tools |
| Paytm Money | Web Platform | Digital-first, zero brokerage delivery |

### 🔧 How It Works
1. **Recommendation Parsing**: Extracts investment details from AI response
2. **Broker Selection**: User chooses preferred broker
3. **URL Generation**: Creates broker-specific investment URLs
4. **Platform Launch**: Opens broker platform in browser
5. **Execution Guidance**: Provides step-by-step instructions

### 🧪 Testing
```bash
# Test broker selection interface
python test_invest_now.py

# Full demo with sample recommendations
python demo_invest_now.py

# Test in CLI
python simple_investment_cli.py
```

## 🔑 API Keys & Credentials You Need to Replace

### 1. **Google AI API Key** (Required)
```env
GOOGLE_API_KEY=your_google_ai_api_key_here
```
**How to get:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and paste in `.env` file

### 2. **Angel One API Credentials** (Optional but Recommended)
```env
# Angel One API Configuration
ANGEL_ONE_API_KEY=your_angel_one_api_key_here
ANGEL_ONE_CLIENT_ID=your_angel_one_client_id_here
ANGEL_ONE_PASSWORD=your_angel_one_password_here
ANGEL_ONE_TOTP_SECRET=your_angel_one_totp_secret_here
```
**How to get:**
1. Create account at [Angel One](https://www.angelone.in/)
2. Apply for API access through their developer portal
3. Get API key, client ID, password, and TOTP secret
4. **Note**: Currently the project uses simulated data, so this is optional

### 3. **Flask Configuration**
```env
FLASK_SECRET_KEY=your_flask_secret_key_here
FLASK_ENV=development
```
**How to generate:**
```python
import secrets
print(secrets.token_hex(32))  # Use this as your FLASK_SECRET_KEY
```

## 🚀 Quick Setup for New Team Member

### Step 1: Environment Setup
```bash
# Clone the project (if not already done)
cd investment-agent-standalone

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env file with your credentials
notepad .env
```

### Step 2: Test the Setup
```bash
# Test the CLI version (simplest)
python simple_investment_cli.py

# Test the interactive version
python run_interactive.py

# Test the web app version
python run_web_app.py
```

### Step 3: Verify Angel One Integration
```bash
# Check if Angel One tool is working
python -c "
from investment_agent.tools.angel_one_tool import AngelOneMarketTool
import asyncio
tool = AngelOneMarketTool()
result = asyncio.run(tool.run_async('Get market status'))
print(result)
"
```

## 📊 How Angel One API Integration Works

### Current Implementation Status
- ✅ **Angel One Tool**: Implemented with simulated data
- ✅ **Market Data**: Stocks, ETFs, indices with realistic prices
- ✅ **Integration**: Works with all sub-agents
- 🔄 **Real API**: Ready for real Angel One API when credentials are added

### Data Flow Process

1. **User asks investment question**
   ```
   "Should I invest ₹50,000 in Nifty ETFs?"
   ```

2. **Investment Agent analyzes request**
   - Identifies need for market data
   - Routes to Data Analyst sub-agent

3. **Data Analyst uses Angel One Tool**
   ```python
   # investment_agent/sub_agents/data_analyst/agent.py
   tools = [google_search, angel_one_tool]  # Angel One tool available
   ```

4. **Angel One Tool fetches data**
   ```python
   # investment_agent/tools/angel_one_tool.py
   async def run_async(self, query: str) -> str:
       # Simulates Angel One API calls
       # Returns JSON with market data
   ```

5. **Agent provides recommendation**
   ```
   📊 NIFTYBEES: ₹248.75 (+0.87%)
   💰 Investment: 201 units for ₹49,999
   ✅ Recommendation: BUY (Good entry level)
   ```

### Angel One API Endpoints (When Real API is Connected)

| API Type | Purpose | Authentication | Status |
|----------|---------|----------------|---------|
| **Market API** | Live prices, market status | Basic/None | 🔄 Ready |
| **Historical API** | Price history, charts | Basic | 🔄 Ready |
| **Trading API** | Order placement, portfolio | Full (TOTP) | 🔄 Ready |

### Code Files to Understand

1. **`investment_agent/tools/angel_one_tool.py`**
   - Main Angel One integration
   - Simulates API responses
   - Easy to replace with real API calls

2. **`services/enhanced_angel_one_service.py`**
   - Service layer for Angel One APIs
   - Handles authentication
   - Ready for real API integration

3. **`investment_agent/sub_agents/data_analyst/agent.py`**
   - Uses Angel One tool for market data
   - Combines with Google Search for analysis

## 🧪 Testing Different Scenarios

### Test Users (Fi Money Integration)
The project includes test data for different user profiles:

| Phone Number | Profile Type | Description |
|--------------|--------------|-------------|
| `2222222222` | Large Portfolio | 9 mutual funds, high net worth |
| `3333333333` | Small Portfolio | 1 mutual fund, beginner |
| `7777777777` | Poor Performer | High debt, low returns |
| `8888888888` | SIP Investor | Regular SIP, moderate returns |
| `1313131313` | Balanced | Well diversified |
| `2020202020` | Beginner | Minimal investments |

### Test Commands
```bash
# Test with different user profiles
python simple_investment_cli.py
# Select user: 2222222222 (Large Portfolio)

# Test web interface
python run_web_app.py
# Open: http://localhost:5000

# Test interactive mode
python run_interactive.py
```

## 🔧 Development Workflow

### Adding New Features

1. **For new investment strategies:**
   - Edit `investment_agent/prompt.py`
   - Add logic in `investment_agent/agent.py`

2. **For new data sources:**
   - Create new tool in `investment_agent/tools/`
   - Add to sub-agent tool lists

3. **For new Angel One features:**
   - Update `angel_one_tool.py`
   - Add real API calls in `enhanced_angel_one_service.py`

### Testing Your Changes
```bash
# Quick test
python simple_investment_cli.py

# Full test with logs
python run_interactive.py

# Web interface test
python run_web_app.py
```

## 🐛 Common Issues & Solutions

### Issue: "Google API Key not found"
**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check content
cat .env | grep GOOGLE_API_KEY

# Fix: Add your API key
echo "GOOGLE_API_KEY=your_actual_key_here" >> .env
```

### Issue: "Angel One tool not working"
**Solution:**
```bash
# Test the tool directly
python -c "
from investment_agent.tools.angel_one_tool import AngelOneMarketTool
import asyncio
tool = AngelOneMarketTool()
print(asyncio.run(tool.run_async('market status')))
"
```

### Issue: "Import errors"
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (need 3.9+)
python --version
```

## 📁 Project Structure Deep Dive

```
investment-agent-standalone/
├── 📄 .env                          # Your API keys (EDIT THIS!)
├── 📄 .env.example                  # Template for API keys
├── 📄 requirements.txt              # Python dependencies
├── 📄 simple_investment_cli.py      # Main CLI app (START HERE!)
├── 📄 run_interactive.py            # Interactive mode
├── 📄 run_web_app.py               # Web interface
├── 📄 direct_data_investment_app.py # Direct data app
│
├── 📁 investment_agent/             # Core AI agent
│   ├── 📄 agent.py                 # Main coordinator agent
│   ├── 📄 prompt.py                # Agent instructions
│   ├── 📁 sub_agents/              # Specialized agents
│   │   ├── 📁 data_analyst/        # Market data analysis
│   │   ├── 📁 trading_analyst/     # Trading strategies  
│   │   ├── 📁 execution_analyst/   # Investment execution
│   │   └── 📁 risk_analyst/        # Risk assessment
│   └── 📁 tools/                   # External integrations
│       └── 📄 angel_one_tool.py    # Angel One API (IMPORTANT!)
│
├── 📁 services/                     # Backend services
│   └── 📄 enhanced_angel_one_service.py # Angel One service layer
│
├── 📁 fi-mcp-dev/                  # Fi Money test server
│   ├── 📄 main.go                  # Go server for test data
│   └── 📁 test_data_dir/           # User test profiles
│
└── 📁 Documentation/               # Guides and docs
    ├── 📄 README.md                # Main documentation
    ├── 📄 QUICK_START.md           # Quick setup guide
    ├── 📄 FI_MONEY_SETUP_GUIDE.md  # Fi Money integration
    ├── 📄 angel_one_data_flow.md   # Angel One data flow
    └── 📄 TEAM_HANDOVER_GUIDE.md   # This file!
```

## 🎯 Next Steps for Development

### Immediate Tasks (Week 1)
1. ✅ Set up your development environment
2. ✅ Test all three modes (CLI, interactive, web)
3. ✅ Understand Angel One integration
4. ✅ Test with different user profiles

### Short-term Goals (Week 2-3)
1. 🔄 Connect real Angel One APIs (if credentials available)
2. 🔄 Add more investment strategies
3. 🔄 Improve risk assessment logic
4. 🔄 Add more Indian market instruments

### Long-term Goals (Month 1+)
1. 🔄 Add portfolio tracking features
2. 🔄 Implement real-time alerts
3. 🔄 Add more sophisticated analysis
4. 🔄 Improve user interface

## 📞 Getting Help

### Code Understanding
- **Main entry point**: `simple_investment_cli.py`
- **Agent logic**: `investment_agent/agent.py`
- **Angel One integration**: `investment_agent/tools/angel_one_tool.py`
- **Test data**: `fi-mcp-dev/test_data_dir/`

### Documentation
- **Setup**: `QUICK_START.md`
- **Fi Money**: `FI_MONEY_SETUP_GUIDE.md`
- **Angel One**: `angel_one_data_flow.md`
- **Main docs**: `README.md`

### Testing Commands
```bash
# Quick test everything works
python simple_investment_cli.py

# Test specific components
python -c "from investment_agent.agent import InvestmentAgent; print('✅ Agent imports OK')"
python -c "from investment_agent.tools.angel_one_tool import AngelOneMarketTool; print('✅ Angel One tool OK')"
```

## 🎉 You're Ready to Continue!

The project is well-structured and ready for continued development. The Angel One integration is working with simulated data, and you can easily switch to real APIs when ready.

**Start with**: `python simple_investment_cli.py` and explore from there!

**Questions?** Check the documentation files or test the components individually.

Good luck with the development! 🚀📈