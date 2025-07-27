# Artha AI - Personal Financial Assistant

Artha AI is a comprehensive personal finance management platform that leverages artificial intelligence to provide intelligent investment recommendations, portfolio analysis, and financial insights. Built specifically for Indian markets, it integrates with Fi Money's MCP protocol to deliver real-time financial data and personalized investment strategies.

## Features

### 🤖 Multi-Agent Investment System
- **SAndeep AI Agents**: Advanced 4-agent architecture for comprehensive investment analysis
- **Data Analyst Agent**: Market research and financial data processing
- **Trading Analyst Agent**: Investment strategy and stock/mutual fund recommendations
- **Execution Analyst Agent**: Broker selection and investment execution planning
- **Risk Analyst Agent**: Portfolio risk assessment and diversification strategies

### 💰 Fi Money Integration
- Real-time financial data via Model Context Protocol (MCP)
- Net worth tracking across multiple accounts
- Bank transaction analysis and categorization
- EPF balance monitoring
- Credit score and report integration

### 📊 Portfolio Management
- Comprehensive portfolio analysis with asset allocation breakdown
- Mutual fund performance tracking with XIRR calculations
- Investment goal-based recommendations
- Tax-efficient investment strategies (ELSS, PPF, 80C optimization)

### 💳 Credit Monitoring
- Real-time credit score tracking
- Credit report analysis and insights
- Credit improvement recommendations
- Bureau score monitoring across CIBIL, Experian, Equifax

### 🎯 Investment Recommendations
- Personalized mutual fund selections based on risk profile
- Blue-chip stock recommendations with detailed analysis
- Sector-wise investment allocation strategies
- SIP planning and goal-based investing

### 💡 Demo Mode
- Instant hardcoded responses for demonstrations
- Comprehensive demo data with "*" indicators
- Market research-based intelligent demo responses
- Perfect for showcasing capabilities without real account setup

## Technology Stack

### Backend
- **FastAPI**: High-performance API framework with automatic documentation
- **Google AI/ADK**: Advanced AI agents with Gemini 2.5 Flash integration
- **Python 3.13**: Latest Python with async/await support
- **SQLAlchemy**: Database ORM for financial data persistence
- **Pydantic**: Data validation and serialization
- **Fi Money MCP**: Real financial data integration protocol

### Frontend
- **Next.js 15**: React framework with app router and server components
- **TypeScript**: Type-safe development with enhanced developer experience
- **Tailwind CSS**: Utility-first CSS framework for responsive design
- **Recharts**: Powerful charting library for financial data visualization
- **Framer Motion**: Smooth animations and transitions
- **Redux Toolkit**: Predictable state management
- **Heroicons**: Beautiful SVG icons

### AI & Data Processing
- **Google Generative AI**: Advanced language models for financial analysis
- **Angel One API**: Real-time stock market data
- **Pandas & NumPy**: Data analysis and numerical computation
- **Yahoo Finance**: Market data and stock information

## Installation and Setup

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.13+
- Google AI API key

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/Artha-Agent.git
cd Artha-Agent/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_gemini_api_key
```

5. Start the development server:
```bash
python api_server.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Documentation

### Core Endpoints

#### Financial Insights
```http
GET /api/financial-insights
```
Returns comprehensive portfolio analysis including net worth, asset allocation, and investment breakdown.

#### Investment Recommendations
```http
POST /api/ai-investment-recommendations
Content-Type: application/json

{
  "investment_amount": 50000,
  "risk_tolerance": "moderate",
  "investment_goal": "wealth_creation",
  "time_horizon": "long_term"
}
```

#### Interactive Chat
```http
POST /api/ai-investment-recommendations/chat
Content-Type: application/json

{
  "query": "What are the best mutual funds for 2025?",
  "mode": "comprehensive"
}
```

#### Credit Analysis
```http
GET /api/credit-analysis
```
Returns detailed credit score analysis and improvement recommendations.

