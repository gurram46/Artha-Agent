#!/bin/bash

# Artha-Agent Service Shutdown Script
# This script stops all Artha-Agent services

echo "🛑 Stopping Artha-Agent Services..."
echo "==================================="

# Function to stop a service
stop_service() {
    local name=$1
    local pidfile="/tmp/artha-$name.pid"
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔄 Stopping $name (PID: $pid)..."
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $name..."
                kill -9 "$pid"
            fi
            
            echo "✅ $name stopped"
        else
            echo "⚠️  $name was not running"
        fi
        rm -f "$pidfile"
    else
        echo "⚠️  No PID file found for $name"
    fi
}

# Stop all services
stop_service "frontend"
stop_service "backend-api" 
stop_service "stock-ai"

# Also kill any remaining processes on our ports
echo ""
echo "🔍 Checking for remaining processes on ports 3000, 8000, 8001..."

for port in 3000 8000 8001; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "🔄 Killing process on port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null
    fi
done

echo ""
echo "✅ All Artha-Agent services stopped successfully!"
echo "💡 You can restart with: ./start-all-services.sh"