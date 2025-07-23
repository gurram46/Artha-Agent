#!/usr/bin/env python3
"""
Start Stock AI Agents Server

This script starts the Stock AI Agents server for the Artha-Agent system.
It provides comprehensive stock research and personalized recommendations.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = [
        'flask',
        'flask-cors', 
        'google-genai',
        'asyncio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check for Google AI API key
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("⚠️ GOOGLE_AI_API_KEY environment variable not set")
        print("   The system will run in fallback mode with limited AI capabilities")
        print("   To enable full AI features, set your Google AI API key:")
        print("   export GOOGLE_AI_API_KEY='your_api_key_here'")
        return False
    else:
        print("✅ Google AI API key configured")
        return True

def start_server():
    """Start the Stock AI Agents server."""
    print("🚀 Starting Stock AI Agents Server...")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    server_file = script_dir / "stock_api_server.py"
    
    if not server_file.exists():
        print(f"❌ Server file not found: {server_file}")
        return False
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(script_dir.parent.parent)  # Add backend root to Python path
    
    # Start the server
    try:
        print(f"📂 Server location: {server_file}")
        print("🌐 Starting on http://localhost:8001")
        print("📚 Available endpoints:")
        print("   GET  /health - Health check")
        print("   POST /api/stock/research - Comprehensive stock research") 
        print("   POST /api/stock/recommend - Personalized recommendation")
        print("   POST /api/stock/full-analysis - Complete analysis")
        print("   GET  /api/agents/status - Agent status")
        print("\n🔗 Integration with frontend:")
        print("   Set STOCK_AI_URL=http://localhost:8001 in frontend environment")
        print("\n" + "="*60)
        
        # Run the server
        subprocess.run([
            sys.executable, str(server_file)
        ], env=env, cwd=str(script_dir))
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main function to start the Stock AI Agents system."""
    print("=" * 60)
    print("🤖 ARTHA-AGENT STOCK AI SYSTEM")
    print("=" * 60)
    print("Comprehensive Stock Research & Personalized Recommendations")
    print("Powered by Google AI & Grounding Technology")
    print("=" * 60)
    
    # Check requirements
    print("\n📋 Checking system requirements...")
    if not check_requirements():
        return 1
    
    print("✅ All required packages are installed")
    
    # Check environment
    api_configured = check_environment()
    
    if not api_configured:
        response = input("\n❓ Continue without AI capabilities? (y/N): ").lower()
        if response != 'y':
            print("💡 Configure your Google AI API key and try again")
            return 1
    
    # Start server
    print("\n🚀 Initializing Stock AI Agents...")
    success = start_server()
    
    if success:
        print("✅ Stock AI Agents server stopped successfully")
        return 0
    else:
        print("❌ Failed to start Stock AI Agents server")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)