### Demo Mode
Add `?demo=true` to any endpoint for instant demo responses:
```http
GET /api/ai-investment-recommendations?demo=true
```

Demo responses include "*" indicators and are based on real market research data from July 2025.

## Project Structure

```
Artha-Agent/
├── backend/
│   ├── api_server.py              # Main FastAPI application
│   ├── core/
│   │   ├── fi_mcp/                # Fi Money MCP integration
│   │   └── money_truth_engine.py  # Financial analysis engine
│   ├── agents/                    # AI agents for analysis
│   ├── sandeep_investment_system/ # Multi-agent investment system
│   │   ├── investment_agent/      # Core investment agents
│   │   ├── services/              # Broker and market services
│   │   ├── demo_responses.py      # Demo mode responses
│   │   └── intelligent_responses.py # Market data responses
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js app router
│   │   ├── components/            # React components
│   │   ├── contexts/              # React contexts
│   │   └── services/              # API services
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Key Features Deep Dive

### SAndeep Multi-Agent Investment System

The investment system uses a sophisticated 4-agent architecture:

1. **Data Analyst Agent**: Processes market data, analyzes trends, and provides fundamental analysis
2. **Trading Analyst Agent**: Generates specific investment recommendations with risk-return analysis
3. **Execution Analyst Agent**: Plans investment execution across multiple brokers with cost optimization
4. **Risk Analyst Agent**: Assesses portfolio risk, suggests diversification, and monitors exposure

### Fi Money MCP Integration

Real-time financial data integration provides:
- Live net worth calculations across all accounts
- Transaction categorization and spending analysis
- Investment performance tracking with XIRR
- Credit monitoring and score updates
- EPF balance and employer contribution tracking

### Indian Market Focus

Built specifically for Indian investors:
- Integration with major Indian brokers (Groww, Zerodha, Angel One, Upstox)
- Indian tax optimization (80C, ELSS, PPF recommendations)
- INR currency handling and Indian market hours
- Mutual fund analysis with Indian AMCs
- BSE/NSE stock recommendations

## Deployment

### Using Render (Recommended)

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service from your forked repo
4. Set environment variables in Render dashboard
5. Deploy automatically triggers on git push

### Manual Deployment

#### Backend Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export GOOGLE_API_KEY=your_api_key
export PORT=8000

# Start production server
uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

#### Frontend Deployment
```bash
# Build the application
npm run build

# Start production server
npm start
```

## Configuration

### Environment Variables

#### Backend (.env)
```
GOOGLE_API_KEY=your_gemini_api_key
PORT=8000
DEBUG=false
```

#### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEMO_MODE=false
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Use meaningful commit messages
- Add tests for new features
- Update documentation for API changes
- Ensure responsive design for mobile devices

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Performance Optimization

- **Backend**: Async/await for concurrent operations, Redis caching for market data
- **Frontend**: Next.js optimization, image optimization, lazy loading
- **Database**: Efficient queries with SQLAlchemy, connection pooling
- **API**: Response compression, pagination for large datasets

## Security

- **API Security**: Rate limiting, input validation, CORS configuration
- **Data Protection**: Encrypted sensitive data, secure token handling
- **Authentication**: OAuth integration, session management
- **Compliance**: Financial data handling best practices

## Monitoring and Logging

- **Application Logs**: Structured logging with different levels
- **Performance Monitoring**: Response time tracking, error rate monitoring
- **Health Checks**: Endpoint availability monitoring
- **Analytics**: User interaction tracking (privacy-compliant)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@artha-ai.com or open an issue on GitHub.

## Acknowledgments

- **Fi Money** for MCP protocol and real financial data
- **Google AI** for advanced language models
- **SAndeep Team** for the multi-agent investment architecture
- **Open Source Community** for the excellent tools and libraries

---

**Artha AI** - Making intelligent financial decisions accessible to everyone. 🚀