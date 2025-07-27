"""
Real Fi MCP Client using actual sample data structure
Uses the actual data structure from Fi Money MCP documentation
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class FinancialData:
    """Structured financial data container matching real Fi MCP format"""
    net_worth: Dict[str, Any]
    credit_report: Optional[Dict[str, Any]]
    epf_details: Optional[Dict[str, Any]]
    bank_transactions: Optional[Dict[str, Any]] = None

class RealFiMCPClient:
    """Real Fi MCP Client that uses actual sample data"""
    
    def __init__(self):
        self.sample_data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'mcp-docs', 'sample_responses'
        )
        logger.info(f"🔗 Real Fi MCP Client initialized - Sample data path: {self.sample_data_path}")
    
    def _load_sample_data(self, filename: str) -> Dict[str, Any]:
        """Load sample data from MCP docs"""
        try:
            file_path = os.path.join(self.sample_data_path, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded sample data from {filename}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load {filename}: {e}")
            return {}
    
    async def fetch_net_worth(self) -> Dict[str, Any]:
        """Fetch net worth data using actual Fi MCP structure"""
        return self._load_sample_data('fetch_net_worth.json')
    
    async def fetch_credit_report(self) -> Dict[str, Any]:
        """Fetch credit report using actual Fi MCP structure"""
        return self._load_sample_data('fetch_credit_report.json')
    
    async def fetch_epf_details(self) -> Dict[str, Any]:
        """Fetch EPF details using actual Fi MCP structure"""
        return self._load_sample_data('fetch_epf_details.json')
    
    async def fetch_mf_transactions(self) -> Dict[str, Any]:
        """Fetch mutual fund transactions using actual Fi MCP structure"""
        return self._load_sample_data('fetch_mf_transactions.json')
    
    async def fetch_bank_transactions(self) -> Dict[str, Any]:
        """Fetch bank/credit card transactions using actual Fi MCP structure"""
        return self._load_sample_data('fetch_bank_transactions.json')

async def get_user_financial_data() -> FinancialData:
    """
    Get comprehensive user financial data using real Fi MCP structure
    Returns actual data structure from Fi Money platform
    """
    try:
        client = RealFiMCPClient()
        
        # Fetch all data types in parallel
        net_worth_task = client.fetch_net_worth()
        credit_report_task = client.fetch_credit_report()
        epf_details_task = client.fetch_epf_details()
        bank_transactions_task = client.fetch_bank_transactions()
        
        # Wait for all data
        net_worth, credit_report, epf_details, bank_transactions = await asyncio.gather(
            net_worth_task,
            credit_report_task, 
            epf_details_task,
            bank_transactions_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(net_worth, Exception):
            logger.error(f"Net worth fetch failed: {net_worth}")
            net_worth = {}
            
        if isinstance(credit_report, Exception):
            logger.error(f"Credit report fetch failed: {credit_report}")
            credit_report = None
            
        if isinstance(epf_details, Exception):
            logger.error(f"EPF details fetch failed: {epf_details}")
            epf_details = None
            
        if isinstance(bank_transactions, Exception):
            logger.error(f"Bank transactions fetch failed: {bank_transactions}")
            bank_transactions = None
        
        financial_data = FinancialData(
            net_worth=net_worth,
            credit_report=credit_report,
            epf_details=epf_details,
            bank_transactions=bank_transactions
        )
        
        logger.info("💰 Successfully fetched real Fi MCP financial data")
        return financial_data
        
    except Exception as e:
        logger.error(f"Failed to fetch financial data: {e}")
        # Return empty structure on failure
        return FinancialData(
            net_worth={},
            credit_report=None,
            epf_details=None,
            bank_transactions=None
        )

def parse_currency_value(currency_obj: Dict[str, Any]) -> float:
    """Parse Fi MCP currency format to float value"""
    try:
        units = float(currency_obj.get('units', '0'))
        nanos = currency_obj.get('nanos', 0)
        return units + (nanos / 1_000_000_000)
    except (ValueError, TypeError):
        return 0.0

def format_currency(amount: float) -> str:
    """Format currency for display"""
    if amount >= 10_000_000:  # 1 Cr+
        return f"₹{amount/10_000_000:.1f}Cr"
    elif amount >= 100_000:  # 1L+
        return f"₹{amount/100_000:.1f}L"
    elif amount >= 1_000:  # 1K+
        return f"₹{amount/1_000:.1f}K"
    else:
        return f"₹{amount:.0f}"

def get_portfolio_summary(financial_data: FinancialData) -> Dict[str, Any]:
    """Extract key portfolio metrics from real Fi MCP data"""
    try:
        net_worth_data = financial_data.net_worth
        
        if not net_worth_data or 'netWorthResponse' not in net_worth_data:
            return {"error": "No net worth data available"}
        
        nw_response = net_worth_data['netWorthResponse']
        
        # Total net worth
        total_net_worth = parse_currency_value(nw_response.get('totalNetWorthValue', {}))
        
        # Asset breakdown
        assets = {}
        for asset in nw_response.get('assetValues', []):
            asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '')
            asset_value = parse_currency_value(asset.get('value', {}))
            assets[asset_type] = asset_value
        
        # Liability breakdown  
        liabilities = {}
        total_debt = 0
        for liability in nw_response.get('liabilityValues', []):
            liability_type = liability.get('netWorthAttribute', '').replace('LIABILITY_TYPE_', '')
            liability_value = parse_currency_value(liability.get('value', {}))
            liabilities[liability_type] = liability_value
            total_debt += liability_value
        
        # Mutual fund details
        mutual_funds = []
        mf_data = net_worth_data.get('mfSchemeAnalytics', {})
        for scheme in mf_data.get('schemeAnalytics', []):
            scheme_detail = scheme.get('schemeDetail', {})
            analytics = scheme.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
            
            fund_info = {
                'name': scheme_detail.get('nameData', {}).get('longName', 'Unknown Fund'),
                'amc': scheme_detail.get('amc', '').replace('_', ' '),
                'asset_class': scheme_detail.get('assetClass', ''),
                'risk_level': scheme_detail.get('fundhouseDefinedRiskLevel', ''),
                'current_value': parse_currency_value(analytics.get('currentValue', {})),
                'invested_value': parse_currency_value(analytics.get('investedValue', {})),
                'xirr': analytics.get('XIRR', 0),
                'absolute_returns': parse_currency_value(analytics.get('absoluteReturns', {})),
            }
            mutual_funds.append(fund_info)
        
        # Bank accounts
        bank_accounts = []
        account_details = net_worth_data.get('accountDetailsBulkResponse', {}).get('accountDetailsMap', {})
        
        for account_id, account_info in account_details.items():
            if 'depositSummary' in account_info:
                deposit_info = account_info['depositSummary']
                account_data = account_info['accountDetails']
                
                bank_account = {
                    'bank': account_data.get('fipMeta', {}).get('displayName', 'Unknown Bank'),
                    'account_type': deposit_info.get('depositAccountType', '').replace('DEPOSIT_ACCOUNT_TYPE_', ''),
                    'balance': parse_currency_value(deposit_info.get('currentBalance', {})),
                    'masked_number': account_data.get('maskedAccountNumber', '')
                }
                bank_accounts.append(bank_account)
        
        # Credit score
        credit_score = None
        if financial_data.credit_report and 'creditReports' in financial_data.credit_report:
            reports = financial_data.credit_report['creditReports']
            if reports and len(reports) > 0:
                credit_score = reports[0].get('creditReportData', {}).get('score', {}).get('bureauScore')
        
        return {
            'total_net_worth': total_net_worth,
            'total_net_worth_formatted': format_currency(total_net_worth),
            'assets': assets,
            'liabilities': liabilities,
            'total_debt': total_debt,
            'total_debt_formatted': format_currency(total_debt),
            'mutual_funds': mutual_funds,
            'bank_accounts': bank_accounts,
            'credit_score': credit_score,
            'liquid_funds': assets.get('SAVINGS_ACCOUNTS', 0),
            'liquid_funds_formatted': format_currency(assets.get('SAVINGS_ACCOUNTS', 0)),
            'investments': assets.get('MUTUAL_FUND', 0) + assets.get('INDIAN_SECURITIES', 0),
            'epf_balance': assets.get('EPF', 0),
            'epf_balance_formatted': format_currency(assets.get('EPF', 0))
        }
        
    except Exception as e:
        logger.error(f"Error parsing portfolio summary: {e}")
        return {"error": str(e)}