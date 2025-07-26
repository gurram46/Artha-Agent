"""
Local LLM Processor for Financial Data
Compresses real Fi Money MCP data to under 1K tokens for mobile/edge processing
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CompressedFinancialData:
    """Ultra-compressed financial data for local LLM processing"""
    net_worth: str
    assets: Dict[str, str]
    debt: Optional[str]
    credit_score: Optional[str]
    top_investments: List[Dict[str, str]]
    risk_profile: str
    liquid_ratio: str
    key_insights: List[str]
    
    def to_compact_text(self) -> str:
        """Convert to ultra-compact text format for minimal token usage"""
        parts = [f"NW:{self.net_worth}"]
        
        if self.assets:
            asset_str = ','.join([f"{k}:{v}" for k, v in self.assets.items()])
            parts.append(f"A:{asset_str}")
        
        if self.debt:
            parts.append(f"D:{self.debt}")
        
        if self.credit_score:
            parts.append(f"CS:{self.credit_score}")
        
        if self.top_investments:
            inv_str = ','.join([f"{inv['v']}" + (f"@{inv['r']}" if 'r' in inv else "") 
                               for inv in self.top_investments[:2]])
            parts.append(f"INV:{inv_str}")
        
        parts.append(f"RISK:{self.risk_profile}")
        parts.append(f"LIQ:{self.liquid_ratio}")
        
        return '|'.join(parts)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format for structured processing"""
        return {
            'nw': self.net_worth,
            'assets': self.assets,
            'debt': self.debt,
            'credit': self.credit_score,
            'investments': self.top_investments,
            'risk': self.risk_profile,
            'liquidity': self.liquid_ratio,
            'insights': self.key_insights
        }

