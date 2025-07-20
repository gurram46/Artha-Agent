"""
Data Loader for MCP Sample Responses
Loads and processes financial data from sample response files
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class DataLoader:
    """Loads financial data from MCP sample response files"""
    
    def __init__(self, data_path: str = "../mcp-docs/sample_responses/"):
        self.data_path = Path(data_path)
        self.cached_data = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all sample data files on initialization"""
        try:
            # Load credit report data
            credit_file = self.data_path / "fetch_credit_report.json"
            if credit_file.exists():
                with open(credit_file, 'r') as f:
                    self.cached_data['credit_report'] = json.load(f)
            
            # Load net worth data
            networth_file = self.data_path / "fetch_net_worth.json"
            if networth_file.exists():
                with open(networth_file, 'r') as f:
                    self.cached_data['net_worth'] = json.load(f)
            
            # Load EPF details
            epf_file = self.data_path / "fetch_epf_details.json"
            if epf_file.exists():
                with open(epf_file, 'r') as f:
                    self.cached_data['epf_details'] = json.load(f)
            
            # Load MF transactions
            mf_file = self.data_path / "fetch_mf_transactions.json"
            if mf_file.exists():
                with open(mf_file, 'r') as f:
                    self.cached_data['mf_transactions'] = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data files: {e}")
            self.cached_data = {}
    
    def get_credit_report(self, user_id: str = "demo") -> Dict[str, Any]:
        """Get credit report data"""
        return self.cached_data.get('credit_report', {})
    
    def get_net_worth_data(self, user_id: str = "demo") -> Dict[str, Any]:
        """Get net worth and portfolio data"""
        return self.cached_data.get('net_worth', {})
    
    def get_epf_details(self, user_id: str = "demo") -> Dict[str, Any]:
        """Get EPF details"""
        return self.cached_data.get('epf_details', {})
    
    def get_mf_transactions(self, user_id: str = "demo") -> Dict[str, Any]:
        """Get mutual fund transactions"""
        return self.cached_data.get('mf_transactions', {})
    
    def get_user_financial_data(self, user_id: str = "demo") -> Dict[str, Any]:
        """Get complete financial profile for user"""
        return {
            'user_id': user_id,
            'credit_report': self.get_credit_report(user_id),
            'net_worth': self.get_net_worth_data(user_id),
            'epf_details': self.get_epf_details(user_id),
            'mf_transactions': self.get_mf_transactions(user_id),
            'timestamp': self._get_current_timestamp()
        }
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get market data (simulated from portfolio data)"""
        net_worth = self.get_net_worth_data()
        
        # Extract market insights from portfolio data
        market_insights = {
            'equity_performance': self._analyze_equity_performance(net_worth),
            'mutual_fund_trends': self._analyze_mf_trends(net_worth),
            'sector_allocation': self._get_sector_allocation(net_worth),
            'risk_metrics': self._calculate_risk_metrics(net_worth)
        }
        
        return market_insights
    
    def _analyze_equity_performance(self, net_worth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze equity performance from net worth data"""
        try:
            equity_data = net_worth_data.get('accountDetailsBulkResponse', {}).get('accountDetailsMap', {})
            equity_accounts = [acc for acc in equity_data.values() if 
                             acc.get('accountDetails', {}).get('accInstrumentType') == 'ACC_INSTRUMENT_TYPE_EQUITIES']
            
            total_equity_value = sum(
                float(acc.get('equitySummary', {}).get('currentValue', {}).get('units', 0))
                for acc in equity_accounts
            )
            
            return {
                'total_value': total_equity_value,
                'account_count': len(equity_accounts),
                'performance': 'positive' if total_equity_value > 20000 else 'negative'
            }
        except:
            return {'total_value': 0, 'account_count': 0, 'performance': 'neutral'}
    
    def _analyze_mf_trends(self, net_worth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mutual fund trends"""
        try:
            mf_data = net_worth_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
            
            total_current_value = sum(
                float(scheme.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                     .get('currentValue', {}).get('units', 0))
                for scheme in mf_data
            )
            
            positive_returns = [
                scheme for scheme in mf_data
                if scheme.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {}).get('XIRR', 0) > 0
            ]
            
            return {
                'total_schemes': len(mf_data),
                'total_value': total_current_value,
                'positive_performers': len(positive_returns),
                'performance_ratio': len(positive_returns) / len(mf_data) if mf_data else 0
            }
        except:
            return {'total_schemes': 0, 'total_value': 0, 'positive_performers': 0, 'performance_ratio': 0}
    
    def _get_sector_allocation(self, net_worth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get sector allocation from portfolio"""
        try:
            mf_data = net_worth_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
            
            sectors = {}
            for scheme in mf_data:
                asset_class = scheme.get('schemeDetail', {}).get('assetClass', 'OTHER')
                current_value = float(scheme.get('enrichedAnalytics', {}).get('analytics', {})
                                   .get('schemeDetails', {}).get('currentValue', {}).get('units', 0))
                
                if asset_class in sectors:
                    sectors[asset_class] += current_value
                else:
                    sectors[asset_class] = current_value
            
            return sectors
        except:
            return {}
    
    def _calculate_risk_metrics(self, net_worth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic risk metrics"""
        try:
            assets = net_worth_data.get('netWorthResponse', {}).get('assetValues', [])
            liabilities = net_worth_data.get('netWorthResponse', {}).get('liabilityValues', [])
            
            total_assets = sum(float(asset.get('value', {}).get('units', 0)) for asset in assets)
            total_liabilities = sum(float(liability.get('value', {}).get('units', 0)) for liability in liabilities)
            
            debt_to_asset_ratio = total_liabilities / total_assets if total_assets > 0 else 0
            
            risk_level = 'low' if debt_to_asset_ratio < 0.3 else 'medium' if debt_to_asset_ratio < 0.7 else 'high'
            
            return {
                'debt_to_asset_ratio': debt_to_asset_ratio,
                'risk_level': risk_level,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities
            }
        except:
            return {'debt_to_asset_ratio': 0, 'risk_level': 'unknown', 'total_assets': 0, 'total_liabilities': 0}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def is_data_available(self) -> bool:
        """Check if data is available"""
        return len(self.cached_data) > 0
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data"""
        return {
            'available_datasets': list(self.cached_data.keys()),
            'total_files': len(self.cached_data),
            'data_path': str(self.data_path),
            'last_loaded': self._get_current_timestamp()
        }