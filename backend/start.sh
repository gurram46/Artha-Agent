#!/bin/bash

# Artha AI Backend Startup Script

echo "🚀 Starting Artha AI Backend..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create it with your Gemini API key:"
    echo "   GEMINI_API_KEY=your_api_key_here"
    echo "   You can get a free API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "For now, continuing with default settings..."
fi

# Check if sample data exists
if [ ! -d "../mcp-docs/sample_responses" ]; then
    echo "⚠️  Sample data directory not found at ../mcp-docs/sample_responses"
    echo "   Please ensure the mcp-docs folder with sample responses is available."
fi

echo "🤖 Starting FastAPI server..."
echo "💡 The server will be available at: http://localhost:8000"
echo "📚 API documentation will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python main_fastapi.py