# 🏦 Artha Investment Agent

An intelligent AI-powered investment advisor specifically designed for the Indian financial markets. Built for the GCP hackathon with Fi Money integration and Firebase backend support.

## 🏗️ Architecture Options

### 🌐 Firebase Backend (Recommended for Production)
Complete serverless backend with Next.js frontend integration:
- **Firebase Cloud Functions**: Scalable API backend
- **Fi Money Integration**: Real user financial data
- **Angel One API**: Investment execution
- **Next.js Frontend**: Modern web interface

### 💻 Standalone Local (Development & Testing)
Run the investment agent locally for development and testing.

## 🚀 Invest Now Feature

After receiving personalized investment recommendations, users can immediately execute their investments through the **"Invest Now"** button in the terminal.

### 🏦 Supported Brokers
- **Angel One** - Zero brokerage on delivery trades
- **Zerodha** - Kite platform with comprehensive tools  
- **Groww** - Beginner-friendly interface
- **Upstox** - Professional trading platform
- **IIFL Securities** - Full-service broker
- **Paytm Money** - Digital-first platform

### 🔄 How It Works
1. **Get Recommendations** - AI analyzes your profile and suggests investments
2. **Click "Invest Now"** - Terminal shows broker selection interface
3. **Choose Your Broker** - Select from 6 major Indian brokers
4. **Login & Execute** - System opens your broker's platform in browser
5. **Complete Investment** - Follow guided steps to execute trades

### 🧪 Test the Feature
```bash
# Test broker selection interface
python test_demat_broker.py

# Full CLI with invest now feature
python simple_investment_cli.py
```

## 🚀 Quick Start

### Option 1: One-Click Setup (Recommended)
```bash
# Clone and setup everything automatically
git clone <repository-url>
cd investment-agent-standalone
python quick_setup.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run the agent
python simple_investment_cli.py
```

### Firebase Backend Deployment
```bash
# Deploy to Firebase (for production/hackathon)
python deploy.py
```

### Local Development
```bash
# One-Click Setup (Windows)
start.bat

# Or automated setup
python setup.py

# Or manual setup
pip install -r requirements.txt
python run_with_ai_studio.py
```

## 📋 Requirements

- Python 3.9 or higher
- Internet connection
- **Choose ONE of the following:**
  - **Google AI Studio API Key** (Free tier available) - Recommended for beginners
  - **Google Cloud Project** with Vertex AI enabled - For production use

## 🔧 Setup Options

### Google AI Studio (Recommended for Local Development)
1. Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Run `python setup.py` and choose option 1
3. Run `python run_with_ai_studio.py`

### Google Cloud Vertex AI (For Production/Enterprise)
1. Set up a Google Cloud Project
2. Enable Vertex AI API
3. Authenticate: `gcloud auth application-default login`
4. Run `python setup.py` and choose option 2
5. Run `python run_with_vertex_ai.py`

For detailed Vertex AI setup instructions, see [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md).

## 🎯 What Can This Agent Do?

### 📈 Investment Strategies
- SIP (Systematic Investment Plan) recommendations
- Asset allocation strategies for Indian markets
- Tax-saving investment options (ELSS, PPF, etc.)
- Portfolio diversification guidance

### 🔍 Market Analysis
- Indian stock market insights
- Mutual fund recommendations
- Risk assessment for different investment products
- Market timing and entry/exit strategies

### 💰 Financial Planning
- Goal-based investment planning
- Retirement planning strategies
- Emergency fund recommendations
- Tax optimization strategies

### ⚠️ Risk Management
- Risk profiling based on age, income, and goals
- Risk mitigation strategies
- Portfolio rebalancing recommendations
- Market volatility analysis

## 🎮 Available Scripts

- `run_with_ai_studio.py` - Run with Google AI Studio (free tier)
- `run_with_vertex_ai.py` - Run with Google Cloud Vertex AI
- `run_interactive.py` - Interactive mode with custom configuration
- `run_local_test.py` - Local testing and development
- `setup.py` - Automated setup script
- `start.bat` - One-click Windows setup

## 💡 Example Questions to Ask

