#!/bin/bash

# Artha-Agent Complete Application Startup Script
# This script starts all required services for the real-data-only application

echo "🚀 Starting Artha-Agent with Real Data APIs..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the Artha-Agent root directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to start a service in background
start_service() {
    local name=$1
    local command=$2
    local directory=$3
    local port=$4
    
    echo "🔄 Starting $name on port $port..."
    cd "$directory"
    $command &
    local pid=$!
    echo "$pid" > "/tmp/artha-$name.pid"
    echo "✅ $name started (PID: $pid)"
    cd - > /dev/null
}

# Check required ports
echo "🔍 Checking required ports..."
PORTS_OK=true

if ! check_port 3000; then PORTS_OK=false; fi  # Frontend
if ! check_port 8000; then PORTS_OK=false; fi  # Main Backend API
if ! check_port 8001; then PORTS_OK=false; fi  # Stock AI Agents

if [ "$PORTS_OK" = false ]; then
    echo "❌ Some required ports are in use. Please stop other services or kill processes on ports 3000, 8000, 8001"
    exit 1
fi

echo "✅ All ports are available"

# Start Backend Financial API (Port 8000)
echo ""
echo "📊 Starting Main Backend API (Port 8000)..."
if [ -f "backend/requirements.txt" ]; then
    echo "🔄 Installing Python dependencies..."
    cd backend
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Python dependencies installed"
    start_service "backend-api" "python api_server.py" "$(pwd)" "8000"
    cd ..
else
    echo "⚠️  Backend requirements.txt not found - skipping backend API"
fi

# Start Stock AI Agents (Port 8001)
echo ""
echo "🤖 Starting Stock AI Agents (Port 8001)..."
if [ -f "backend/agents/stock_agents/requirements.txt" ]; then
    echo "🔄 Installing Stock AI dependencies..."
    cd backend/agents/stock_agents
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Stock AI dependencies installed"
    
    # Check for Google AI API key
    if [ -z "$GOOGLE_AI_API_KEY" ]; then
        echo "⚠️  GOOGLE_AI_API_KEY not set - Stock AI will run in limited mode"
        echo "   Set GOOGLE_AI_API_KEY='your_key' for full AI capabilities"
    else
        echo "✅ Google AI API key configured"
    fi
    
    start_service "stock-ai" "python stock_api_server.py" "$(pwd)" "8001"
    cd ../../..
else
    echo "⚠️  Stock AI requirements.txt not found - skipping Stock AI agents"
fi

# Start Frontend (Port 3000)
echo ""
echo "🌐 Starting Frontend (Port 3000)..."
if [ -f "frontend/package.json" ]; then
    echo "🔄 Installing Node.js dependencies..."
    cd frontend
    npm install > /dev/null 2>&1
    echo "✅ Node.js dependencies installed"
    start_service "frontend" "npm run dev" "$(pwd)" "3000"
    cd ..
else
    echo "❌ Frontend package.json not found"
    exit 1
fi

# Wait a moment for services to start
sleep 3

echo ""
echo "🎉 Artha-Agent Started Successfully!"
echo "=================================="
echo ""
echo "📱 Frontend:           http://localhost:3000"
echo "🔗 Backend API:        http://localhost:8000"
echo "🤖 Stock AI Agents:    http://localhost:8001"
echo ""
echo "📊 Real Data Sources:"
echo "   • Financial Data:   Fi MCP (via backend)"
echo "   • Stock Data:       NSE API (stock-market-india)"
echo "   • Stock Analysis:   Google AI + Grounding"
echo ""
echo "🛑 To stop all services, run: ./stop-all-services.sh"
echo "📋 Service PIDs saved in /tmp/artha-*.pid"
echo ""
echo "⏳ Services are starting... Please wait 30 seconds before accessing the application"

# Show real-time logs (optional)
echo ""
echo "📜 Showing frontend logs (Ctrl+C to exit log view, services continue running):"
echo "============================================================================"
tail -f frontend/.next/trace 2>/dev/null || echo "Frontend logs will appear once the application starts..."