# Artha AI Backend

The backend service for Artha AI, a FastAPI-based application that provides intelligent financial analysis and investment recommendations through a multi-agent AI system.

## Overview

This backend application integrates with Fi Money's MCP (Model Context Protocol) to access real financial data and uses Google's advanced AI models to provide personalized investment advice. The system features a sophisticated multi-agent architecture for comprehensive financial analysis.

## Features

### Core Functionality
- **Real-time Financial Data**: Integration with Fi Money MCP for live portfolio data
- **Multi-Agent AI System**: SAndeep investment agents for comprehensive analysis
- **Investment Recommendations**: Personalized mutual fund and stock suggestions
- **Portfolio Analysis**: Net worth tracking and asset allocation insights
- **Credit Monitoring**: Credit score analysis and improvement recommendations
- **Demo Mode**: Instant hardcoded responses for demonstrations

### AI Agents
1. **Data Analyst Agent**: Market research and fundamental analysis
2. **Trading Analyst Agent**: Investment strategy and recommendations
3. **Execution Analyst Agent**: Broker selection and execution planning
4. **Risk Analyst Agent**: Portfolio risk assessment and diversification

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Google AI/ADK**: Advanced language models for financial analysis
- **Python 3.13**: Latest Python with async/await support
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server

## Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager
- Google AI API key

### Setup Steps

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Artha-Agent/backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Environment configuration**:
Create a `.env` file in the backend directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
PORT=8000
DEBUG=true
```

5. **Start the development server**:
```bash
python api_server.py
```

The server will start at `http://localhost:8000`

## API Documentation

### Core Endpoints

#### Financial Insights
```http
GET /api/financial-insights
```
Returns comprehensive portfolio analysis including net worth, asset breakdown, and investment performance.

**Response Example**:
```json
{
  "status": "success",
  "net_worth": {
    "total": 500000,
    "assets": {
      "mutual_funds": 250000,
      "stocks": 150000,
      "bank_accounts": 100000
    }
  },
  "insights": ["Portfolio diversification suggestions..."]
}
```

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

**Response Example**:
```json
{
  "status": "success",
  "recommendations": {
    "mutual_funds": [
      {
        "name": "HDFC Top 100 Fund",
        "allocation": 30,
        "amount": 15000,
        "expected_returns": "12-15%"
      }
    ],
    "stocks": [
      {
        "name": "TCS",
        "allocation": 20,
        "amount": 10000,
        "target_price": 4200
      }
    ]
  }
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

Demo responses include "*" indicators to clearly identify test data.

## Project Structure

```
backend/
├── api_server.py                    # Main FastAPI application
├── core/
│   ├── fi_mcp/                     # Fi Money MCP integration
│   │   ├── real_client.py          # Real Fi Money data client
│   │   └── demo_client.py          # Demo data client
│   ├── money_truth_engine.py       # Financial analysis engine
│   └── local_llm_processor.py      # LLM processing utilities
├── agents/                         # AI agents for different analyses
│   ├── enhanced_analyst.py         # Enhanced financial analyst
│   ├── enhanced_risk_advisor.py    # Risk assessment agent
│   └── stock_agents/               # Stock analysis agents
├── sandeep_investment_system/      # Multi-agent investment system
│   ├── investment_agent/           # Core investment agents
│   │   ├── agent.py               # Main investment agent
│   │   ├── sub_agents/            # Specialized sub-agents
│   │   └── tools/                 # Agent tools and utilities
│   ├── services/                   # External service integrations
│   │   ├── demat_broker_service.py # Broker integrations
│   │   └── enhanced_angel_one_service.py # Angel One API
│   ├── demo_responses.py           # Demo mode responses
│   ├── intelligent_responses.py    # Market data responses
│   └── sandeep_api_integration.py  # Main integration layer
├── config/
│   └── settings.py                 # Application configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# Database (if using)
DATABASE_URL=sqlite:///./artha.db

# External APIs
ANGEL_ONE_API_KEY=your_angel_one_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

### Application Settings

The application can be configured through `config/settings.py`:

```python
class Settings:
    app_name: str = "Artha AI Backend"
    debug: bool = True
    port: int = 8000
    google_api_key: str
    # ... other settings
```

## Development

### Running in Development Mode

```bash
# With auto-reload
python api_server.py

# Or using uvicorn directly
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Production Deployment

### Using Docker

```bash
# Build image
docker build -t artha-ai-backend .

# Run container
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key artha-ai-backend
```

### Using Render

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically triggers on git push

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export GOOGLE_API_KEY=your_api_key
export PORT=8000
export DEBUG=false

# Start production server
uvicorn api_server:app --host 0.0.0.0 --port $PORT --workers 4
```

## API Authentication

Currently, the API uses basic authentication. For production deployment, consider implementing:

- JWT token authentication
- API key management
- Rate limiting
- CORS configuration

## Monitoring and Logging

The application includes structured logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Financial data processed successfully")
```

Logs are output in JSON format for easy parsing by monitoring tools.

## Performance Considerations

- **Async Operations**: All I/O operations use async/await
- **Connection Pooling**: Database connections are pooled
- **Caching**: Market data is cached to reduce API calls
- **Response Compression**: Gzip compression for large responses

## Security

- **Input Validation**: All inputs validated using Pydantic models
- **Environment Variables**: Sensitive data stored in environment variables
- **CORS**: Configured for frontend domain only
- **Rate Limiting**: Implemented to prevent abuse

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and virtual environment is activated
2. **API Key Issues**: Verify Google AI API key is correctly set in environment variables
3. **Port Conflicts**: Change port in `.env` if 8000 is in use
4. **Module Not Found**: Ensure you're running from the backend directory

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

This provides detailed logging and error traces.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow PEP 8 conventions
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API logs for error details