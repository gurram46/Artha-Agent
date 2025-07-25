"""
Hidden Truths Agent - Reveals shocking financial discoveries
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class HiddenTruthsAgent(BaseMoneyAgent):
    """AI agent specialized in uncovering hidden financial truths and shocking discoveries"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Hidden Truths Detective"
        self.description = "Reveals shocking financial discoveries hidden in your data"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Uncover hidden financial truths that will shock the user"""
        try:
            logger.info(f"🚨 {self.name}: Formatting financial data for analysis...")
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            logger.info(f"💰 {self.name}: Calculated net worth: ₹{net_worth:,.2f}")
            
            logger.info(f"🔍 {self.name}: Analyzing data for shocking discoveries...")
            
            system_prompt = f"""
            You are the HIDDEN TRUTHS DETECTIVE - a financial forensics expert who uncovers shocking discoveries.
            
            Your mission: Analyze the user's financial data and reveal 3-5 SHOCKING hidden truths that will make them say "I had NO IDEA!"
            
            Focus on:
            1. Hidden patterns that reveal surprising money behaviors
            2. Shocking waste or inefficiencies they don't realize
            3. Surprising strengths or weaknesses in their portfolio
            4. Eye-opening comparisons to their peers
            5. Shocking implications of their current trajectory
            
            WRITING STYLE: 
            - Use 🔥, 💥, ⚡ emojis for impact
            - Start with "SHOCKING DISCOVERY:" 
            - Be specific with numbers and percentages
            - Make it personal and surprising
            - End each truth with a call to action
            """
            
            prompt = f"""
            FINANCIAL FORENSICS ANALYSIS
            Net Worth: ₹{net_worth:,.2f}
            
            {financial_data}
            
            Uncover the most SHOCKING hidden truths about this financial data. What would absolutely surprise this person about their money? 
            
            IMPORTANT: You MUST respond with ONLY valid JSON. Do not include any text before or after the JSON.
            
            Required JSON format:
            {{
                "shocking_discoveries": [
                    {{
                        "title": "SHOCKING DISCOVERY: [Eye-catching title with 🔥 emoji]",
                        "truth": "Detailed explanation with specific numbers and insights",
                        "impact": "What this means for their financial future", 
                        "action": "Specific actionable step they should take immediately"
                    }}
                ],
                "overall_shock_factor": "One-line summary of the biggest financial surprise",
                "confidence_level": 0.85
            }}
            
            Respond with JSON only - no other text.
            """
            
            logger.info(f"🤖 {self.name}: Sending prompt to AI for analysis...")
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Try to parse JSON response
            try:
                logger.info(f"📝 {self.name}: Parsing AI response...")
                result = json.loads(ai_response)
                
                discoveries_count = len(result.get('shocking_discoveries', []))
                logger.info(f"🔥 {self.name}: Found {discoveries_count} shocking discoveries!")
                
                # Add analysis metadata
                result.update({
                    "agent_name": self.name,
                    "analysis_type": "hidden_truths",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "net_worth_analyzed": net_worth,
                    "data_points_analyzed": len(mcp_data.get('accounts', [])) + len(mcp_data.get('mutual_funds', [])) + len(mcp_data.get('stocks', []))
                })
                
                logger.info(f"✅ {self.name}: Successfully generated hidden truths analysis")
                return result
                
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                logger.warning(f"⚠️ {self.name}: Failed to parse JSON from AI response, using fallback")
                logger.error(f"📝 JSON Error: {str(e)}")
                logger.error(f"🔍 AI Response Preview (first 500 chars): {ai_response[:500]}")
                logger.error(f"📊 Full AI Response Length: {len(ai_response)} chars")
                return {
                    "shocking_discoveries": [{
                        "title": "🔍 SHOCKING DISCOVERY: Hidden Financial Pattern Detected",
                        "truth": ai_response[:500] + "..." if len(ai_response) > 500 else ai_response,
                        "impact": "This discovery could significantly change your financial strategy",
                        "action": "Review the detailed analysis and consider making immediate adjustments"
                    }],
                    "overall_shock_factor": "Your financial data reveals surprising hidden patterns",
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "hidden_truths",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Hidden Truths analysis failed: {e}")
            return {
                "shocking_discoveries": [{
                    "title": "🚨 ANALYSIS ERROR",
                    "truth": f"Unable to complete hidden truths analysis: {str(e)}",
                    "impact": "Analysis temporarily unavailable",
                    "action": "Please try again later"
                }],
                "overall_shock_factor": "Analysis temporarily unavailable",
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "hidden_truths",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }