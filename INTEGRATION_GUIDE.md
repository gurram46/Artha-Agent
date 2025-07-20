# Artha AI Complete Integration Guide

A comprehensive guide to run the complete Artha AI system with 3 collaborative agents and Flutter frontend.

## 🏗️ System Overview

### Architecture
```
Flutter App (Frontend) ↔ FastAPI Backend ↔ 3 Gemini AI Agents ↔ Sample Financial Data
```

### Agents
1. **Data Analyst Agent** - Analyzes financial data, credit scores, portfolio performance
2. **Research Agent** - Provides market insights and investment strategies  
3. **Risk Management Agent** - Identifies risks and provides protective recommendations

## 🚀 Quick Start (5 Minutes)

### Step 1: Backend Setup
```bash
# Navigate to backend directory
cd Artha-Agent/backend

# Make scripts executable (if needed)
chmod +x start.sh test_system.py

# Start the backend (this will install dependencies automatically)
./start.sh
```

### Step 2: Configure Gemini API Key
1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create/update `.env` file in the backend directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
3. Restart the backend: `Ctrl+C` then `./start.sh`

### Step 3: Test Backend
```bash
# In a new terminal, test the system
cd Artha-Agent/backend
python test_system.py
```

### Step 4: Start Flutter App
```bash
# Navigate to Flutter app directory
cd Artha-Agent/artha_ai_app

# Get dependencies
flutter pub get

# Run the app
flutter run
```

### Step 5: Test Complete System
1. Open the Flutter app
2. Navigate to the Chat section
3. Try a query like: "I want to invest 2000 rupees in OLAELEC stock. Is it a good idea?"
4. You should get a comprehensive response from all 3 agents

## 📱 Expected Output Example

When you ask: *"I want to invest 2000 rupees in OLAELEC stock. Is it a good idea?"*

You'll get a response like:

> **Of course. Here is a simple final summary that brings together the findings from all our specialized agents.**
> 
> **Final Summary: A High-Risk Plan for OLAELEC**
> 
> After a step-by-step analysis using our team of financial subagents, here is the complete picture for your plan to invest 2,000 rupees in OLAELEC.
> 
> **1. What Our Data Analyst Found (The Asset):**
> Based on your current portfolio analysis, your credit score is 746 which is excellent. Your current portfolio shows good diversification across mutual funds with a total value of ₹84,613. However, adding individual stock exposure would increase concentration risk.
> Conclusion: Your financial foundation is strong enough to consider speculative investments.
> 
> **2. What Our Research Agent Found (The Strategy):**
> OLAELEC operates in the electric vehicle space which shows long-term growth potential. However, the stock has been highly volatile. A systematic approach would be to invest in tranches rather than a lump sum. Consider this as a small speculative portion (5-10%) of your overall portfolio.
> 
> **3. What Our Risk Management Agent Warned (The Dangers):**
> This investment carries VERY HIGH risk. Individual stocks can lose 50-90% of their value. Never invest more than you can afford to lose completely. Ensure you have adequate emergency funds and continue your existing SIP investments before taking speculative positions.
> 
> This structured process provides a high-risk speculative plan. It balances growth opportunity with strong risk awareness and requires strict discipline and position sizing.

## 🔧 Configuration Options

### Backend Configuration (.env)
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
APP_PORT=8000
DEBUG=True
MCP_DATA_PATH=../mcp-docs/sample_responses/
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Flutter Configuration
Update `lib/services/artha_api_service.dart` if needed:
```dart
static const String baseUrl = 'http://localhost:8000';
// For Android emulator: 'http://10.0.2.2:8000'
// For iOS simulator: 'http://localhost:8000'  
// For physical device: 'http://YOUR_IP:8000'
```

## 🧪 Testing Different Scenarios

Try these queries to test different agent responses:

### Portfolio Analysis
- "How is my portfolio performing?"
- "Should I rebalance my investments?"
- "What are my best and worst performing funds?"