class LocalLLMProcessor:
    """Process and compress financial data for local LLM inference"""
    
    @staticmethod
    def compress_amount(value: float) -> str:
        """Compress amount to shortest representation"""
        if value >= 10000000:  # 1 Cr+
            return f"{value/10000000:.1f}Cr"
        elif value >= 100000:  # 1L+
            return f"{int(value/100000)}L"
        elif value >= 1000:  # 1K+
            return f"{int(value/1000)}K"
        else:
            return str(int(value))
    
    @staticmethod
    def parse_currency_value(currency_obj: Dict[str, Any]) -> float:
        """Parse Fi MCP currency format to float"""
        try:
            units = float(currency_obj.get('units', '0'))
            nanos = currency_obj.get('nanos', 0)
            return units + (nanos / 1_000_000_000)
        except (ValueError, TypeError):
            return 0.0
    
    def compress_financial_data(self, financial_data: Any) -> CompressedFinancialData:
        """
        Compress real Fi Money MCP data to under 1K tokens
        Optimized for local LLM processing on mobile devices
        """
        try:
            # Extract net worth data
            net_worth_value = 0
            assets = {}
            total_debt = 0
            
            if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
                nw_response = financial_data.net_worth.get('netWorthResponse', {})
                
                # Total net worth
                total_nw = nw_response.get('totalNetWorthValue', {})
                net_worth_value = self.parse_currency_value(total_nw)
                
                # Assets breakdown
                for asset in nw_response.get('assetValues', []):
                    asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '')
                    asset_value = self.parse_currency_value(asset.get('value', {}))
                    
                    # Compress asset types
                    if asset_type == 'MUTUAL_FUND':
                        assets['mf'] = self.compress_amount(asset_value)
                    elif asset_type == 'EPF':
                        assets['epf'] = self.compress_amount(asset_value)
                    elif asset_type == 'INDIAN_SECURITIES':
                        assets['stock'] = self.compress_amount(asset_value)
                    elif asset_type == 'SAVINGS_ACCOUNTS':
                        assets['bank'] = self.compress_amount(asset_value)
                
                # Liabilities
                for liability in nw_response.get('liabilityValues', []):
                    liability_value = self.parse_currency_value(liability.get('value', {}))
                    total_debt += liability_value
            
            # Credit score
            credit_score = None
            if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
                reports = financial_data.credit_report.get('creditReports', [])
                if reports:
                    credit_score = reports[0].get('creditReportData', {}).get('score', {}).get('bureauScore')
            
            # Top investments with returns
            top_investments = []
            if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
                mf_analytics = financial_data.net_worth.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
                
                # Get top 5 mutual funds by value for more context
                funds_with_value = []
                for fund in mf_analytics:
                    analytics = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                    current_value = self.parse_currency_value(analytics.get('currentValue', {}))
                    xirr = analytics.get('XIRR', 0)
                    
                    if current_value > 10000:  # Only significant holdings
                        funds_with_value.append((current_value, xirr))
                
                # Sort by value and take top 5 for more insights
                funds_with_value.sort(key=lambda x: x[0], reverse=True)
                for value, xirr in funds_with_value[:5]:
                    inv = {'v': self.compress_amount(value)}
                    if isinstance(xirr, (int, float)) and xirr != 0:
                        inv['r'] = f"{xirr:.1f}%"
                    top_investments.append(inv)
            
            # Calculate risk profile
            liquid_assets = self.parse_currency_value(
                next((a.get('value', {}) for a in nw_response.get('assetValues', []) 
                     if 'SAVINGS' in a.get('netWorthAttribute', '')), {})
            )
            total_assets = sum(self.parse_currency_value(a.get('value', {})) 
                             for a in nw_response.get('assetValues', []))
            
            liquid_ratio = f"{int((liquid_assets / total_assets * 100) if total_assets > 0 else 0)}%"
            
            # Determine risk profile based on portfolio composition
            equity_allocation = 0
            debt_allocation = 0
            
            for fund in mf_analytics:
                asset_class = fund.get('schemeDetail', {}).get('assetClass', '')
                analytics = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                current_value = self.parse_currency_value(analytics.get('currentValue', {}))
                
                if asset_class == 'EQUITY':
                    equity_allocation += current_value
                elif asset_class in ['DEBT', 'CASH']:
                    debt_allocation += current_value
            
            total_mf = equity_allocation + debt_allocation
            equity_percent = (equity_allocation / total_mf * 100) if total_mf > 0 else 0
            
            if equity_percent > 70:
                risk_profile = "HIGH"
            elif equity_percent > 40:
                risk_profile = "MOD"
            else:
                risk_profile = "LOW"
            
            # Generate key insights
            key_insights = []
            
            # Debt to asset ratio
            if total_debt > 0 and total_assets > 0:
                debt_ratio = (total_debt / total_assets) * 100
                if debt_ratio > 50:
                    key_insights.append(f"High debt ratio: {int(debt_ratio)}%")
                
            # Credit score insight
            if credit_score and int(credit_score) < 700:
                key_insights.append(f"Credit score needs improvement: {credit_score}")
            
            # Liquidity insight
            if liquid_assets < total_assets * 0.1:
                key_insights.append("Low emergency fund")
            
            return CompressedFinancialData(
                net_worth=self.compress_amount(net_worth_value),
                assets=assets,
                debt=self.compress_amount(total_debt) if total_debt > 0 else None,
                credit_score=credit_score,
                top_investments=top_investments,
                risk_profile=risk_profile,
                liquid_ratio=liquid_ratio,
                key_insights=key_insights
            )
            
        except Exception as e:
            logger.error(f"Error compressing financial data: {e}")
            return CompressedFinancialData(
                net_worth="0",
                assets={},
                debt=None,
                credit_score=None,
                top_investments=[],
                risk_profile="UNK",
                liquid_ratio="0%",
                key_insights=["Error processing data"]
            )
    
    def generate_local_llm_prompt(self, compressed_data: CompressedFinancialData, 
                                 user_query: str) -> str:
        """
        Generate detailed prompt for local LLM with comprehensive financial data
        Provides rich context for deeper insights (up to 4K tokens)
        """
        # Create detailed financial overview
        financial_overview = f"""
FINANCIAL PORTFOLIO ANALYSIS (All amounts in Indian Rupees ₹)

📊 NET WORTH: ₹{compressed_data.net_worth}

🏦 ASSET BREAKDOWN:"""
        
        for asset_type, value in compressed_data.assets.items():
            asset_name = {
                'mf': 'Mutual Funds',
                'epf': 'Employees Provident Fund (EPF)',
                'stock': 'Stock Holdings',
                'bank': 'Bank Savings'
            }.get(asset_type, asset_type.upper())
            financial_overview += f"\n  • {asset_name}: ₹{value}"
        
        if compressed_data.debt:
            financial_overview += f"\n\n💳 TOTAL DEBT: ₹{compressed_data.debt}"
        
        if compressed_data.credit_score:
            financial_overview += f"\n📈 CREDIT SCORE: {compressed_data.credit_score}"
        
        if compressed_data.top_investments:
            financial_overview += f"\n\n🎯 TOP INVESTMENTS:"
            for i, inv in enumerate(compressed_data.top_investments[:5], 1):
                investment_info = f"\n  {i}. ₹{inv['v']}"
                if 'r' in inv:
                    investment_info += f" (XIRR: {inv['r']})"
                financial_overview += investment_info
        
        financial_overview += f"\n\n⚖️ RISK PROFILE: {compressed_data.risk_profile}"
        financial_overview += f"\n💧 LIQUIDITY RATIO: {compressed_data.liquid_ratio}"
        
        if compressed_data.key_insights:
            financial_overview += f"\n\n💡 KEY INSIGHTS:"
            for insight in compressed_data.key_insights:
                financial_overview += f"\n  • {insight}"
        
        # Create comprehensive prompt
        prompt = f"""{financial_overview}

USER QUESTION: {user_query}

ANALYSIS INSTRUCTIONS:
You are a financial advisor analyzing an Indian investor's portfolio. All amounts are in Indian Rupees (₹). 
Provide a comprehensive financial analysis covering:
1. Portfolio health assessment
2. Risk evaluation
3. Asset allocation analysis  
4. Specific recommendations for improvement
5. Action items prioritized by importance

Focus on practical, actionable insights. Be specific about Indian financial context, tax implications, and investment opportunities. Provide detailed reasoning for your recommendations."""
        
        # Log token estimate
        char_count = len(prompt)
        token_estimate = char_count // 4  # Rough estimate
        logger.info(f"Enhanced Local LLM prompt: {char_count} chars, ~{token_estimate} tokens")
        
        return prompt
    
    def prepare_for_local_inference(self, financial_data: Any, 
                                   user_query: str = "Give me financial insights") -> Dict[str, Any]:
        """
        Prepare data for local LLM inference
        Returns both compressed data and optimized prompt
        """
        # Compress financial data
        compressed = self.compress_financial_data(financial_data)
        
        # Generate prompt
        prompt = self.generate_local_llm_prompt(compressed, user_query)
        
        # Return package for local LLM
        return {
            'compressed_data': compressed.to_json(),
            'compact_text': compressed.to_compact_text(),
            'prompt': prompt,
            'metadata': {
                'compression_ratio': self._calculate_compression_ratio(financial_data, compressed),
                'estimated_tokens': len(prompt) // 4,
                'char_count': len(prompt),
                'data_points': len(compressed.assets) + len(compressed.top_investments) + 3
            }
        }
    
    def _calculate_compression_ratio(self, original: Any, compressed: CompressedFinancialData) -> float:
        """Calculate compression ratio"""
        try:
            # Estimate original size
            original_str = json.dumps(original.raw_data if hasattr(original, 'raw_data') else {})
            compressed_str = compressed.to_compact_text()
            
            ratio = len(original_str) / len(compressed_str) if compressed_str else 0
            return round(ratio, 2)
        except:
            return 0.0

# Global processor instance
_processor = LocalLLMProcessor()

def compress_for_local_llm(financial_data: Any) -> CompressedFinancialData:
    """Compress financial data for local LLM processing"""
    return _processor.compress_financial_data(financial_data)

def prepare_local_llm_request(financial_data: Any, user_query: str) -> Dict[str, Any]:
    """Prepare complete request package for local LLM"""
    return _processor.prepare_for_local_inference(financial_data, user_query)