- "I'm 25 years old with ₹50,000 monthly income. How should I start investing?"
- "What are the best tax-saving investment options for this financial year?"
- "Should I invest in large-cap or small-cap mutual funds?"
- "How should I diversify my portfolio across different asset classes?"
- "What are the risks of investing in sectoral funds?"
- "When should I start SIP and how much should I invest?"

## 🏗️ Project Structure

```
investment-agent-standalone/
├── functions/                  # Firebase Cloud Functions
│   ├── main.py                # API endpoints
│   ├── requirements.txt       # Firebase dependencies
│   ├── .env.example          # Environment template
│   └── services/             # Service modules
│       ├── fi_money_service.py
│       ├── angel_one_service.py
│       └── investment_agent_service.py
├── investment_agent/           # Main agent code
│   ├── agent.py               # Core agent logic
│   ├── prompt.py              # Main coordinator prompt
│   └── sub_agents/            # Specialized sub-agents
│       ├── data_analyst/      # Market data analysis
│       ├── trading_analyst/   # Trading strategies
│       ├── execution_analyst/ # Investment execution
│       └── risk_analyst/      # Risk assessment
├── firebase.json              # Firebase configuration
├── deploy.py                  # Firebase deployment script
├── test_firebase.py           # Firebase testing script
├── setup.py                   # Automated setup script
├── run_with_ai_studio.py      # Easy runner (recommended)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── README_FIREBASE.md         # Firebase documentation
```

## 📚 Documentation

### For New Team Members
- **[Team Handover Guide](TEAM_HANDOVER_GUIDE.md)**: Complete project handover for new developers
- **[Developer Setup Checklist](DEVELOPER_SETUP_CHECKLIST.md)**: Quick setup checklist

### Setup & Configuration
- **[Quick Start Guide](QUICK_START.md)**: Get started in minutes
- **[Fi Money Setup](FI_MONEY_SETUP_GUIDE.md)**: Fi Money integration guide
- **[Angel One Data Flow](angel_one_data_flow.md)**: How Angel One API integration works

## 🔧 Troubleshooting

### "Module not found" errors
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### "API key not found" errors
1. Make sure you have a `.env` file in the project directory
2. Verify your API key is correctly added to the `.env` file
3. Check that the API key is valid and active

### Agent not responding
1. Check your internet connection
2. Verify your API key has sufficient quota
3. Try running the test script: `python run_local_test.py`

## 🌟 Features

- **🤖 AI-Powered Recommendations**: Personalized investment advice using Google's Gemini AI
- **📊 Real-time Market Data**: Live prices and market analysis via Angel One APIs
- **💰 Fi Money Integration**: Analyzes user's actual financial data from Fi Money accounts
- **🎯 Multi-Asset Support**: Stocks, ETFs, Mutual Funds, and more
- **📱 Multiple Interfaces**: CLI, Web App, and Interactive modes
- **🔒 Secure & Private**: No direct account access, data stays local
- **🚀 Invest Now Feature**: Seamless transition from recommendations to execution
- **🏦 Multi-Broker Support**: Angel One, Zerodha, Groww, Upstox, and more
- **Indian Market Focus**: Specifically designed for Indian investment products
- **Multi-Agent Architecture**: Specialized agents for different aspects of investment
- **Real-time Analysis**: Up-to-date market insights and recommendations
- **📈 Risk Assessment**: Comprehensive risk analysis for all recommendations
- **Tax Optimization**: Indian tax law compliant investment strategies
- **💡 Educational**: Detailed explanations and investment guidance
- **Goal-based Planning**: Customized advice based on your financial goals

## 📞 Support

If you encounter any issues:
1. Run the automated setup: `python setup.py`
2. Check the troubleshooting section above
3. Verify all prerequisites are met
4. Ensure your API key is valid and has quota
5. Try the test script to isolate issues

## 🔒 Privacy & Security

- Your conversations are processed by Google's AI services
- No financial data is stored permanently
- API keys should be kept secure and not shared
- This is for educational and advisory purposes only

## ⚖️ Disclaimer

This AI agent provides educational and informational content only. It is not a substitute for professional financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

---

**Happy Investing! 🚀📈**