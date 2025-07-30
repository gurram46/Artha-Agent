"""
Quick Response Agent 🚀
Single agent for fast financial responses using Gemini 2.5 Flash without grounding
Optimized for speed and immediate actionable insights
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseFinancialAgent, AgentResponse
from core.fi_mcp.client import FinancialData
from google.genai import types

logger = logging.getLogger(__name__)

class QuickResponseAgent(BaseFinancialAgent):
    """Quick Response Agent - Single agent for fast financial responses without grounding"""
    
    def __init__(self):
        super().__init__("analyst")  # Inherits analyst agent configuration
        self.name = "Quick Response Financial Advisor"
        self.emoji = "⚡"
        self.personality = "fast and focused financial advisor"
        logger.info("⚡ Quick Response Financial Advisor initialized - Speed optimized without grounding")
    
    async def generate_quick_response(self, user_query: str, financial_data: FinancialData) -> Dict[str, Any]:
        """Generate fast response using Gemini 2.5 Flash without grounding"""
        
        try:
            # Quick financial context extraction
            financial_summary = self._extract_quick_financial_context(financial_data)
            
            # Create optimized prompt for quick response without grounding
            quick_prompt = f"""
You are a fast and focused Indian financial advisor. Provide immediate, actionable financial advice based on the user's actual financial data.

USER QUERY: {user_query}

USER'S FINANCIAL SITUATION:
{financial_summary}

INSTRUCTIONS:
1. Analyze the user's actual financial data provided above
2. If asking about transactions, identify the top transactions from the recent transaction data
3. Provide IMMEDIATE actionable advice (2-3 sentences max)
4. Use the specific financial data provided, not general advice
5. Focus on Indian financial context (₹, Indian markets, Indian products)
6. Be direct and practical - NO lengthy explanations
7. Give specific actionable steps based on their actual financial situation

