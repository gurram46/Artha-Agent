# AGENTS.md - Artha AI Development Guide

## Dev Environment Tips
- Use `cd backend && python api_server.py` to start the backend server on port 8000
- Use `cd frontend && npm run dev` to start the Next.js frontend development server on port 3000
- Run `pip install -r requirements.txt` in the backend directory to install Python dependencies
- Run `npm install` in the frontend directory to install Node.js dependencies
- Use `python -m pytest` in the backend directory to run Python tests
- Check the `.env` file in the backend directory for configuration - ensure database and API keys are properly set
- Use `npm run build` in the frontend directory to create production build
- PostgreSQL database runs on port 5433 (non-standard port to avoid conflicts)

## Testing Instructions
- Backend tests: Run `python -m pytest` from the backend directory
- Frontend tests: Run `npm test` from the frontend directory
- Integration tests: Start both backend and frontend servers, then test API endpoints
- Run `python test_fi_import.py` to diagnose Fi Money MCP client import issues
- Run `python test_cache_system.py` to test the secure cache system
- Run `python test_chat_system.py` to test the AI chat functionality
- Check `backend.log` for backend server logs and debugging information
- Use `curl http://localhost:8000/api/fi-auth/status` to test Fi Money authentication endpoints
- Test financial data endpoints with `curl http://localhost:8000/api/financial-data?demo=true` for demo mode
- Ensure all tests pass before committing changes

## PR Instructions
- Title format: [backend/frontend] <Feature/Fix Description>
- Always run backend tests with `python -m pytest` before committing
- Always run frontend tests with `npm test` before committing
- Check that both servers start without errors
- Verify that the Fi Money authentication flow works (or falls back to demo mode)
- Update documentation if adding new API endpoints or features

## Project Context

### What is Artha AI?
Artha AI is a comprehensive financial advisory application that integrates with Fi Money's MCP (Model Context Protocol) to provide real-time financial data analysis, investment recommendations, and personalized financial insights.

### Architecture Overview
- **Backend**: Python FastAPI server with PostgreSQL database
- **Frontend**: Next.js React application with TypeScript
- **Integration**: Fi Money MCP client for real financial data
- **AI**: Google Gemini integration for financial analysis and recommendations
- **Cache**: Secure 24-hour cache system for persistent data storage

### Key Features
1. **Fi Money Integration**: Real-time financial data from Fi Money MCP
2. **AI-Powered Analysis**: Multi-agent system for investment recommendations
3. **Secure Authentication**: Web-based Fi Money authentication flow
4. **Demo Mode**: Fallback system with sample data when real data unavailable
5. **Real-time Chat**: Streaming AI responses for financial queries
6. **Portfolio Analysis**: Net worth, credit reports, and transaction history
7. **Investment Recommendations**: Personalized investment advice using AI agents

### Current Status & Recent Fixes

#### ✅ Recently Resolved Issues:
1. **Fi Money Authentication Timeouts**: Fixed frontend polling timeouts and backend API timeouts
2. **Demo Mode Configuration**: Enabled fallback to demo data when Fi Money MCP unavailable
3. **Timeout Configurations**: Extended authentication polling from 3 minutes to 5 minutes
4. **Error Handling**: Improved user feedback for authentication failures

#### 🔧 Current State:
- Backend server is functional and responding correctly
- Fi Money authentication endpoints are working
- Demo mode is properly configured as fallback
- Frontend timeout issues have been resolved
- Both real Fi Money data and demo data flows are operational

### Common Issues & Solutions

#### Fi Money MCP Issues:
- **Problem**: `FI_MONEY_AVAILABLE = False` due to import errors
- **Solution**: System automatically falls back to demo mode
- **Config**: Set `ENABLE_DEMO_MODE=true` in `.env` file

#### Authentication Timeouts:
- **Problem**: Frontend timing out during Fi Money authentication
- **Solution**: Extended polling duration to 5 minutes with 3-second intervals
- **Files**: `FiMoneyWebAuth.tsx`, `mcpDataService.ts`

#### Database Connection:
- **Problem**: PostgreSQL connection issues
- **Solution**: Ensure PostgreSQL is running on port 5433
- **Setup**: Run `python setup_postgresql.py` to initialize database

### Development Workflow
1. Start PostgreSQL database (port 5433)
2. Start backend server: `cd backend && python api_server.py`
3. Start frontend server: `cd frontend && npm run dev`
4. Test Fi Money authentication or use demo mode
5. Verify all endpoints are responding correctly
6. Run tests before committing changes

### Key Files to Monitor
- `backend/api_server.py`: Main backend server
- `backend/.env`: Configuration file
- `backend/backend.log`: Server logs
- `frontend/src/components/FiMoneyWebAuth.tsx`: Authentication component
- `frontend/src/services/mcpDataService.ts`: API service layer
- `backend/core/fi_mcp/production_client.py`: Fi Money MCP client

### Next Steps for Development
1. Monitor Fi Money MCP integration stability
2. Enhance error handling and user feedback
3. Optimize caching strategies for better performance
4. Add more comprehensive test coverage
5. Implement additional financial analysis features

### Emergency Debugging
If the system is not working:
1. Check `backend/backend.log` for errors
2. Verify database connection (PostgreSQL on port 5433)
3. Test backend endpoints with curl commands
4. Ensure `.env` file has correct configuration
5. Fall back to demo mode if Fi Money MCP is unavailable
6. Check frontend console for JavaScript errors

### Contact & Support
- Backend issues: Check Python logs and database connectivity
- Frontend issues: Check browser console and network requests
- Fi Money integration: Verify MCP client configuration and authentication flow
- Demo mode: Ensure `ENABLE_DEMO_MODE=true` in backend `.env` file