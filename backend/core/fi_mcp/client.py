"""
Fi MCP Client for Dynamic Financial Data Fetching
Integrates with Fi Money's Model Context Protocol to fetch real user financial data
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
# Mock imports for demo - commented out actual MCP imports
# from mcp.client.streamable_http import streamablehttp_client
# from mcp.client.session import ClientSession
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import config

logger = logging.getLogger(__name__)

@dataclass
class FinancialData:
    """Structured financial data container"""
    net_worth: Dict[str, Any]
    mutual_funds: List[Dict[str, Any]]
    bank_accounts: List[Dict[str, Any]] 
    equity_holdings: List[Dict[str, Any]]
    credit_report: Optional[Dict[str, Any]]
    epf_details: Optional[Dict[str, Any]]
    mf_transactions: List[Dict[str, Any]]
    bank_transactions: List[Dict[str, Any]]
    stock_transactions: List[Dict[str, Any]]
    
    def get_total_assets(self) -> float:
        """Calculate total assets value"""
        if not self.net_worth or 'totalNetWorthValue' not in self.net_worth:
            return 0.0
        return float(self.net_worth['totalNetWorthValue']['units'])
    
    def get_asset_allocation(self) -> Dict[str, float]:
        """Get asset allocation breakdown"""
        allocation = {}
        if not self.net_worth or 'assetValues' not in self.net_worth:
            return allocation
            
        for asset in self.net_worth['assetValues']:
            asset_type = asset['netWorthAttribute']
            value = float(asset['value']['units'])
            allocation[asset_type] = value
            
        return allocation
    
    def get_liability_breakdown(self) -> Dict[str, float]:
        """Get liability breakdown"""
        liabilities = {}
        if not self.net_worth or 'liabilityValues' not in self.net_worth:
            return liabilities
            
        for liability in self.net_worth['liabilityValues']:
            liability_type = liability['netWorthAttribute'] 
            value = float(liability['value']['units'])
            liabilities[liability_type] = value
            
        return liabilities

class FiMCPClient:
    """Fi MCP Client for financial data access"""
    
    def __init__(self, mcp_url: str = None, auth_token: str = None):
        self.mcp_url = mcp_url or config.FI_MCP_URL
        self.auth_token = auth_token or config.FI_MCP_AUTH_TOKEN
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Establish connection to Fi MCP"""
        try:
            self.stream_client = streamablehttp_client(self.mcp_url)
            read_stream, write_stream, _ = await self.stream_client.__aenter__()
            
            self.session = ClientSession(read_stream, write_stream)
            await self.session.__aenter__()
            await self.session.initialize()
            
            logger.info("Successfully connected to Fi MCP")
            
        except Exception as e:
            logger.error(f"Failed to connect to Fi MCP: {e}")
            raise
            
    async def disconnect(self):
        """Disconnect from Fi MCP"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if hasattr(self, 'stream_client'):
                await self.stream_client.__aexit__(None, None, None)
                
            logger.info("Disconnected from Fi MCP")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def fetch_net_worth(self) -> Dict[str, Any]:
        """Fetch complete net worth data"""
        try:
            result = await self.session.call_tool('fetch_net_worth', {})
            return result.content[0].text if result.content else {}
            
        except Exception as e:
            logger.error(f"Failed to fetch net worth: {e}")
            return {}
    
    async def fetch_credit_report(self) -> Dict[str, Any]:
        """Fetch credit report data"""
        try:
            result = await self.session.call_tool('fetch_credit_report', {})
            return result.content[0].text if result.content else {}
            
        except Exception as e:
            logger.error(f"Failed to fetch credit report: {e}")
            return {}
    
    async def fetch_epf_details(self) -> Dict[str, Any]:
        """Fetch EPF account details"""
        try:
            result = await self.session.call_tool('fetch_epf_details', {})
            return result.content[0].text if result.content else {}
            
        except Exception as e:
            logger.error(f"Failed to fetch EPF details: {e}")
            return {}
    
    async def fetch_mf_transactions(self) -> Dict[str, Any]:
        """Fetch mutual fund transactions"""
        try:
            result = await self.session.call_tool('fetch_mf_transactions', {})
            return result.content[0].text if result.content else {}
            
        except Exception as e:
            logger.error(f"Failed to fetch MF transactions: {e}")
            return {}
    
    async def fetch_bank_transactions(self) -> Dict[str, Any]:
        """Fetch bank transactions"""
        try:
            result = await self.session.call_tool('fetch_bank_transactions', {})
            return result.content[0].text if result.content else {}
            
        except Exception as e:
            logger.error(f"Failed to fetch bank transactions: {e}")
            return {}
    
    async def fetch_stock_transactions(self) -> Dict[str, Any]:
        """Fetch stock transactions"""
        try:
            result = await self.session.call_tool('fetch_stock_transactions', {})
            return result.content[0].text if result.content else {}
            
        except Exception as e:
            logger.error(f"Failed to fetch stock transactions: {e}")
            return {}
    
    async def fetch_all_financial_data(self) -> FinancialData:
        """Fetch all available financial data"""
        logger.info("Fetching comprehensive financial data from Fi MCP...")
        
        # Fetch all data concurrently
        tasks = [
            self.fetch_net_worth(),
            self.fetch_credit_report(), 
            self.fetch_epf_details(),
            self.fetch_mf_transactions(),
            self.fetch_bank_transactions(),
            self.fetch_stock_transactions()
        ]
        
        net_worth_data, credit_data, epf_data, mf_transaction_data, bank_transaction_data, stock_transaction_data = await asyncio.gather(*tasks)
        
        # Parse net worth data to extract components
        net_worth = json.loads(net_worth_data) if isinstance(net_worth_data, str) else net_worth_data
        
        mutual_funds = []
        bank_accounts = []
        equity_holdings = []
        
        if 'mfSchemeAnalytics' in net_worth:
            mutual_funds = net_worth['mfSchemeAnalytics'].get('schemeAnalytics', [])
            
        if 'accountDetailsBulkResponse' in net_worth:
            account_map = net_worth['accountDetailsBulkResponse'].get('accountDetailsMap', {})
            
            for account_id, account_info in account_map.items():
                account_details = account_info.get('accountDetails', {})
                
                # Categorize accounts
                if 'depositSummary' in account_info:
                    bank_accounts.append({
                        'id': account_id,
                        'details': account_details,
                        'summary': account_info['depositSummary']
                    })
                elif 'equitySummary' in account_info:
                    equity_holdings.append({
                        'id': account_id, 
                        'details': account_details,
                        'holdings': account_info['equitySummary']
                    })
        
        # Parse transactions
        mf_transactions = []
        bank_transactions = []
        stock_transactions = []
        
        if mf_transaction_data:
            mf_tx_data = json.loads(mf_transaction_data) if isinstance(mf_transaction_data, str) else mf_transaction_data
            mf_transactions = mf_tx_data.get('transactions', [])
            
        if bank_transaction_data:
            bank_tx_data = json.loads(bank_transaction_data) if isinstance(bank_transaction_data, str) else bank_transaction_data
            bank_transactions = bank_tx_data.get('transactions', [])
            
        if stock_transaction_data:
            stock_tx_data = json.loads(stock_transaction_data) if isinstance(stock_transaction_data, str) else stock_transaction_data
            stock_transactions = stock_tx_data.get('transactions', [])
        
        return FinancialData(
            net_worth=net_worth.get('netWorthResponse', {}),
            mutual_funds=mutual_funds,
            bank_accounts=bank_accounts,
            equity_holdings=equity_holdings,
            credit_report=json.loads(credit_data) if credit_data else None,
            epf_details=json.loads(epf_data) if epf_data else None,
            mf_transactions=mf_transactions,
            bank_transactions=bank_transactions,
            stock_transactions=stock_transactions
        )

async def get_user_financial_data() -> FinancialData:
    """Dynamically fetch real Fi MCP sample data from /mcp-docs/ files"""
    logger.info("Loading real Fi MCP sample data from /mcp-docs/ files...")
    
    try:
        # Construct file paths dynamically 
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "mcp-docs", "sample_responses"
        )
        
        # Load net worth data from actual sample file
        net_worth_file = os.path.join(base_path, "fetch_net_worth.json")
        with open(net_worth_file, 'r') as f:
            net_worth_data = json.load(f)
            logger.info(f"✅ Loaded net worth data from: {net_worth_file}")
        
        # Load EPF data from actual sample file
        epf_file = os.path.join(base_path, "fetch_epf_details.json") 
        epf_data = None
        try:
            with open(epf_file, 'r') as f:
                epf_data = json.load(f)
                logger.info(f"✅ Loaded EPF data from: {epf_file}")
        except FileNotFoundError:
            logger.warning(f"EPF file not found: {epf_file}")
        
        # Load credit report from actual sample file
        credit_file = os.path.join(base_path, "fetch_credit_report.json")
        credit_data = None
        try:
            with open(credit_file, 'r') as f:
                credit_data = json.load(f)
                logger.info(f"✅ Loaded credit data from: {credit_file}")
        except FileNotFoundError:
            logger.warning(f"Credit file not found: {credit_file}")
        
        # Load MF transactions from actual sample file
        mf_file = os.path.join(base_path, "fetch_mf_transactions.json")
        mf_transactions = []
        try:
            with open(mf_file, 'r') as f:
                mf_data = json.load(f)
                mf_transactions = mf_data.get('transactions', [])
                logger.info(f"✅ Loaded MF transactions from: {mf_file}")
        except FileNotFoundError:
            logger.warning(f"MF transactions file not found: {mf_file}")
        
        # Load bank transactions from actual sample file
        bank_file = os.path.join(base_path, "fetch_bank_transactions.json")
        bank_transactions = []
        try:
            with open(bank_file, 'r') as f:
                bank_data = json.load(f)
                bank_transactions = bank_data.get('transactions', [])
                logger.info(f"✅ Loaded bank transactions from: {bank_file}")
        except FileNotFoundError:
            logger.warning(f"Bank transactions file not found: {bank_file}")
        
        # Load stock transactions from actual sample file
        stock_file = os.path.join(base_path, "fetch_stock_transactions.json")
        stock_transactions = []
        try:
            with open(stock_file, 'r') as f:
                stock_data = json.load(f)
                stock_transactions = stock_data.get('transactions', [])
                logger.info(f"✅ Loaded stock transactions from: {stock_file}")
        except FileNotFoundError:
            logger.warning(f"Stock transactions file not found: {stock_file}")
        
        # Extract structured data from the loaded files
        net_worth_response = net_worth_data.get('netWorthResponse', {})
        
        # Extract mutual funds from mfSchemeAnalytics
        mutual_funds = []
        if 'mfSchemeAnalytics' in net_worth_data:
            mutual_funds = net_worth_data['mfSchemeAnalytics'].get('schemeAnalytics', [])
        
        # Extract bank accounts from accountDetailsBulkResponse
        bank_accounts = []
        equity_holdings = []
        if 'accountDetailsBulkResponse' in net_worth_data:
            account_map = net_worth_data['accountDetailsBulkResponse'].get('accountDetailsMap', {})
            
            for account_id, account_info in account_map.items():
                if 'depositSummary' in account_info:
                    bank_accounts.append({
                        'id': account_id,
                        'details': account_info.get('accountDetails', {}),
                        'summary': account_info['depositSummary']
                    })
                elif 'equitySummary' in account_info:
                    equity_holdings.append({
                        'id': account_id,
                        'details': account_info.get('accountDetails', {}),
                        'holdings': account_info['equitySummary'] 
                    })
        
        # Log summary of loaded data
        total_net_worth = net_worth_response.get('totalNetWorthValue', {}).get('units', '0')
        asset_count = len(net_worth_response.get('assetValues', []))
        liability_count = len(net_worth_response.get('liabilityValues', []))
        
        logger.info(f"📊 Fi MCP Data Summary: Net Worth ₹{total_net_worth}, Assets: {asset_count}, Liabilities: {liability_count}, MF Schemes: {len(mutual_funds)}, Bank Accounts: {len(bank_accounts)}")
        
        return FinancialData(
            net_worth=net_worth_data,  # Full net worth response with all nested data
            mutual_funds=mutual_funds,
            bank_accounts=bank_accounts,
            equity_holdings=equity_holdings,
            credit_report=credit_data,
            epf_details=epf_data,
            mf_transactions=mf_transactions,
            bank_transactions=bank_transactions,
            stock_transactions=stock_transactions
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to load Fi MCP sample data: {e}")
        logger.error(f"Attempted base path: {base_path if 'base_path' in locals() else 'Unknown'}")
        
        # Return minimal fallback data instead of crashing
        return FinancialData(
            net_worth={
                'netWorthResponse': {
                    'totalNetWorthValue': {'currencyCode': 'INR', 'units': '0'},
                    'assetValues': [],
                    'liabilityValues': []
                }
            },
            mutual_funds=[],
            bank_accounts=[],
            equity_holdings=[],
            credit_report=None,
            epf_details=None,
            mf_transactions=[],
            bank_transactions=[],
            stock_transactions=[]
        )