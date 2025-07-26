"""
Demat Account Broker Selection Service
Provides broker selection and account access functionality for investment execution.
"""

import webbrowser
import time
from typing import Dict, List, Optional

class DematBrokerService:
    """Service for handling demat account broker selection and login."""
    
    def __init__(self):
        self.supported_brokers = {
            "1": {
                "name": "Angel One",
                "url": "https://trade.angelone.in/",
                "login_url": "https://trade.angelone.in/login",
                "features": ["Zero brokerage on delivery", "Advanced trading tools", "Research reports"],
                "description": "India's leading discount broker with comprehensive trading platform"
            },
            "2": {
                "name": "Zerodha",
                "url": "https://kite.zerodha.com/",
                "login_url": "https://kite.zerodha.com/",
                "features": ["Kite platform", "Coin for mutual funds", "Educational content"],
                "description": "Pioneer in discount broking with user-friendly Kite platform"
            },
            "3": {
                "name": "Groww",
                "url": "https://groww.in/",
                "login_url": "https://groww.in/login",
                "features": ["Simple interface", "Mutual funds & stocks", "Goal-based investing"],
                "description": "Beginner-friendly platform with simple investment process"
            },
            "4": {
                "name": "Upstox",
                "url": "https://upstox.com/",
                "login_url": "https://login.upstox.com/",
                "features": ["Pro platform", "Low brokerage", "Advanced charts"],
                "description": "Technology-driven broker with professional trading tools"
            },
            "5": {
                "name": "IIFL Securities",
                "url": "https://www.iiflsecurities.com/",
                "login_url": "https://www.iiflsecurities.com/login",
                "features": ["Full-service broker", "Research & advisory", "Wealth management"],
                "description": "Full-service broker with comprehensive financial services"
            },
            "6": {
                "name": "Paytm Money",
                "url": "https://www.paytmmoney.com/",
                "login_url": "https://www.paytmmoney.com/login",
                "features": ["Zero brokerage delivery", "Digital-first", "Easy KYC"],
                "description": "Digital-first broker with zero brokerage on delivery trades"
            }
        }
    
    def display_broker_selection(self) -> None:
        """Display the broker selection interface."""
        print("\n" + "=" * 60)
        print("🏦 SELECT YOUR DEMAT ACCOUNT BROKER")
        print("=" * 60)
        print("\nChoose your preferred broker to execute the investment:")
        print()
        
        for broker_id, broker_info in self.supported_brokers.items():
            print(f"  {broker_id}. {broker_info['name']}")
            print(f"     📝 {broker_info['description']}")
            print(f"     ✨ Features: {', '.join(broker_info['features'][:2])}")
            print()
        
        print("  0. Cancel and return to recommendations")
        print("\n" + "=" * 60)
    
    def get_broker_choice(self) -> Optional[str]:
        """Get user's broker selection."""
        while True:
            try:
                choice = input("👆 Enter your choice (0-6): ").strip()
                
                if choice == "0":
                    print("\n📝 Returning to recommendations...")
                    return None
                
                if choice in self.supported_brokers:
                    return choice
                else:
                    print("❌ Invalid choice. Please enter a number between 0-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Investment cancelled by user.")
                return None
            except Exception as e:
                print(f"❌ Error: {e}. Please try again.")
    
    def execute_broker_login(self, broker_id: str) -> bool:
        """Execute broker login and account access."""
        broker_info = self.supported_brokers[broker_id]
        
        print(f"\n🚀 Connecting to {broker_info['name']}...")
        print("=" * 50)
        
        # Show broker information
        print(f"📊 Broker: {broker_info['name']}")
        print(f"📝 Description: {broker_info['description']}")
        print(f"✨ Key Features:")
        for feature in broker_info['features']:
            print(f"   • {feature}")
        
        print(f"\n🔐 Opening {broker_info['name']} login page...")
        print("Please complete the following steps:")
        print("1. 🔑 Log in to your account")
        print("2. 📊 Navigate to trading/investment section")
        print("3. 💰 Execute the recommended investments")
        print("4. ✅ Confirm your transactions")
        
        # Confirmation before opening browser
        proceed = input(f"\n🌐 Open {broker_info['name']} in your browser? (y/n): ").strip().lower()
        
        if proceed in ['y', 'yes']:
            try:
                # Open broker login page
                webbrowser.open(broker_info['login_url'])
                print(f"\n✅ {broker_info['name']} opened in your default browser")
                print("🔄 Please complete your investment in the opened tab")
                
                # Wait a moment for browser to open
                time.sleep(2)
                
                # Show post-login guidance
                self._show_post_login_guidance(broker_info['name'])
                
                return True
                
            except Exception as e:
                print(f"❌ Error opening browser: {e}")
                print(f"💡 Please manually visit: {broker_info['login_url']}")
                return False
        else:
            print(f"📝 You can manually visit: {broker_info['login_url']}")
            return False
    
    def _show_post_login_guidance(self, broker_name: str) -> None:
        """Show guidance after broker login."""
        print(f"\n📋 INVESTMENT EXECUTION GUIDE - {broker_name}")
        print("=" * 50)
        
        if broker_name == "Angel One":
            print("1. 📊 Go to 'Trade' section")
            print("2. 🔍 Search for recommended stocks/ETFs")
            print("3. 💰 Enter investment amounts as recommended")
            print("4. 📈 Choose 'Market' or 'Limit' order type")
            print("5. ✅ Review and place orders")
            
        elif broker_name == "Zerodha":
            print("1. 📊 Open Kite trading platform")
            print("2. 🔍 Use search to find recommended instruments")
            print("3. 💰 Enter quantities based on recommendations")
            print("4. 📈 Select order type (CNC for delivery)")
            print("5. ✅ Review and confirm orders")
            
        elif broker_name == "Groww":
            print("1. 📊 Go to 'Stocks' or 'Mutual Funds' section")
            print("2. 🔍 Search for recommended investments")
            print("3. 💰 Enter investment amounts")
            print("4. 📈 Choose investment type (SIP/Lumpsum)")
            print("5. ✅ Complete payment and confirmation")
            
        else:
            print("1. 📊 Navigate to trading/investment section")
            print("2. 🔍 Search for recommended instruments")
            print("3. 💰 Enter investment amounts as suggested")
            print("4. 📈 Choose appropriate order types")
            print("5. ✅ Review and execute trades")
        
        print("\n💡 Tips:")
        print("   • Double-check investment amounts")
        print("   • Review all fees and charges")
        print("   • Keep transaction confirmations")
        print("   • Monitor your portfolio regularly")
        
        # Wait for user acknowledgment
        input("\n⏸️  Press Enter when you've completed your investment...")
        print("🎉 Thank you for using our investment service!")
        print("📈 Happy investing! 🚀")

