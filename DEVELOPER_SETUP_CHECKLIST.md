# 🔧 Developer Setup Checklist

Use this checklist to ensure your development environment is properly configured.

## ✅ Pre-Setup Checklist

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Git installed and configured
- [ ] Text editor/IDE ready (VS Code recommended)
- [ ] Internet connection available

## ✅ Project Setup Checklist

### 1. Environment Configuration
- [ ] Project cloned/downloaded to local machine
- [ ] Navigate to project directory: `cd investment-agent-standalone`
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`: `copy .env.example .env`

### 2. API Keys Configuration
- [ ] **Google AI API Key** obtained from [Google AI Studio](https://aistudio.google.com/app/apikey)
- [ ] Google AI API Key added to `.env` file
- [ ] Flask secret key generated and added to `.env`
- [ ] Angel One credentials added (optional, uses simulated data if not provided)

### 3. Basic Testing
- [ ] CLI version works: `python simple_investment_cli.py`
- [ ] Interactive version works: `python run_interactive.py`
- [ ] Web version works: `python run_web_app.py`
- [ ] Angel One tool test passes:
```bash
python -c "
from investment_agent.tools.angel_one_tool import AngelOneMarketTool
import asyncio
tool = AngelOneMarketTool()
result = asyncio.run(tool.run_async('Get market status'))
print('✅ Angel One tool working' if 'market_status' in result else '❌ Angel One tool failed')
"
```

### 4. Component Testing
- [ ] Investment Agent imports: `python -c "from investment_agent.agent import InvestmentAgent; print('✅ Agent OK')"`
- [ ] Sub-agents import: `python -c "from investment_agent.sub_agents.data_analyst.agent import data_analyst_agent; print('✅ Sub-agents OK')"`
- [ ] Tools import: `python -c "from investment_agent.tools.angel_one_tool import AngelOneMarketTool; print('✅ Tools OK')"`

### 5. Fi Money Integration (Optional)
- [ ] Go installed (for Fi Money MCP server)
- [ ] Fi Money MCP server runs: `cd fi-mcp-dev && go run main.go`
- [ ] Test data accessible at `http://localhost:8080`

## 🔑 Required API Keys

### Google AI API Key (Required)
```env
GOOGLE_API_KEY=your_google_ai_api_key_here
```
**Get it from**: https://aistudio.google.com/app/apikey

### Angel One API (Optional - Uses Simulated Data)
```env
ANGEL_ONE_API_KEY=your_angel_one_api_key_here
ANGEL_ONE_CLIENT_ID=your_angel_one_client_id_here
ANGEL_ONE_PASSWORD=your_angel_one_password_here
ANGEL_ONE_TOTP_SECRET=your_angel_one_totp_secret_here
```
**Get it from**: Angel One Developer Portal (requires account)

### Flask Configuration
```env
FLASK_SECRET_KEY=your_flask_secret_key_here
FLASK_ENV=development
```
**Generate secret key**:
```python
import secrets
print(secrets.token_hex(32))
```

## 🧪 Test Scenarios

### Test User Profiles (Fi Money)
Try these phone numbers in the CLI:
- `2222222222` - Large portfolio (9 mutual funds)
- `3333333333` - Small portfolio (1 mutual fund)  
- `8888888888` - SIP investor
- `1313131313` - Balanced portfolio
- `2020202020` - Beginner investor

### Test Questions
Try asking the agent:
```
"I want to invest ₹50,000 in Nifty ETFs. Is this a good time?"
"What are the best tax-saving investment options?"
"Should I invest in large-cap or mid-cap funds?"
"How should I diversify my portfolio?"
```

## 🐛 Troubleshooting

### Common Issues

**"Google API Key not found"**
- Check `.env` file exists: `ls .env` (Linux/Mac) or `dir .env` (Windows)
- Check key is properly set: `cat .env | grep GOOGLE_API_KEY`
- Ensure no extra spaces or quotes around the key

**"Module not found" errors**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.9+)
- Try using virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**"Angel One tool not responding"**
- This is normal - it uses simulated data by default
- Check tool works: Run the Angel One tool test from checklist above
- Real API integration requires Angel One developer account

**"Fi Money server not starting"**
- Ensure Go is installed: `go version`
- Navigate to correct directory: `cd fi-mcp-dev`
- Check port 8080 is available: `netstat -an | grep 8080`

## 📁 Key Files to Understand

| File | Purpose | When to Edit |
|------|---------|--------------|
| `.env` | API keys and configuration | First setup, adding new keys |
| `simple_investment_cli.py` | Main CLI application | Testing, understanding flow |
| `investment_agent/agent.py` | Core agent logic | Adding new features |
| `investment_agent/tools/angel_one_tool.py` | Angel One integration | Market data customization |
| `investment_agent/prompt.py` | Agent instructions | Changing behavior |
| `requirements.txt` | Python dependencies | Adding new libraries |

## 🚀 Ready to Start!

Once all checkboxes are ✅, you're ready to start development!

**First command to run**: `python simple_investment_cli.py`

**Next steps**: Read `TEAM_HANDOVER_GUIDE.md` for detailed project understanding.