### Risk Assessment  
- "What are the risks in my current portfolio?"
- "Is my investment strategy too aggressive?"
- "How much emergency fund should I maintain?"

### Investment Planning
- "Should I increase my SIP amount?"
- "What new investments should I consider?"
- "How should I invest my bonus amount?"

### Specific Stock Analysis
- "Should I invest in HDFC Bank stock?"
- "Is it a good time to invest in tech stocks?"
- "Analyze the risk of investing in cryptocurrency"

## 🛠️ Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check if port is available
lsof -i :8000

# Kill existing process if needed
pkill -f "python.*main_fastapi"
```

#### 2. Gemini API Errors
- Verify API key is correct in `.env`
- Check API quota at [Google AI Studio](https://makersuite.google.com/)
- Ensure internet connection is stable

#### 3. Flutter Connection Issues
- Check `artha_api_service.dart` base URL
- For Android emulator, use `http://10.0.2.2:8000`
- For physical device, use your computer's IP address

#### 4. Sample Data Not Found
```bash
# Verify sample data exists
ls -la ../mcp-docs/sample_responses/

# Should contain:
# - fetch_credit_report.json
# - fetch_net_worth.json  
# - fetch_epf_details.json
# - fetch_mf_transactions.json
```

### Debug Mode

#### Backend Debugging
1. Set `DEBUG=True` in `.env`
2. Check logs in terminal where backend is running
3. Visit `http://localhost:8000/docs` for API documentation

#### Flutter Debugging
1. Run with verbose logs: `flutter run -v`
2. Check debug console for API call errors
3. Use Flutter Inspector for UI debugging

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/chat` - Main chat interface
- `GET /api/financial-data/{user_id}` - Financial data
- `GET /api/market-data` - Market insights

### Testing Endpoints
- `GET /api/coordinator-status` - Agent status
- `GET /api/data-summary` - Data availability
- `POST /api/agent-discussion` - Agent collaboration details

## 🚀 Production Deployment

### Backend Deployment
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn main_fastapi:app --host 0.0.0.0 --port 8000 --workers 4
```

### Flutter Deployment
```bash
# Build for web
flutter build web

# Build for mobile
flutter build apk  # Android
flutter build ios  # iOS
```

### Environment Variables for Production
```env
GEMINI_API_KEY=your_production_api_key
DEBUG=False
APP_PORT=8000
CORS_ORIGINS=["https://yourdomain.com"]
```

## 🔄 System Flow

1. **User Input**: User types financial query in Flutter app
2. **API Call**: Flutter sends POST request to `/api/chat`
3. **Agent Coordination**: Backend coordinator distributes query to all 3 agents
4. **Parallel Analysis**: Each agent analyzes with their specialization
5. **Collaboration**: Agents share insights and collaborate
6. **Summary Generation**: Coordinator creates comprehensive final response
7. **Response Delivery**: Structured response sent back to Flutter app
8. **UI Display**: Flutter displays the comprehensive advice

## 📋 Next Steps

After successful setup:

1. **Customize Agents**: Modify agent prompts in respective files
2. **Add Real Data**: Integrate with actual financial data APIs
3. **Enhance UI**: Improve Flutter interface based on user feedback
4. **Add Features**: Implement voice input, charts, notifications
5. **Deploy**: Set up production deployment with proper security

## 🤝 Support

If you encounter issues:

1. **Check Logs**: Backend terminal and Flutter debug console
2. **Test Endpoints**: Use the test script and API docs
3. **Verify Configuration**: Ensure all environment variables are set
4. **Sample Data**: Confirm sample data files are accessible
5. **Network**: Check firewall and network connectivity

## 📈 Performance Tips

- **Backend**: Use caching for repeated queries
- **Flutter**: Implement pagination for long conversations
- **API**: Add request/response compression
- **Database**: Consider Redis for session storage in production

---

🎉 **Congratulations!** You now have a fully functional multi-agent financial advisory system powered by AI. The system provides comprehensive, collaborative financial advice through an intuitive chat interface.