def create_demat_broker_interface(recommendations: List[str]) -> None:
    """
    Create and run the demat broker selection interface.
    
    Args:
        recommendations: List of investment recommendations from the agent
    """
    print("\n" + "🎯" * 20)
    print("INVESTMENT EXECUTION PORTAL")
    print("🎯" * 20)
    
    print("\n📊 Based on your personalized recommendations, you can now:")
    print("   • Choose your preferred broker")
    print("   • Access your demat account")
    print("   • Execute the recommended investments")
    print("   • Start building your portfolio")
    
    # Initialize broker service
    broker_service = DematBrokerService()
    
    # Show broker selection
    broker_service.display_broker_selection()
    
    # Get user choice
    broker_choice = broker_service.get_broker_choice()
    
    if broker_choice:
        # Execute broker login and investment flow
        success = broker_service.execute_broker_login(broker_choice)
        
        if success:
            print("\n✅ Investment process initiated successfully!")
        else:
            print("\n⚠️ Please try again or contact your broker for assistance.")
    else:
        print("\n📝 Investment execution cancelled.")
        print("💡 You can always execute these recommendations later through your preferred broker.")

if __name__ == "__main__":
    # Test the broker selection interface
    test_recommendations = [
        "Invest ₹20,000 in Nifty ETF (NIFTYBEES)",
        "Invest ₹15,000 in Bank Nifty ETF (BANKBEES)",
        "Invest ₹10,000 in Gold ETF (GOLDBEES)"
    ]
    
    create_demat_broker_interface(test_recommendations)