"""
Base class for Money Truth Engine agents
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class BaseMoneyAgent:
    """Base class for all Money Truth Engine agents"""
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "Base Money Agent"
        self.description = "Base agent for financial analysis"
        
        # Standard AI configuration for financial analysis
        self.config = types.GenerateContentConfig(
            temperature=0.3,  # Lower temperature for more consistent financial analysis
            max_output_tokens=8000,
            top_p=0.8,
            top_k=40
        )
    
    def format_financial_data(self, mcp_data: Dict[str, Any]) -> str:
        """Format MCP financial data for AI analysis"""
        try:
            formatted = []
            
            logger.info(f"🔍 {self.name}: Formatting MCP data with keys: {list(mcp_data.keys())}")
            
            # Handle nested data structure
            data = mcp_data.get('data', mcp_data)  # Handle both formats
            
            # Account balances
            if 'accounts' in data:
                formatted.append("💰 ACCOUNT BALANCES:")
                for account in data['accounts']:
                    formatted.append(f"  - {account.get('name', 'Unknown')}: ₹{account.get('balance', 0):,.2f}")
            
            # Mutual funds
            if 'mutual_funds' in data:
                formatted.append("\n📊 MUTUAL FUNDS:")
                for fund in data['mutual_funds']:
                    current_value = fund.get('current_value', 0)
                    invested_amount = fund.get('invested_amount', 0)
                    gain_loss = current_value - invested_amount
                    
                    formatted.append(f"  - {fund.get('name', 'Unknown Fund')}")
                    formatted.append(f"    Invested: ₹{invested_amount:,.2f}")
                    formatted.append(f"    Current: ₹{current_value:,.2f}")
                    formatted.append(f"    Gain/Loss: ₹{gain_loss:,.2f}")
            
            # Stocks
            if 'stocks' in data:
                formatted.append("\n📈 STOCKS:")
                for stock in data['stocks']:
                    formatted.append(f"  - {stock.get('symbol', 'Unknown')}: {stock.get('quantity', 0)} shares @ ₹{stock.get('current_price', 0)}")
            
            # Loans
            if 'loans' in data:
                formatted.append("\n💳 LOANS:")
                for loan in data['loans']:
                    formatted.append(f"  - {loan.get('type', 'Unknown Loan')}: ₹{loan.get('outstanding_amount', 0):,.2f}")
            
            # Goals
            if 'goals' in data:
                formatted.append("\n🎯 FINANCIAL GOALS:")
                for goal in data['goals']:
                    formatted.append(f"  - {goal.get('name', 'Unknown Goal')}: Target ₹{goal.get('target_amount', 0):,.2f}")
            
            return "\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Error formatting financial data: {e}")
            return f"Financial data available but formatting failed: {str(e)}"
    
    async def call_ai(self, prompt: str, system_prompt: str = "") -> str:
        """Call Gemini AI with proper error handling and detailed logging"""
        try:
            logger.info(f"🤖 {self.name}: Calling Gemini AI...")
            logger.info(f"📝 Prompt length: {len(prompt)} chars")
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            ai_start_time = datetime.now()
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=self.config
            )
            ai_time = (datetime.now() - ai_start_time).total_seconds()
            
            logger.info(f"⚡ {self.name}: Gemini AI responded in {ai_time:.2f}s")
            
            # Extract text from response with better error handling
            response_text = None
            
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        part_text = candidate.content.parts[0].text
                        if part_text:  # Check for None
                            response_text = part_text
                            logger.info(f"✅ {self.name}: Generated {len(response_text)} chars of analysis")
                        else:
                            logger.warning(f"⚠️ {self.name}: AI response part text is None")
            
            # Fallback extraction
            if not response_text and hasattr(response, 'text') and response.text:
                response_text = response.text
                logger.info(f"✅ {self.name}: Generated {len(response_text)} chars of analysis (fallback)")
            
            # If we still don't have text, check for finish reason
            if not response_text:
                finish_reason = "unknown"
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = candidate.finish_reason
                
                logger.error(f"❌ {self.name}: No text in AI response. Finish reason: {finish_reason}")
                return f"AI analysis failed for {self.name}: No response text generated (finish reason: {finish_reason})"
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ AI call failed for {self.name}: {e}")
            return f"AI analysis failed for {self.name}: {str(e)}"
    
    def calculate_net_worth(self, mcp_data: Dict[str, Any]) -> float:
        """Calculate total net worth from MCP data"""
        total_assets = 0
        total_liabilities = 0
        
        # Handle nested data structure
        data = mcp_data.get('data', mcp_data)
        
        logger.info(f"💰 {self.name}: Calculating net worth from data keys: {list(data.keys())}")
        
        # Add account balances
        if 'accounts' in data:
            for account in data['accounts']:
                balance = account.get('balance', 0)
                total_assets += balance
                logger.info(f"💳 Account: {account.get('name', 'Unknown')} = ₹{balance:,.2f}")
        
        # Add mutual fund current values
        if 'mutual_funds' in data:
            for fund in data['mutual_funds']:
                value = fund.get('current_value', 0)
                total_assets += value
                logger.info(f"📊 Fund: {fund.get('name', 'Unknown')} = ₹{value:,.2f}")
        
        # Add stock values
        if 'stocks' in data:
            for stock in data['stocks']:
                quantity = stock.get('quantity', 0)
                price = stock.get('current_price', 0)
                value = quantity * price
                total_assets += value
                logger.info(f"📈 Stock: {stock.get('symbol', 'Unknown')} = ₹{value:,.2f}")
        
        # Subtract loan amounts
        if 'loans' in data:
            for loan in data['loans']:
                amount = loan.get('outstanding_amount', 0)
                total_liabilities += amount
                logger.info(f"💳 Loan: {loan.get('type', 'Unknown')} = -₹{amount:,.2f}")
        
        net_worth = total_assets - total_liabilities
        logger.info(f"💰 {self.name}: Calculated Net Worth = ₹{net_worth:,.2f} (Assets: ₹{total_assets:,.2f}, Liabilities: ₹{total_liabilities:,.2f})")
        
        return net_worth
    
    async def analyze(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method - to be implemented by subclasses"""
        logger.info(f"🔍 {self.name}: Starting analysis...")
        logger.info(f"📊 Input data keys: {list(mcp_data.keys()) if mcp_data else 'No data'}")
        
        start_time = datetime.now()
        try:
            # This will be overridden by subclasses
            result = await self._perform_analysis(mcp_data)
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ {self.name}: Analysis completed in {analysis_time:.2f}s")
            
            return result
            
        except Exception as e:
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ {self.name}: Analysis failed after {analysis_time:.2f}s - {str(e)}")
            raise
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement the _perform_analysis method")