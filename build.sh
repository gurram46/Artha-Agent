#!/bin/bash
# Render build script for backend

set -e

echo "🚀 Starting Render build for Artha-AI SAndeep backend..."

# Navigate to backend directory
cd backend

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🤖 Installing SAndeep AI dependencies..."
pip install -r sandeep_investment_system/requirements.txt

echo "🧠 Installing Google ADK for SAndeep..."
pip install google-adk google-genai

echo "📊 Verifying MCP data files..."
if [ -d "../mcp-docs" ]; then
    echo "✅ MCP sample data found"
    ls -la ../mcp-docs/
else
    echo "⚠️ MCP sample data not found, but will work with real Fi Money data"
fi

echo "🔧 Setting up Python path..."
export PYTHONPATH="/opt/render/project/src/backend:$PYTHONPATH"

echo "✅ Render build completed successfully!"
echo "🎯 Backend will start with: uvicorn api_server:app --host 0.0.0.0 --port $PORT"