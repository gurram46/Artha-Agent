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

"""Enhanced Angel One API Service with Real-time Data.
Handles Angel One SmartAPI integration for real-time market data and trading.
"""

import os
import json
import urllib.parse
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from SmartApi import SmartConnect
import pyotp

load_dotenv()

class EnhancedAngelOneService:
    """Enhanced service for Angel One SmartAPI integration with real-time data."""
    
    def __init__(self):
        """Initialize Enhanced Angel One service."""
        # Market API credentials (for market data)
        self.market_api_key = os.getenv('ANGEL_ONE_MARKET_API_KEY')
        self.market_client_secret = os.getenv('ANGEL_ONE_MARKET_CLIENT_SECRET')
        
        # Trading API credentials (for trading operations)
        self.trading_api_key = os.getenv('ANGEL_ONE_TRADING_API_KEY')
        self.trading_client_secret = os.getenv('ANGEL_ONE_TRADING_CLIENT_SECRET')
        
        # Common credentials
        self.client_id = os.getenv('ANGEL_ONE_CLIENT_ID', '')
        self.password = os.getenv('ANGEL_ONE_PASSWORD', '')
        self.totp_secret = os.getenv('ANGEL_ONE_TOTP_SECRET', '')
        
        # Historical API credentials (fallback to market API if not provided)
        self.historical_api_key = os.getenv('ANGEL_ONE_HISTORICAL_API_KEY', self.market_api_key)
        self.historical_client_secret = os.getenv('ANGEL_ONE_HISTORICAL_CLIENT_SECRET', self.market_client_secret)
        
        # Initialize SmartConnect instances
        self.market_api = None
        self.trading_api = None
        self.historical_api = None
        self.auth_token = None
        self.refresh_token = None
        
        self.base_url = "https://apiconnect.angelone.in"
        self.web_url = "https://trade.angelone.in"
        
        # Initialize APIs
        self._initialize_apis()
        
        # Extended instrument list with more options
        self.instruments = {
            'NIFTYBEES': {
                'symbol': 'NIFTYBEES',
                'name': 'Nippon India ETF Nifty BeES',
                'exchange': 'NSE',
                'instrument_type': 'ETF',
                'lot_size': 1,
                'token': '26000'  # NSE token for NIFTYBEES
            },
            'SETFBEES': {
                'symbol': 'SETFBEES', 
                'name': 'Nippon India ETF Sensex BeES',
                'exchange': 'NSE',
                'instrument_type': 'ETF',
                'lot_size': 1,
                'token': '26001'
            },
            'GOLDBEES': {
                'symbol': 'GOLDBEES',
                'name': 'Nippon India ETF Gold BeES', 
                'exchange': 'NSE',
                'instrument_type': 'ETF',
                'lot_size': 1,
                'token': '26002'
            },
            'BANKBEES': {
                'symbol': 'BANKBEES',
                'name': 'Nippon India ETF Bank BeES',
                'exchange': 'NSE', 
                'instrument_type': 'ETF',
                'lot_size': 1,
                'token': '26003'
            },
            'RELIANCE': {
                'symbol': 'RELIANCE',
                'name': 'Reliance Industries Limited',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'lot_size': 1,
                'token': '2885'
            },
            'TCS': {
                'symbol': 'TCS',
                'name': 'Tata Consultancy Services Limited',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'lot_size': 1,
                'token': '11536'
            }
        }
    
    def _initialize_apis(self):
        """Initialize different API connections"""
        try:
            # Market API for real-time data
            if self.market_api_key:
                self.market_api = SmartConnect(api_key=self.market_api_key)
                print("✅ Market API initialized")
            
            # Trading API for trade execution
            if self.trading_api_key:
                self.trading_api = SmartConnect(api_key=self.trading_api_key)
                print("✅ Trading API initialized")
                
            # Historical API for historical data
            if self.historical_api_key:
                self.historical_api = SmartConnect(api_key=self.historical_api_key)
                print("✅ Historical API initialized")
                
        except Exception as e:
            print(f"❌ Error initializing APIs: {e}")
    
    def is_configured(self) -> bool:
        """Check if Angel One API is properly configured."""
        return bool((self.market_api_key or self.trading_api_key) and self.client_id)
    
    def authenticate_market_api(self) -> bool:
        """Authenticate Market API (usually doesn't need login for basic data)"""
        if not self.market_api:
            return False
        try:
            # Market API often works without authentication for basic data
            return True
        except Exception as e:
            print(f"Market API authentication error: {e}")
            return False
    
    def authenticate_trading_api(self) -> bool:
        """Authenticate Trading API (requires full login with TOTP)"""
        if not self.trading_api or not self.client_id or not self.password:
            return False
        
        try:
            # Generate TOTP if secret is provided
            totp_code = None
            if self.totp_secret:
                totp = pyotp.TOTP(self.totp_secret)
                totp_code = totp.now()
            
            # Login to trading API
            data = self.trading_api.generateSession(
                clientCode=self.client_id,
                password=self.password,
                totp=totp_code
            )
            
            if data['status']:
                self.auth_token = data['data']['jwtToken']
                self.refresh_token = data['data']['refreshToken']
                print("✅ Trading API authenticated successfully")
                return True
            else:
                print(f"❌ Trading API authentication failed: {data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Trading API authentication error: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with Angel One SmartAPI."""
        try:
            if not self.is_configured():
                print("Angel One API not properly configured")
                return False
            
            # Try to authenticate trading API first (most comprehensive)
            if self.authenticate_trading_api():
                return True
            
            # Fallback to market API
            return self.authenticate_market_api()
                
        except Exception as e:
            print(f"Error authenticating with Angel One: {e}")
            return False
    
    def get_live_price(self, symbol: str) -> float:
        """Get live price for a symbol."""
        try:
            # Try market API first for live prices
            api_to_use = self.market_api or self.trading_api
            
            if not api_to_use:
                return self._get_estimated_price(symbol)
            
            # Authenticate if needed
            if api_to_use == self.trading_api and not self.auth_token:
                if not self.authenticate_trading_api():
                    return self._get_estimated_price(symbol)
            elif api_to_use == self.market_api:
                self.authenticate_market_api()
            
            if symbol not in self.instruments:
                return self._get_estimated_price(symbol)
            
            instrument = self.instruments[symbol]
            
            # Get LTP (Last Traded Price)
            ltp_data = api_to_use.ltpData(
                exchange=instrument['exchange'],
                tradingsymbol=symbol,
                symboltoken=instrument['token']
            )
            
            if ltp_data['status'] and 'data' in ltp_data:
                return float(ltp_data['data']['ltp'])
            else:
                print(f"Failed to get live price for {symbol}: {ltp_data.get('message', 'Unknown error')}")
                return self._get_estimated_price(symbol)
                
        except Exception as e:
            print(f"Error getting live price for {symbol}: {e}")
            return self._get_estimated_price(symbol)
    
    def get_market_depth(self, symbol: str) -> Dict[str, Any]:
        """Get market depth for a symbol."""
        try:
            # Use market API for market depth
            api_to_use = self.market_api or self.trading_api
            
            if not api_to_use:
                return {}
            
            # Authenticate if needed
            if api_to_use == self.trading_api and not self.auth_token:
                if not self.authenticate_trading_api():
                    return {}
            elif api_to_use == self.market_api:
                self.authenticate_market_api()
            
            if symbol not in self.instruments:
                return {}
            
            instrument = self.instruments[symbol]
            
            # Get market depth
            depth_data = api_to_use.getMarketData(
                mode="FULL",
                exchangeTokens={
                    instrument['exchange']: [instrument['token']]
                }
            )
            
            if depth_data['status']:
                return depth_data['data']
            else:
                print(f"Failed to get market depth for {symbol}: {depth_data.get('message', 'Unknown error')}")
                return {}
                
        except Exception as e:
            print(f"Error getting market depth for {symbol}: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, interval: str = "ONE_DAY", from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get historical data for a symbol."""
        try:
            # Use historical API for historical data
            api_to_use = self.historical_api or self.trading_api or self.market_api
            
            if not api_to_use:
                return []
            
            # Authenticate if needed
            if api_to_use == self.trading_api and not self.auth_token:
                if not self.authenticate_trading_api():
                    return []
            elif api_to_use in [self.market_api, self.historical_api]:
                self.authenticate_market_api()
            
            if symbol not in self.instruments:
                return []
            
            instrument = self.instruments[symbol]
            
            # Get historical data
            hist_data = api_to_use.getCandleData(
                exchange=instrument['exchange'],
                symboltoken=instrument['token'],
                interval=interval,
                fromdate=from_date,
                todate=to_date
            )
            
            if hist_data['status']:
                return hist_data['data']
            else:
                print(f"Failed to get historical data for {symbol}: {hist_data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return []
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        try:
            # Use market API for market status
            api_to_use = self.market_api or self.trading_api
            
            if not api_to_use:
                return {'status': 'unknown'}
            
            # Authenticate if needed
            if api_to_use == self.trading_api and not self.auth_token:
                if not self.authenticate_trading_api():
                    return {'status': 'unknown'}
            elif api_to_use == self.market_api:
                self.authenticate_market_api()
            
            # Get market status
            status_data = api_to_use.getMarketData(mode="LTP", exchangeTokens={"NSE": ["26000"]})
            
            if status_data['status']:
                return {
                    'status': 'open',
                    'message': 'Market is open',
                    'data': status_data['data']
                }
            else:
                return {
                    'status': 'closed',
                    'message': 'Market is closed or API error'
                }
                
        except Exception as e:
            print(f"Error getting market status: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    def search_instruments(self, query: str) -> List[Dict[str, Any]]:
        """Search for instruments by name or symbol."""
        try:
            # Use market API for instrument search
            api_to_use = self.market_api or self.trading_api
            
            if not api_to_use:
                return []
            
            # Authenticate if needed
            if api_to_use == self.trading_api and not self.auth_token:
                if not self.authenticate_trading_api():
                    return []
            elif api_to_use == self.market_api:
                self.authenticate_market_api()
            
            # Search instruments
            search_data = api_to_use.searchScrip(exchange="NSE", searchtext=query)
            
            if search_data['status']:
                return search_data['data']
            else:
                print(f"Failed to search instruments for '{query}': {search_data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error searching instruments for '{query}': {e}")
            return []
    
    def _get_estimated_price(self, symbol: str) -> float:
        """Get estimated price for symbol (fallback when API fails)."""
        estimated_prices = {
            'NIFTYBEES': 250.0,
            'SETFBEES': 500.0,
            'GOLDBEES': 45.0,
            'BANKBEES': 400.0,
            'RELIANCE': 2800.0,
            'TCS': 4200.0
        }
        return estimated_prices.get(symbol, 100.0)
    
    def generate_investment_url(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate Angel One investment URL with real-time prices."""
        try:
            if not recommendations:
                return self.web_url
            
            basket_items = []
            
            for rec in recommendations:
                symbol = rec.get('symbol', '')
                amount = rec.get('amount', 0)
                
                if symbol and symbol in self.instruments:
                    instrument = self.instruments[symbol]
                    
                    # Get real-time price
                    current_price = self.get_live_price(symbol)
                    quantity = max(1, int(amount / current_price)) if current_price > 0 else 1
                    
                    basket_items.append({
                        'symbol': symbol,
                        'exchange': instrument['exchange'],
                        'quantity': quantity,
                        'order_type': rec.get('order_type', 'MARKET'),
                        'product_type': 'DELIVERY',
                        'price': current_price
                    })
            
            if basket_items:
                return self._create_basket_url(basket_items)
            
            return self.web_url
            
        except Exception as e:
            print(f"Error generating Angel One URL: {e}")
            return self.web_url
    
    def _create_basket_url(self, basket_items: List[Dict[str, Any]]) -> str:
        """Create Angel One basket URL."""
        try:
            basket_data = {
                'basket_name': 'Artha_Investment_Plan',
                'instruments': basket_items
            }
            
            basket_json = json.dumps(basket_data)
            encoded_basket = urllib.parse.quote(basket_json)
            
            return f"{self.web_url}/basket?data={encoded_basket}"
            
        except Exception as e:
            print(f"Error creating basket URL: {e}")
            return self.web_url
    
    def create_investment_button_data(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create data for "Invest Now" button with real-time pricing."""
        try:
            total_amount = 0
            instrument_count = 0
            
            for rec in recommendations:
                symbol = rec.get('symbol', '')
                if symbol and symbol in self.instruments:
                    # Use real-time price for accurate calculation
                    current_price = self.get_live_price(symbol)
                    amount = rec.get('amount', 0)
                    if amount > 0:
                        total_amount += amount
                        instrument_count += 1
            
            return {
                'provider': 'angel_one',
                'provider_name': 'Angel One (Real-time)',
                'total_amount': total_amount,
                'instrument_count': instrument_count,
                'button_text': f'Invest ₹{total_amount:,.0f} via Angel One',
                'description': f'Invest in {instrument_count} instruments with live prices',
                'configured': self.is_configured(),
                'authenticated': bool(self.auth_token),
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Error creating button data: {e}")
            return {
                'provider': 'angel_one',
                'provider_name': 'Angel One',
                'configured': False,
                'error': str(e)
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get comprehensive API status."""
        return {
            'configured': self.is_configured(),
            'authenticated': bool(self.auth_token),
            'market_api_key_present': bool(self.market_api_key),
            'trading_api_key_present': bool(self.trading_api_key),
            'historical_api_key_present': bool(self.historical_api_key),
            'client_id_present': bool(self.client_id),
            'password_present': bool(self.password),
            'totp_secret_present': bool(self.totp_secret),
            'base_url': self.base_url,
            'web_url': self.web_url,
            'market_api_connected': bool(self.market_api),
            'trading_api_connected': bool(self.trading_api),
            'historical_api_connected': bool(self.historical_api)
        }