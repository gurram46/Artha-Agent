# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Flask web application for Investment Agent with Angel One integration.
Provides a web interface for investment recommendations with "Invest Now" functionality.
"""

import os
import json
import asyncio
from flask import Flask, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from investment_agent.agent import root_agent
from investment_agent.angel_integration import get_angel_integration

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Global variables for agent
runner = None
angel_integration = None

def initialize_agent():
    """Initialize the investment agent and Angel One integration."""
    global runner, angel_integration
    
    try:
        # Initialize the investment agent
        runner = InMemoryRunner(root_agent)
        print("✅ Investment Agent initialized successfully")
        
        # Initialize Angel One integration
        angel_integration = get_angel_integration()
        if angel_integration:
            print("✅ Angel One integration initialized")
        else:
            print("⚠️ Angel One integration not configured (API key missing)")
            
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        runner = None

@app.route('/')
def index():
    """Main page with investment query form."""
    return get_index_template()

@app.route('/api/get_recommendation', methods=['POST'])
def get_recommendation():
    """Get investment recommendation from the agent."""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not runner:
            return jsonify({'error': 'Investment agent not initialized'}), 500
        
        # Get recommendation from the agent using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(runner.run_async(user_query))
        finally:
            loop.close()
        
        # Extract investment recommendations for Angel One integration
        recommendations = extract_investment_recommendations(response)
        
        # Generate Angel One button data if integration is available
        angel_button_data = None
        if angel_integration and recommendations:
            angel_button_data = angel_integration.create_investment_button_data(recommendations)
        
        return jsonify({
            'recommendation': response,
            'angel_button': angel_button_data,
            'has_angel_integration': angel_integration is not None
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting recommendation: {str(e)}'}), 500

@app.route('/api/invest_now', methods=['POST'])
def invest_now():
    """Handle the "Invest Now" button click and redirect to Angel One."""
    try:
        data = request.get_json()
        recommendations = data.get('recommendations', [])
        
        if not angel_integration:
            return jsonify({'error': 'Angel One integration not configured'}), 400
        
        if not recommendations:
            return jsonify({'error': 'No investment recommendations provided'}), 400
        
        # Generate Angel One investment URL
        investment_url = angel_integration.generate_investment_url(recommendations)
        
        return jsonify({
            'investment_url': investment_url,
            'message': 'Redirecting to Angel One for investment execution'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating investment URL: {str(e)}'}), 500

def extract_investment_recommendations(agent_response):
    """
    Extract structured investment recommendations from agent response.
    This function parses the agent's text response to identify specific investment products.
    """
    recommendations = []
    
    try:
        # Look for common investment product patterns in the response
        response_text = str(agent_response).lower()
        
        # Common ETF patterns
        etf_patterns = {
            'nifty': {'symbol': 'NIFTYBEES', 'name': 'Nippon India ETF Nifty BeES'},
            'sensex': {'symbol': 'SETFBEES', 'name': 'Nippon India ETF Sensex BeES'},
            'gold': {'symbol': 'GOLDBEES', 'name': 'Nippon India ETF Gold BeES'},
            'bank nifty': {'symbol': 'BANKBEES', 'name': 'Nippon India ETF Bank BeES'}
        }
        
        # Look for ETF mentions
        for pattern, details in etf_patterns.items():
            if pattern in response_text:
                recommendations.append({
                    'name': details['name'],
                    'symbol': details['symbol'],
                    'exchange': 'NSE',
                    'amount': 5000,  # Default amount
                    'quantity': 50,  # Default quantity
                    'order_type': 'MARKET',
                    'product_type': 'ETF'
                })
        
        # Look for mutual fund mentions (simplified pattern matching)
        mf_patterns = {
            'sbi bluechip': {'name': 'SBI Bluechip Fund', 'amount': 5000},
            'hdfc top 100': {'name': 'HDFC Top 100 Fund', 'amount': 5000},
            'icici prudential': {'name': 'ICICI Prudential Bluechip Fund', 'amount': 5000},
            'axis bluechip': {'name': 'Axis Bluechip Fund', 'amount': 5000}
        }
        
        for pattern, details in mf_patterns.items():
            if pattern in response_text:
                recommendations.append({
                    'name': details['name'],
                    'amount': details['amount'],
                    'product_type': 'Mutual Fund',
                    'sip_amount': 1000  # Default SIP amount
                })
        
        # If no specific patterns found, create a generic recommendation
        if not recommendations:
            recommendations.append({
                'name': 'Diversified Portfolio',
                'amount': 10000,
                'product_type': 'Mixed',
                'note': 'Please review the detailed recommendations above'
            })
            
    except Exception as e:
        print(f"Error extracting recommendations: {e}")
        
    return recommendations

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'agent_initialized': runner is not None,
        'angel_integration': angel_integration is not None
    })

# HTML Templates (embedded for simplicity)
@app.route('/templates/index.html')
def get_index_template():
    """Serve the main HTML template."""
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Agent - AI-Powered Investment Recommendations</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .query-section {
            margin-bottom: 30px;
        }
        
        .query-section label {
            display: block;
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .query-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1em;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #4CAF50;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
        }
        
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result-section {
            display: none;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .recommendation {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        
        .angel-section {
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 20px;
        }
        
        .invest-now-btn {
            background: white;
            color: #FF6B35;
            border: none;
            padding: 15px 30px;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s;
        }
        
        .invest-now-btn:hover {
            transform: scale(1.05);
        }
        
        .disclaimer {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 0.9em;
        }
        
        .example-queries {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .example-queries h3 {
            color: #1976d2;
            margin-bottom: 10px;
        }
        
        .example-query {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .example-query:hover {
            background: #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Investment Agent</h1>
            <p>AI-Powered Investment Recommendations with Direct Angel One Execution</p>
        </div>
        
        <div class="main-content">
            <div class="example-queries">
                <h3>💡 Example Queries:</h3>
                <div class="example-query" onclick="setQuery('I am 25 years old, earning ₹50,000 per month. I want to start investing ₹10,000 monthly for long-term wealth creation.')">
                    "I am 25 years old, earning ₹50,000 per month. I want to start investing ₹10,000 monthly for long-term wealth creation."
                </div>
                <div class="example-query" onclick="setQuery('I have ₹2 lakh to invest as lump sum. I am 35 years old with moderate risk appetite.')">
                    "I have ₹2 lakh to invest as lump sum. I am 35 years old with moderate risk appetite."
                </div>
                <div class="example-query" onclick="setQuery('I want to invest ₹5,000 monthly in mutual funds for my child education in 15 years.')">
                    "I want to invest ₹5,000 monthly in mutual funds for my child education in 15 years."
                </div>
            </div>
            
            <div class="query-section">
                <label for="investmentQuery">Tell me about your investment goals:</label>
                <textarea 
                    id="investmentQuery" 
                    class="query-input" 
                    placeholder="Example: I am 30 years old, earning ₹75,000 per month. I want to invest ₹15,000 monthly for retirement planning. I have moderate risk tolerance and prefer a mix of equity and debt investments."
                ></textarea>
            </div>
            
            <button class="submit-btn" onclick="getRecommendation()">
                Get Investment Recommendation
            </button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing your requirements and generating personalized investment recommendations...</p>
            </div>
            
            <div class="result-section" id="resultSection">
                <h3>📊 Your Personalized Investment Recommendation:</h3>
                <div class="recommendation" id="recommendation"></div>
                
                <div class="angel-section" id="angelSection" style="display: none;">
                    <h3>🚀 Ready to Invest? Execute Directly with Angel One!</h3>
                    <p>Click the button below to execute your investment recommendations directly through Angel One API.</p>
                    <button class="invest-now-btn" onclick="investNow()">
                        🚀 Invest Now with Angel One
                    </button>
                    <p style="margin-top: 10px; font-size: 0.9em;">
                        You'll be redirected to Angel One with pre-filled investment details.
                    </p>
                </div>
                
                <div class="disclaimer">
                    <strong>⚠️ Important Disclaimer:</strong> This is for educational and informational purposes only. 
                    Not financial advice. Please consult with a qualified financial advisor before making investment decisions. 
                    Past performance does not guarantee future results.
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentRecommendations = [];
        
        function setQuery(query) {
            document.getElementById('investmentQuery').value = query;
        }
        
        async function getRecommendation() {
            const query = document.getElementById('investmentQuery').value.trim();
            
            if (!query) {
                alert('Please enter your investment query.');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultSection').style.display = 'none';
            document.querySelector('.submit-btn').disabled = true;
            
            try {
                const response = await fetch('/api/get_recommendation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Display recommendation
                document.getElementById('recommendation').textContent = data.recommendation;
                document.getElementById('resultSection').style.display = 'block';
                
                // Show Angel One section if integration is available
                if (data.has_angel_integration && data.angel_button) {
                    document.getElementById('angelSection').style.display = 'block';
                    currentRecommendations = data.angel_button.products || [];
                }
                
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.submit-btn').disabled = false;
            }
        }
        
        async function investNow() {
            if (currentRecommendations.length === 0) {
                alert('No investment recommendations available.');
                return;
            }
            
            try {
                const response = await fetch('/api/invest_now', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ recommendations: currentRecommendations })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Redirect to Angel One
                window.open(data.investment_url, '_blank');
                
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        // Allow Enter key to submit
        document.getElementById('investmentQuery').addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                getRecommendation();
            }
        });
    </script>
</body>
</html>
    '''
    return html_content

# Create templates directory and save the template
def create_templates():
    """Create templates directory and save HTML template."""
    import os
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(get_index_template())

if __name__ == '__main__':
    print("🚀 Starting Investment Agent Web Application...")
    print("=" * 50)
    
    # Initialize the agent
    initialize_agent()
    
    # Create templates
    create_templates()
    
    # Check environment setup
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️ Warning: GOOGLE_API_KEY not found in environment variables")
    
    if not os.getenv('ANGEL_API_KEY'):
        print("⚠️ Warning: ANGEL_API_KEY not found - Angel One integration will be disabled")
    
    print("\n✅ Web application starting...")
    print("🌐 Open your browser and go to: http://localhost:4000")
    print("💡 Use Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=4000)