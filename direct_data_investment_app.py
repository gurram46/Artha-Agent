import json
import os
from flask import Flask, render_template, request, jsonify
from investment_agent.agent import investment_coordinator
from mcp import InMemoryRunner

app = Flask(__name__)

class DirectDataService:
    def __init__(self):
        self.data_dir = "fi-mcp-dev/test_data_dir"
        
    def get_user_data(self, phone_number):
        """Load user data directly from JSON files"""
        user_dir = os.path.join(self.data_dir, phone_number)
        if not os.path.exists(user_dir):
            return None
            
        user_data = {}
        
        # Load all available data files
        data_files = [
            'fetch_net_worth.json',
            'fetch_bank_transactions.json', 
            'fetch_credit_report.json',
            'fetch_epf_details.json',
            'fetch_mf_transactions.json',
            'fetch_stock_transactions.json'
        ]
        
        for file_name in data_files:
            file_path = os.path.join(user_dir, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                        if content:
                            user_data[file_name.replace('.json', '')] = json.loads(content)
                        else:
                            user_data[file_name.replace('.json', '')] = {}
                except json.JSONDecodeError:
                    user_data[file_name.replace('.json', '')] = {}
                    
        return user_data
    
    def get_available_users(self):
        """Get list of available test users"""
        if not os.path.exists(self.data_dir):
            return []
        return [d for d in os.listdir(self.data_dir) if os.path.isdir(os.path.join(self.data_dir, d))]

# Initialize services
data_service = DirectDataService()

@app.route('/')
def index():
    return render_template('simple_index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "data_source": "direct_files"})

@app.route('/api/users')
def get_users():
    """Get available test users"""
    users = data_service.get_available_users()
    return jsonify({"users": users})

@app.route('/api/user/<phone_number>')
def get_user_profile(phone_number):
    """Get user financial profile"""
    user_data = data_service.get_user_data(phone_number)
    if not user_data:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user_data)

@app.route('/api/recommend', methods=['POST'])
def get_investment_recommendation():
    """Generate investment recommendation using the agent"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        investment_amount = data.get('investment_amount', 10000)
        
        if not phone_number:
            return jsonify({"error": "Phone number required"}), 400
            
        # Get user data
        user_data = data_service.get_user_data(phone_number)
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Create user context for the agent
        user_context = f"""
        User Financial Profile (Phone: {phone_number}):
        
        Net Worth Data: {json.dumps(user_data.get('fetch_net_worth', {}), indent=2)}
        
        Mutual Fund Holdings: {json.dumps(user_data.get('fetch_mf_transactions', {}), indent=2)}
        
        Stock Holdings: {json.dumps(user_data.get('fetch_stock_transactions', {}), indent=2)}
        
        Credit Report: {json.dumps(user_data.get('fetch_credit_report', {}), indent=2)}
        
        EPF Details: {json.dumps(user_data.get('fetch_epf_details', {}), indent=2)}
        
        Investment Amount: ₹{investment_amount:,}
        """
        
        # Generate recommendation using investment agent
        query = f"Based on this user's financial profile, provide investment recommendations for ₹{investment_amount:,}. Consider their current portfolio, risk profile, and financial situation."
        
        runner = InMemoryRunner()
        result = runner.run(investment_coordinator, query, user_context)
        
        return jsonify({
            "recommendation": result,
            "user_data_summary": {
                "phone_number": phone_number,
                "has_net_worth": bool(user_data.get('fetch_net_worth')),
                "has_mf_data": bool(user_data.get('fetch_mf_transactions')),
                "has_stock_data": bool(user_data.get('fetch_stock_transactions')),
                "has_credit_data": bool(user_data.get('fetch_credit_report')),
                "investment_amount": investment_amount
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Direct Data Investment App...")
    print("Available test users:", data_service.get_available_users())
    app.run(debug=True, port=5000)