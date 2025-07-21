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
    transactions: List[Dict[str, Any]]
    
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
    
    async def fetch_all_financial_data(self) -> FinancialData:
        """Fetch all available financial data"""
        logger.info("Fetching comprehensive financial data from Fi MCP...")
        
        # Fetch all data concurrently
        tasks = [
            self.fetch_net_worth(),
            self.fetch_credit_report(), 
            self.fetch_epf_details(),
            self.fetch_mf_transactions()
        ]
        
        net_worth_data, credit_data, epf_data, transaction_data = await asyncio.gather(*tasks)
        
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
        transactions = []
        if transaction_data:
            tx_data = json.loads(transaction_data) if isinstance(transaction_data, str) else transaction_data
            transactions = tx_data.get('transactions', [])
        
        return FinancialData(
            net_worth=net_worth.get('netWorthResponse', {}),
            mutual_funds=mutual_funds,
            bank_accounts=bank_accounts,
            equity_holdings=equity_holdings,
            credit_report=json.loads(credit_data) if credit_data else None,
            epf_details=json.loads(epf_data) if epf_data else None,
            transactions=transactions
        )

async def get_user_financial_data() -> FinancialData:
    """Demo function to get sample financial data"""
    # For demo purposes, return sample data
    
    sample_net_worth = {
        'totalNetWorthValue': {'currencyCode': 'INR', 'units': '868721'},
        'assetValues': [
            {'netWorthAttribute': 'ASSET_TYPE_MUTUAL_FUND', 'value': {'currencyCode': 'INR', 'units': '84613'}},
            {'netWorthAttribute': 'ASSET_TYPE_EPF', 'value': {'currencyCode': 'INR', 'units': '211111'}},
            {'netWorthAttribute': 'ASSET_TYPE_INDIAN_SECURITIES', 'value': {'currencyCode': 'INR', 'units': '200642'}},
            {'netWorthAttribute': 'ASSET_TYPE_SAVINGS_ACCOUNTS', 'value': {'currencyCode': 'INR', 'units': '436355'}}
        ],
        'liabilityValues': [
            {'netWorthAttribute': 'LIABILITY_TYPE_OTHER_LOAN', 'value': {'currencyCode': 'INR', 'units': '42000'}},
            {'netWorthAttribute': 'LIABILITY_TYPE_HOME_LOAN', 'value': {'currencyCode': 'INR', 'units': '17000'}},
            {'netWorthAttribute': 'LIABILITY_TYPE_VEHICLE_LOAN', 'value': {'currencyCode': 'INR', 'units': '5000'}}
        ]
    }
    
    sample_mf_data = [
        {
            'schemeDetail': {
                'amc': 'ICICI_PRUDENTIAL',
                'nameData': {'longName': 'ICICI Prudential Nifty 50 Index Fund'},
                'assetClass': 'EQUITY',
                'fundhouseDefinedRiskLevel': 'VERY_HIGH_RISK'
            },
            'enrichedAnalytics': {
                'analytics': {
                    'schemeDetails': {
                        'currentValue': {'currencyCode': 'INR', 'units': '20147'},
                        'XIRR': 23.28
                    }
                }
            }
        }
    ]
    
    sample_transactions = [
        {
            'schemeName': 'ICICI Prudential Nifty 50 Index Fund',
            'transactionDate': '2022-03-08T18:30:00Z',
            'transactionAmount': {'currencyCode': 'INR', 'units': '10027'},
            'externalOrderType': 'BUY'
        }
    ]
    
    return FinancialData(
        net_worth=sample_net_worth,
        mutual_funds=sample_mf_data,
        bank_accounts=[],
        equity_holdings=[],
        credit_report=None,
        epf_details=None,
        transactions=sample_transactions
    )