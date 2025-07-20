# Artha AI Backend

A sophisticated multi-agent financial advisory system powered by Google's Gemini AI. The system features three specialized agents that collaborate to provide comprehensive financial advice.

## 🤖 Agent Architecture

### 1. Data Analyst Agent
- **Specialization**: Quantitative financial data analysis
- **Capabilities**: Credit score analysis, portfolio performance evaluation, asset allocation assessment, financial health scoring
- **Data Sources**: Credit reports, mutual fund analytics, EPF details, transaction history

### 2. Research Agent  
- **Specialization**: Market research and investment strategies
- **Capabilities**: Market trend analysis, investment opportunities identification, portfolio optimization strategies
- **Focus**: Strategic recommendations based on market conditions and user profile

### 3. Risk Management Agent
- **Specialization**: Financial risk assessment and mitigation
- **Capabilities**: Portfolio risk analysis, credit risk evaluation, market risk assessment, protection planning
- **Priority**: User financial safety and long-term stability

## 🏗️ System Architecture

```
User Query → Agent Coordinator → Individual Agents → Collaboration → Final Summary
```

1. **User Query Processing**: Coordinator receives and distributes query to all agents
2. **Parallel Analysis**: Each agent analyzes the query from their expertise perspective
3. **Agent Collaboration**: Agents share insights and collaborate on recommendations
4. **Final Summary Generation**: Coordinator creates comprehensive response in structured format

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation & Setup

1. **Clone and navigate to backend directory**
   ```bash
   cd Artha-Agent/backend
   ```

2. **Run the startup script**
   ```bash
   ./start.sh
   ```
   
   This script will:
   - Create a virtual environment
   - Install all dependencies
   - Check for configuration
   - Start the FastAPI server

3. **Configure environment variables**
   Create a `.env` file with your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Verify installation**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## 📊 Data Sources

The system uses sample financial data from the `mcp-docs/sample_responses/` directory:

- `fetch_credit_report.json` - Credit report data with scores and account details
- `fetch_net_worth.json` - Portfolio holdings, mutual funds, and asset allocation
- `fetch_epf_details.json` - EPF balances and contribution history
- `fetch_mf_transactions.json` - Mutual fund transaction history

## 🔌 API Endpoints

### Core Endpoints

- `POST /api/chat` - Main chat interface for multi-agent responses
- `GET /api/health` - System health and agent status
- `GET /api/financial-data/{user_id}` - User's complete financial profile
- `GET /api/market-data` - Market insights and analysis

### Session Management

- `POST /api/agent-discussion` - Get detailed agent collaboration for a session
- `GET /api/sessions` - List active chat sessions
- `DELETE /api/sessions/{session_id}` - Clear specific session

### System Information

- `GET /api/coordinator-status` - Coordinator and agent status
- `GET /api/data-summary` - Available data summary

## 📝 Example Usage

### Chat Request
```json
{
  "message": "I want to invest 2000 rupees in OLAELEC stock. Is it a good idea?",
  "user_id": "demo_user",
  "session_id": "optional_session_id"
}
```

### Chat Response
```json
{
  "session_id": "generated_session_id",
  "user_query": "I want to invest 2000 rupees in OLAELEC stock...",
  "final_summary": "Of course. Here is a simple final summary that brings together the findings from all our specialized agents.\n\nFinal Summary: A High-Risk Plan for OLAELEC\n\nAfter a step-by-step analysis using our team of financial subagents...",
  "agent_insights": {
    "analyst": {
      "agent_name": "Data Analyst",
      "key_findings": ["Current portfolio analysis...", "Credit score: 746"],
      "confidence": 0.85
    },
    "research": {
      "agent_name": "Research Agent", 
      "key_findings": ["Market trends analysis...", "Investment strategy..."],
      "confidence": 0.80
    },
    "risk_management": {
      "agent_name": "Risk Management Agent",
      "key_findings": ["High risk warnings...", "Risk mitigation..."],
      "confidence": 0.90
    }
  },
  "overall_confidence": 0.85,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🔧 Configuration

### Environment Variables
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
APP_PORT=8000
DEBUG=True
MCP_DATA_PATH=../mcp-docs/sample_responses/
```

### Gemini AI Configuration
The system uses `gemini-pro` model with optimized settings:
- Temperature: 0.7 (balanced creativity/consistency)  
- Top-p: 0.8 (focused response quality)
- Max tokens: 2048 (comprehensive responses)

## 🛠️ Development

### Project Structure
```
backend/
├── agents/                     # Individual agent implementations
│   ├── analyst_agent/
│   │   └── analyst.py         # Data analysis specialist
│   ├── research_agent/
│   │   └── research.py        # Market research specialist  
│   ├── risk_management_agent/
│   │   └── risk_manager.py    # Risk assessment specialist
│   └── base_agent.py          # Common agent functionality
├── coordination/               # Agent collaboration system
│   └── agent_coordinator.py   # Orchestrates agent interactions
├── utils/                     # Utilities and helpers
│   ├── data_loader.py         # Financial data management
│   └── gemini_client.py       # Gemini AI integration
├── main_fastapi.py            # FastAPI application entry point
├── requirements.txt           # Python dependencies
└── .env                       # Environment configuration
```

### Adding New Agents
1. Create new agent class inheriting from `BaseAgent`
2. Implement required methods: `analyze_query()` and `generate_agent_discussion_message()`
3. Add agent to coordinator initialization
4. Update API responses to include new agent insights

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest tests/
```

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main_fastapi.py"]
```

### Production Configuration
- Set `DEBUG=False` in environment
- Use proper CORS origins configuration
- Implement proper logging and monitoring
- Use production ASGI server (uvicorn with workers)

## 🔐 Security Considerations

- API keys stored in environment variables only
- No sensitive data logged
- Input validation on all endpoints
- Rate limiting recommended for production
- HTTPS required for production deployment

## 🤝 Integration with Flutter App

The backend is designed to work seamlessly with the Flutter frontend:

1. **API Compatibility**: All endpoints return JSON in expected format
2. **Session Management**: Maintains conversation context across requests
3. **Real-time Feel**: Fast response times with efficient agent coordination
4. **Error Handling**: Graceful fallbacks and informative error messages

## 📋 Monitoring & Logging

The system includes comprehensive logging:
- Agent analysis performance
- Response generation times  
- Error tracking and debugging
- Session management events

Monitor via logs or integrate with observability platforms.

## 🔄 Future Enhancements

- Real-time market data integration
- Machine learning model integration for better insights
- Advanced portfolio optimization algorithms
- Integration with actual financial data APIs
- Multi-language support
- Voice interaction capabilities

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review logs for error details
3. Ensure Gemini API key is valid and has quota
4. Verify sample data files are accessible

---

**Note**: This system uses sample financial data for demonstration. In production, integrate with real financial data providers and ensure compliance with financial regulations.