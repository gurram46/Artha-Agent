"""
Stock API Server - Flask server to integrate stock agents with frontend

This server provides REST API endpoints for:
- Stock research using Google Grounding
- Personalized investment recommendations
- Integration with the existing Artha-Agent frontend
"""

import os
import sys
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from stock_agents.research_agent import StockResearchAgent
from stock_agents.recommendation_agent import StockRecommendationAgent

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize agents
research_agent = None
recommendation_agent = None

def initialize_agents():
    """Initialize the AI agents with API keys."""
    global research_agent, recommendation_agent
    
    try:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            print("⚠️ Warning: GOOGLE_AI_API_KEY not found in environment variables")
            print("   Using fallback mode - some features may be limited")
        
        research_agent = StockResearchAgent(api_key=api_key)
        recommendation_agent = StockRecommendationAgent(api_key=api_key)
        
        print("✅ Stock AI agents initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_initialized": research_agent is not None and recommendation_agent is not None
    })

@app.route('/api/stock/research', methods=['POST'])
def research_stock():
    """
    Comprehensive stock research endpoint.
    
    Expected payload:
    {
        "symbol": "TCS.NS",
        "company_name": "Tata Consultancy Services" (optional)
    }
    """
    try:
        if not research_agent:
            return jsonify({"error": "Research agent not initialized"}), 500
        
        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({"error": "Symbol is required"}), 400
        
        symbol = data['symbol']
        company_name = data.get('company_name')
        
        print(f"🔍 Starting research for {symbol}...")
        
        # Run async research in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            research_result = loop.run_until_complete(
                research_agent.research_stock_comprehensive(symbol, company_name)
            )
        finally:
            loop.close()
        
        print(f"✅ Research completed for {symbol}")
        return jsonify(research_result)
        
    except Exception as e:
        print(f"❌ Error in stock research: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Failed to complete stock research",
            "details": str(e)
        }), 500

@app.route('/api/stock/recommend', methods=['POST'])
def recommend_stock():
    """
    Generate personalized stock recommendation.
    
    Expected payload:
    {
        "symbol": "TCS.NS",
        "user_profile": {
            "riskTolerance": "moderate",
            "investmentHorizon": "long", 
            "investmentGoal": "growth",
            "monthlyInvestment": 25000
        },
        "stock_data": {
            "currentPrice": 3500,
            "marketCap": "13.5L Cr"
        },
        "research_data": { ... } (optional - will research if not provided)
    }
    """
    try:
        if not recommendation_agent:
            return jsonify({"error": "Recommendation agent not initialized"}), 500
        
        data = request.get_json()
        if not data or 'symbol' not in data or 'user_profile' not in data:
            return jsonify({"error": "Symbol and user_profile are required"}), 400
        
        symbol = data['symbol']
        user_profile = data['user_profile']
        stock_data = data.get('stock_data', {})
        research_data = data.get('research_data')
        
        print(f"🎯 Generating recommendation for {symbol}...")
        
        # If no research data provided, conduct research first
        if not research_data:
            if not research_agent:
                return jsonify({"error": "Research agent not initialized for auto-research"}), 500
                
            print("📊 Conducting research first...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                research_data = loop.run_until_complete(
                    research_agent.research_stock_comprehensive(symbol)
                )
            finally:
                loop.close()
        
        # Generate recommendation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            recommendation = loop.run_until_complete(
                recommendation_agent.generate_recommendation(research_data, user_profile, stock_data)
            )
        finally:
            loop.close()
        
        print(f"✅ Recommendation generated for {symbol}")
        return jsonify(recommendation)
        
    except Exception as e:
        print(f"❌ Error in stock recommendation: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Failed to generate stock recommendation",
            "details": str(e)
        }), 500

@app.route('/api/stock/full-analysis', methods=['POST'])
def full_stock_analysis():
    """
    Complete stock analysis - research + recommendation in one call.
    
    Expected payload:
    {
        "symbol": "TCS.NS",
        "company_name": "Tata Consultancy Services" (optional),
        "user_profile": {
            "riskTolerance": "moderate",
            "investmentHorizon": "long",
            "investmentGoal": "growth", 
            "monthlyInvestment": 25000
        },
        "stock_data": {
            "currentPrice": 3500,
            "marketCap": "13.5L Cr"
        }
    }
    """
    try:
        if not research_agent or not recommendation_agent:
            return jsonify({"error": "Agents not initialized"}), 500
        
        data = request.get_json()
        if not data or 'symbol' not in data or 'user_profile' not in data:
            return jsonify({"error": "Symbol and user_profile are required"}), 400
        
        symbol = data['symbol']
        company_name = data.get('company_name')
        user_profile = data['user_profile']
        stock_data = data.get('stock_data', {})
        
        print(f"🚀 Starting full analysis for {symbol}...")
        
        # Run both research and recommendation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Step 1: Comprehensive research
            print("🔍 Phase 1: Conducting comprehensive research...")
            research_result = loop.run_until_complete(
                research_agent.research_stock_comprehensive(symbol, company_name)
            )
            
            # Step 2: Generate personalized recommendation
            print("🎯 Phase 2: Generating personalized recommendation...")
            recommendation = loop.run_until_complete(
                recommendation_agent.generate_recommendation(research_result, user_profile, stock_data)
            )
            
        finally:
            loop.close()
        
        # Combine results
        full_analysis = {
            "symbol": symbol,
            "company_name": company_name or research_result.get("company_name", symbol),
            "analysis_timestamp": datetime.now().isoformat(),
            "research": research_result,
            "recommendation": recommendation,
            "summary": {
                "score": recommendation.get("score", 50),
                "sentiment": recommendation.get("sentiment", "Hold"),
                "confidence": recommendation.get("confidence", 0.5),
                "research_quality": research_result.get("metadata", {}),
                "user_alignment": recommendation.get("alignment_score", 50)
            }
        }
        
        print(f"✅ Full analysis completed for {symbol}")
        return jsonify(full_analysis)
        
    except Exception as e:
        print(f"❌ Error in full stock analysis: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Failed to complete full stock analysis", 
            "details": str(e)
        }), 500

@app.route('/api/agents/status', methods=['GET'])
def agents_status():
    """Get status of all agents."""
    return jsonify({
        "research_agent": research_agent is not None,
        "recommendation_agent": recommendation_agent is not None,
        "google_ai_api_configured": bool(os.getenv("GOOGLE_AI_API_KEY")),
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Stock AI API Server...")
    
    # Initialize agents
    if initialize_agents():
        print("✅ All systems ready!")
    else:
        print("⚠️ Starting with limited functionality")
    
    # Start server
    port = int(os.getenv('PORT', 8001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Server starting on http://localhost:{port}")
    print("📚 Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/stock/research - Comprehensive stock research")
    print("  POST /api/stock/recommend - Personalized recommendation")
    print("  POST /api/stock/full-analysis - Complete research + recommendation")
    print("  GET  /api/agents/status - Agents status")
    
    app.run(host='0.0.0.0', port=port, debug=debug)