Provide fast, actionable response based on the user's actual financial data.
"""
            
            # Generate response without grounding
            logger.info("⚡ Generating quick response without grounding...")
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=quick_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    top_p=0.9,
                    system_instruction="You are a fast Indian financial advisor. Be direct, actionable, and specific. Focus on immediate practical advice based on established financial principles."
                )
            )
            
            if response and response.text:
                response_content = response.text.strip()
                
                logger.info(f"⚡ Quick response generated: {len(response_content)} chars")
                
                return {
                    'agent': 'Quick Response Financial Advisor',
                    'content': response_content,
                    'emoji': '⚡',
                    'sources': [],
                    'search_queries': [],
                    'response_time': 'fast',
                    'mode': 'quick',
                    'grounded': False
                }
            else:
                logger.warning("⚡ Empty response from Gemini, using fallback")
                return self._generate_quick_fallback_response(user_query, financial_data)
                
        except Exception as e:
            logger.error(f"⚡ Quick response generation failed: {e}")
            return self._generate_quick_fallback_response(user_query, financial_data)
    
    def _extract_quick_financial_context(self, financial_data: FinancialData) -> str:
        """Extract essential financial context for quick responses"""
        context_parts = []
        
        try:
            # Essential net worth info
            if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
                net_worth_resp = financial_data.net_worth.get('netWorthResponse', {})
                total_value = net_worth_resp.get('totalNetWorthValue', {})
                if total_value.get('units'):
                    net_worth_amount = float(total_value.get('units', '0'))
                    context_parts.append(f"Net Worth: ₹{self.format_currency(net_worth_amount)}")
                
                # Quick liquid assets calculation
                assets = net_worth_resp.get('assetValues', [])
                liquid_total = 0
                for asset in assets:
                    if 'SAVINGS' in asset.get('netWorthAttribute', ''):
                        try:
                            liquid_total += float(asset.get('value', {}).get('units', '0'))
                        except:
                            pass
                
                if liquid_total > 0:
                    context_parts.append(f"Liquid Funds: ₹{self.format_currency(liquid_total)}")
            
            # Essential credit info
            if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
                credit_reports = financial_data.credit_report.get('creditReports', [])
                if credit_reports:
                    score = credit_reports[0].get('creditReportData', {}).get('score', {}).get('bureauScore')
                    if score:
                        context_parts.append(f"Credit Score: {score}")
            
            # Add transaction summary if available
            if hasattr(financial_data, 'bank_transactions') and financial_data.bank_transactions:
                tx_count = len(financial_data.bank_transactions)
                if tx_count > 0:
                    context_parts.append(f"Bank Transactions: {tx_count} recent transactions available")
                    
                    # Get recent transaction summary for context
                    if tx_count >= 3:
                        recent_transactions = sorted(financial_data.bank_transactions, 
                                                   key=lambda x: x.get('date', ''), reverse=True)[:3]
                        tx_summary = []
                        for tx in recent_transactions:
                            amount = abs(float(tx.get('amount', '0')))
                            narration = tx.get('narration', '')[:30] + '...' if len(tx.get('narration', '')) > 30 else tx.get('narration', '')
                            date = tx.get('date', '')
                            tx_type = 'credit' if tx.get('type') == 1 else 'debit'
                            tx_summary.append(f"{date}: {tx_type.upper()} ₹{amount:,.0f} - {narration}")
                        
                        context_parts.append(f"Recent Transactions: {'; '.join(tx_summary)}")
            
        except Exception as e:
            logger.warning(f"Quick context extraction error: {e}")
        
        return "Financial Profile: " + ", ".join(context_parts) if context_parts else "General Indian investor"
    
    def _generate_quick_fallback_response(self, user_query: str, financial_data: FinancialData) -> Dict[str, Any]:
        """Generate quick fallback response when AI fails"""
        
        # Basic query analysis for fallback
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['transaction', 'spend', 'payment', 'top', 'largest', 'biggest']):
            # Try to analyze actual transaction data for fallback
            if hasattr(financial_data, 'bank_transactions') and financial_data.bank_transactions:
                try:
                    # Get top 3 transactions by amount
                    sorted_transactions = sorted(financial_data.bank_transactions, 
                                               key=lambda x: abs(float(x.get('amount', '0'))), reverse=True)[:3]
                    tx_details = []
                    for i, tx in enumerate(sorted_transactions, 1):
                        amount = abs(float(tx.get('amount', '0')))
                        narration = tx.get('narration', 'Unknown transaction')[:40]
                        date = tx.get('date', '')
                        tx_details.append(f"{i}. ₹{amount:,.0f} - {narration} ({date})")
                    
                    fallback_content = f"Your top 3 transactions: {'; '.join(tx_details)}. Review these for spending patterns and optimize high amounts."
                except:
                    fallback_content = "Check your transaction history in the portfolio page for detailed spending analysis. Focus on reducing high-value unnecessary expenses."
            else:
                fallback_content = "No transaction data available. Connect your bank accounts for detailed spending analysis and personalized recommendations."
        elif any(word in query_lower for word in ['buy', 'purchase', 'invest']):
            fallback_content = "For investment decisions, consider: 1) Emergency fund adequacy (6 months expenses), 2) Debt obligations, 3) Risk tolerance. Research current market rates and consult financial advisors for specific recommendations."
        elif any(word in query_lower for word in ['emergency', 'fund', 'saving']):
            fallback_content = "Emergency fund target: 6-12 months of expenses in liquid savings accounts. Consider high-yield savings accounts or liquid mutual funds for better returns while maintaining accessibility."
        elif any(word in query_lower for word in ['loan', 'emi', 'debt']):
            fallback_content = "Loan decisions depend on: 1) Debt-to-income ratio (<40%), 2) Credit score (>750 for best rates), 3) Existing obligations. Compare interest rates across banks and consider loan tenure impact."
        elif any(word in query_lower for word in ['insurance', 'protection']):
            fallback_content = "Essential insurance: 1) Term life (10-15x annual income), 2) Health insurance (family floater), 3) Disability insurance if applicable. Compare policies and check claim settlement ratios."
        elif any(word in query_lower for word in ['tax', 'saving', '80c']):
            fallback_content = "Tax-saving options: ELSS funds, PPF, EPF, NSC, tax-saving FDs. ELSS offers market returns with 3-year lock-in. Max ₹1.5L under 80C. Consider overall portfolio allocation."
        else:
            fallback_content = "For specific financial advice, consider: 1) Your current financial position, 2) Risk tolerance, 3) Time horizon, 4) Market conditions. Consult certified financial planners for personalized recommendations."
        
        return {
            'agent': 'Quick Response Financial Advisor',
            'content': fallback_content,
            'emoji': '⚡',
            'sources': [],
            'search_queries': [],
            'response_time': 'fast',
            'mode': 'quick',
            'grounded': False,
            'fallback': True
        }
    
    # Required abstract methods (simplified for quick response)
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Not used in quick response mode - no grounding enabled"""
        return []
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Quick financial data analysis"""
        return {
            'analysis_type': 'quick',
            'status': 'completed',
            'mode': 'fast_response'
        }
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], financial_data: FinancialData) -> Dict[str, Any]:
        """Not used in quick response mode"""
        return {'status': 'quick_mode'}
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Not used - quick response uses generate_quick_response instead"""
        response_data = await self.generate_quick_response(user_query, financial_data)
        return response_data.get('content', 'Quick response generated')