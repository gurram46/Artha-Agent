"""
Broker Integration Service - Invest Now Feature
Provides seamless integration with multiple Indian brokers for immediate investment execution.
Enhanced with real-time Angel One API integration and comprehensive demat account management.
"""

import json
import logging
import re
import time
import webbrowser
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)

class BrokerIntegrationService:
    """Service for integrating with multiple Indian brokers for investment execution"""
    
    def __init__(self):
        self.supported_brokers = {
            "1": {
                "id": "angel_one",
                "name": "Angel One",
                "type": "api_web",
                "url": "https://trade.angelone.in/",
                "login_url": "https://trade.angelone.in/login",
                "features": ["Zero brokerage on delivery", "Advanced trading tools", "Research reports"],
                "description": "India's leading discount broker with comprehensive trading platform",
                "api_available": True,
                "best_for": "API Integration, Live Data, All-in-one"
            },
            "2": {
                "id": "zerodha",
                "name": "Zerodha",
                "type": "web",
                "url": "https://kite.zerodha.com/",
                "login_url": "https://kite.zerodha.com/",
                "features": ["Kite platform", "Coin for mutual funds", "Educational content"],
                "description": "Pioneer in discount broking with user-friendly Kite platform",
                "api_available": False,
                "best_for": "Active Traders, Low Cost, Advanced Tools"
            },
            "3": {
                "id": "groww",
                "name": "Groww",
                "type": "web",
                "url": "https://groww.in/",
                "login_url": "https://groww.in/login",
                "features": ["Simple interface", "Mutual funds & stocks", "Goal-based investing"],
                "description": "Beginner-friendly platform with simple investment process",
                "api_available": False,
                "best_for": "Beginners, Mutual Funds, Simple UI"
            },
            "4": {
                "id": "upstox",
                "name": "Upstox",
                "type": "web",
                "url": "https://upstox.com/",
                "login_url": "https://login.upstox.com/",
                "features": ["Pro platform", "Low brokerage", "Advanced charts"],
                "description": "Technology-driven broker with professional trading tools",
                "api_available": False,
                "best_for": "Professional Trading, Research, Charts"
            },
            "5": {
                "id": "iifl",
                "name": "IIFL Securities",
                "type": "web",
                "url": "https://www.iiflsecurities.com/",
                "login_url": "https://www.iiflsecurities.com/login",
                "features": ["Full-service broker", "Research & advisory", "Wealth management"],
                "description": "Full-service broker with comprehensive financial services",
                "api_available": False,
                "best_for": "Full Service, Advisory, Research Reports"
            },
            "6": {
                "id": "paytm_money",
                "name": "Paytm Money",
                "type": "web",
                "url": "https://www.paytmmoney.com/",
                "login_url": "https://www.paytmmoney.com/login",
                "features": ["Zero brokerage delivery", "Digital-first", "Easy KYC"],
                "description": "Digital-first broker with zero brokerage on delivery trades",
                "api_available": False,
                "best_for": "Digital Experience, Zero Delivery Charges"
            }
        }
        
        # Initialize Angel One service for real-time integration
        self.angel_one_service = None
        try:
            self.angel_one_service = self._initialize_angel_one_service()
        except Exception as e:
            logger.warning(f"Angel One service initialization failed: {e}")
    
    def _initialize_angel_one_service(self):
        """Initialize Angel One service for real-time API integration"""
        try:
            # Import here to avoid circular dependencies
            from .enhanced_angel_one_service import EnhancedAngelOneService
            return EnhancedAngelOneService()
        except ImportError:
            logger.warning("EnhancedAngelOneService not available - using fallback")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Angel One service: {e}")
            return None
    
    def display_broker_selection(self) -> None:
        """Display the broker selection interface (CLI-style for reference)"""
        print("\n" + "=" * 60)
        print("🏦 SELECT YOUR DEMAT ACCOUNT BROKER")
        print("=" * 60)
        print("\nChoose your preferred broker to execute the investment:")
        print()
        
        for broker_id, broker_info in self.supported_brokers.items():
            print(f"  {broker_id}. {broker_info['name']}")
            print(f"     📝 {broker_info['description']}")
            print(f"     ✨ Features: {', '.join(broker_info['features'][:2])}")
            print(f"     🎯 Best for: {broker_info['best_for']}")
            print()
        
        print("  0. Cancel and return to recommendations")
        print("\n" + "=" * 60)
    
    def execute_broker_login(self, broker_id: str) -> bool:
        """Execute broker login and account access with enhanced guidance"""
        if broker_id not in self.supported_brokers:
            return False
            
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
            logger.error(f"Error opening browser: {e}")
            print(f"💡 Please manually visit: {broker_info['login_url']}")
            return False
    
    def _show_post_login_guidance(self, broker_name: str) -> None:
        """Show detailed guidance after broker login"""
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
    
    def parse_investment_recommendations(self, recommendation_text: str) -> List[Dict[str, Any]]:
        """Parse investment recommendations from AI response to extract actionable investments"""
        investments = []
        
        try:
            # Look for fund recommendations with amounts
            fund_pattern = r'(?:Fund Name|Stock Name):\s*([^-\n]+)(?:-\s*Direct Plan Growth)?\s*.*?Investment Amount:\s*₹?([0-9,]+)'
            matches = re.findall(fund_pattern, recommendation_text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                fund_name = match[0].strip()
                amount = match[1].replace(',', '')
                
                if fund_name and amount.isdigit():
                    investments.append({
                        "type": "mutual_fund" if "Fund" in fund_name else "stock",
                        "name": fund_name,
                        "amount": int(amount),
                        "platform_recommended": "Groww, Zerodha Coin, Kuvera"
                    })
            
            # Look for SIP recommendations
            sip_pattern = r'SIP Recommendation:\s*₹?([0-9,]+)'
            sip_matches = re.findall(sip_pattern, recommendation_text, re.IGNORECASE)
            
            if sip_matches and investments:
                # Add SIP info to the last found investment
                investments[-1]["sip_amount"] = int(sip_matches[0].replace(',', ''))
            
            # Look for ETF recommendations
            etf_pattern = r'(?:ETF|Gold ETF).*?([A-Z0-9\s]+ETF).*?Investment Amount:\s*₹?([0-9,]+)'
            etf_matches = re.findall(etf_pattern, recommendation_text, re.IGNORECASE | re.DOTALL)
            
            for match in etf_matches:
                etf_name = match[0].strip()
                amount = match[1].replace(',', '')
                
                if etf_name and amount.isdigit():
                    investments.append({
                        "type": "etf",
                        "name": etf_name,
                        "amount": int(amount),
                        "platform_recommended": "Zerodha Kite, Groww, Angel One"
                    })
            
            logger.info(f"✅ Parsed {len(investments)} investment recommendations")
            return investments
            
        except Exception as e:
            logger.error(f"❌ Failed to parse recommendations: {e}")
            return []
    
    def generate_broker_urls(self, investments: List[Dict[str, Any]], preferred_broker: str = "groww") -> Dict[str, Any]:
        """Generate broker-specific URLs for immediate investment execution"""
        
        if not investments:
            return {"error": "No investments to execute"}
        
        # Convert broker name to ID if needed
        broker_id = self._get_broker_id(preferred_broker)
        
        if broker_id not in self.supported_brokers:
            broker_id = "3"  # Default to Groww
        
        broker_info = self.supported_brokers[broker_id]
        urls = []
        
        try:
            for investment in investments:
                if investment["type"] == "mutual_fund":
                    url = self._generate_mutual_fund_url(investment, preferred_broker)
                elif investment["type"] == "etf":
                    url = self._generate_etf_url(investment, preferred_broker)
                elif investment["type"] == "stock":
                    url = self._generate_stock_url(investment, preferred_broker)
                else:
                    continue
                
                if url:
                    urls.append({
                        "investment": investment["name"],
                        "amount": investment["amount"],
                        "url": url,
                        "instructions": self._get_platform_instructions(preferred_broker, investment["type"])
                    })
            
            return {
                "broker": broker_info["name"],
                "total_investments": len(urls),
                "investment_urls": urls,
                "platform_features": broker_info["features"],
                "next_steps": self._get_execution_steps(preferred_broker)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate broker URLs: {e}")
            return {"error": f"Failed to generate investment URLs: {str(e)}"}
    
    def _generate_mutual_fund_url(self, investment: Dict, broker: str) -> str:
        """Generate mutual fund investment URL for specific broker"""
        fund_name = investment["name"]
        amount = investment["amount"]
        
        if broker == "groww":
            # Groww mutual fund search and invest
            search_term = fund_name.replace(" ", "%20")
            return f"https://groww.in/mutual-funds/search?q={search_term}"
        
        elif broker == "zerodha":
            # Zerodha Coin for mutual funds
            return f"https://coin.zerodha.com/funds"
        
        elif broker == "angel_one":
            # Angel One mutual funds
            return f"https://trade.angelone.in/mutual-funds"
        
        elif broker == "paytm_money":
            # Paytm Money mutual funds
            return f"https://www.paytmmoney.com/mutual-funds"
        
        else:
            return f"https://groww.in/mutual-funds/search?q={fund_name.replace(' ', '%20')}"
    
    def _generate_etf_url(self, investment: Dict, broker: str) -> str:
        """Generate ETF investment URL for specific broker"""
        etf_name = investment["name"]
        
        if broker == "zerodha":
            return f"https://kite.zerodha.com/"
        elif broker == "angel_one":
            return f"https://trade.angelone.in/equity"
        elif broker == "groww":
            return f"https://groww.in/stocks"
        else:
            return f"https://kite.zerodha.com/"
    
    def _generate_stock_url(self, investment: Dict, broker: str) -> str:
        """Generate stock investment URL for specific broker"""
        stock_name = investment["name"]
        
        if broker == "zerodha":
            return f"https://kite.zerodha.com/"
        elif broker == "angel_one":
            return f"https://trade.angelone.in/equity"
        elif broker == "groww":
            return f"https://groww.in/stocks/{stock_name.lower().replace(' ', '-')}"
        else:
            return f"https://kite.zerodha.com/"
    
    def _get_platform_instructions(self, broker: str, investment_type: str) -> List[str]:
        """Get step-by-step instructions for each platform"""
        
        instructions = {
            "groww": {
                "mutual_fund": [
                    "1. Login to your Groww account",
                    "2. Search for the recommended fund",
                    "3. Click 'Invest Now'",
                    "4. Enter the investment amount",
                    "5. Choose payment method",
                    "6. Complete the investment"
                ],
                "etf": [
                    "1. Login to Groww",
                    "2. Go to Stocks section",
                    "3. Search for the ETF",
                    "4. Click 'Buy'",
                    "5. Enter quantity/amount",
                    "6. Place order"
                ]
            },
            "zerodha": {
                "mutual_fund": [
                    "1. Login to Zerodha Coin",
                    "2. Search for the fund",
                    "3. Select 'Direct Plan'", 
                    "4. Enter SIP/lumpsum amount",
                    "5. Set auto-pay mandate",
                    "6. Confirm investment"
                ],
                "etf": [
                    "1. Login to Kite",
                    "2. Search for ETF symbol",
                    "3. Click 'Buy'",
                    "4. Enter quantity",
                    "5. Choose order type",
                    "6. Place order"
                ]
            },
            "angel_one": {
                "mutual_fund": [
                    "1. Login to Angel One app/web",
                    "2. Go to Mutual Funds",
                    "3. Search recommended fund",
                    "4. Select investment amount",
                    "5. Choose payment mode",
                    "6. Complete transaction"
                ],
                "etf": [
                    "1. Login to Angel One",
                    "2. Go to Equity section",
                    "3. Search ETF",
                    "4. Place buy order",
                    "5. Enter amount/quantity",
                    "6. Execute trade"
                ]
            }
        }
        
        return instructions.get(broker, {}).get(investment_type, ["Login to platform", "Search for investment", "Complete purchase"])
    
    def _get_execution_steps(self, broker: str) -> List[str]:
        """Get general execution steps for the broker"""
        return [
            f"1. Click on the {self.supported_brokers[broker]['name']} links above",
            "2. Login to your existing account (or create new account)",
            "3. Follow the step-by-step instructions for each investment",
            "4. Verify investment details before confirming",
            "5. Complete payment and save transaction confirmations",
            "6. Set up SIP auto-pay for recurring investments"
        ]
    
    def launch_investment_platform(self, broker_urls: Dict[str, Any]) -> bool:
        """Launch the investment platform in browser"""
        try:
            if "investment_urls" in broker_urls:
                for investment_url in broker_urls["investment_urls"]:
                    webbrowser.open(investment_url["url"])
                    logger.info(f"🚀 Opened {investment_url['investment']} investment page")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to launch platform: {e}")
            return False
    
    def get_broker_comparison(self) -> Dict[str, Any]:
        """Get comparison of all supported brokers"""
        comparison = {}
        for broker_id, broker_info in self.supported_brokers.items():
            comparison[broker_id] = {
                "name": broker_info["name"],
                "features": broker_info["features"],
                "best_for": self._get_broker_strengths(broker_id)
            }
        return comparison
    
    def _get_broker_strengths(self, broker: str) -> str:
        """Get what each broker is best for"""
        strengths = {
            "groww": "Beginners, Mutual Funds, Simple UI",
            "zerodha": "Active Traders, Low Cost, Advanced Tools", 
            "angel_one": "API Integration, Live Data, All-in-one",
            "upstox": "Professional Trading, Research, Charts",
            "iifl": "Full Service, Advisory, Research Reports",
            "paytm_money": "Digital Experience, Zero Delivery Charges"
        }
        return strengths.get(broker, "General investing")


# Global instance
broker_service = BrokerIntegrationService()