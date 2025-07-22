"""
Money Truth Engine - Pure AI-driven analysis engine for revealing hidden financial insights
NO HARDCODING - Everything calculated by AI agents using real MCP data
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class MoneyTruthEngine:
    """Pure AI-driven engine for analyzing user's financial data and revealing hidden truths"""
    
    def __init__(self, analyst_agent, research_agent, risk_agent, gemini_client):
        self.analyst = analyst_agent
        self.researcher = research_agent
        self.risk_advisor = risk_agent
        self.gemini_client = gemini_client
    
    async def analyze_complete(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete AI-driven analysis revealing all money truths"""
        try:
            # Run all AI analyses in parallel
            hidden_truths_task = self.analyze_hidden_truths(mcp_data)
            future_projection_task = self.calculate_future_wealth(mcp_data)
            portfolio_health_task = self.portfolio_health_check(mcp_data)
            goal_reality_task = self.life_goal_simulator(mcp_data)
            personality_task = self.analyze_money_personality(mcp_data)
            
            results = await asyncio.gather(
                hidden_truths_task,
                future_projection_task,
                portfolio_health_task,
                goal_reality_task,
                personality_task,
                return_exceptions=True
            )
            
            # Generate unified summary using AI
            unified_summary = await self._generate_ai_unified_summary(results, mcp_data)
            
            return {
                "hidden_truths": results[0] if not isinstance(results[0], Exception) else {},
                "future_projection": results[1] if not isinstance(results[1], Exception) else {},
                "portfolio_health": results[2] if not isinstance(results[2], Exception) else {},
                "goal_reality": results[3] if not isinstance(results[3], Exception) else {},
                "personality": results[4] if not isinstance(results[4], Exception) else {},
                "unified_summary": unified_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in complete analysis: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def analyze_hidden_truths(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI discovers hidden financial truths from user's data"""
        try:
            # Convert MCP data to JSON string for AI analysis
            financial_data_str = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
Based on this financial data, give me ONLY 3 short shocking truths:

DATA: {financial_data_str}

Format exactly like this:
1. BIGGEST LEAK: [One sentence] - ₹[amount] lost
   FIX: [One simple action]

2. DEAD MONEY: [One sentence] - ₹[amount] idle  
   FIX: [One simple action]

3. MISSED CHANCE: [One sentence] - ₹[amount] potential
   FIX: [One simple action]

Maximum 30 words per point. NO explanations.
"""

            response = await self._get_ai_response(prompt)
            
            # Return simple text response
            return {"ai_insights": response}
            
        except Exception as e:
            logger.error(f"Error in AI hidden truths analysis: {e}")
            return {"error": str(e)}
    
    async def calculate_future_wealth(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI calculates future wealth projections based on actual data patterns"""
        try:
            financial_data_str = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
Quick wealth prediction:

DATA: {financial_data_str}

Give me exactly:
1. At 40: ₹[amount]
2. At 50: ₹[amount]
3. At 60: ₹[amount]
4. SIP needed for ₹1Cr: ₹[amount]/month
5. Biggest missed opportunity: [One sentence]

Max 20 words per point. Numbers only.
"""

            response = await self._get_ai_response(prompt)
            
            return {"ai_projection": response}
            
        except Exception as e:
            logger.error(f"Error in AI wealth projection: {e}")
            return {"error": str(e)}
    
    async def portfolio_health_check(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI agents perform comprehensive portfolio diagnosis"""
        try:
            financial_data_str = json.dumps(mcp_data, indent=2)
            
            # Run parallel AI analysis by all three agents
            analyst_task = self._run_agent_analysis("analyst", financial_data_str)
            research_task = self._run_agent_analysis("researcher", financial_data_str)
            risk_task = self._run_agent_analysis("risk_advisor", financial_data_str)
            
            agent_analyses = await asyncio.gather(
                analyst_task, research_task, risk_task, return_exceptions=True
            )
            
            # Combine agent insights using AI
            combined_prompt = f"""
Portfolio health summary:

ANALYST: {agent_analyses[0] if not isinstance(agent_analyses[0], Exception) else "Failed"}
RESEARCHER: {agent_analyses[1] if not isinstance(agent_analyses[1], Exception) else "Failed"}
RISK: {agent_analyses[2] if not isinstance(agent_analyses[2], Exception) else "Failed"}

Give me:
1. Health Score: [0-100] - [Why in 10 words]
2. Top Problem: [One sentence] - ₹[loss amount]
3. Best Fix: [One action] - ₹[gain amount]

Max 30 words total. No explanations.
"""

            combined_response = await self._get_ai_response(combined_prompt)
            
            try:
                return json.loads(combined_response)
            except json.JSONDecodeError:
                return {"portfolio_diagnosis": combined_response}
            
        except Exception as e:
            logger.error(f"Error in AI portfolio health check: {e}")
            return {"error": str(e)}
    
    async def life_goal_simulator(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI simulates life goal feasibility using actual financial data"""
        try:
            financial_data_str = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
Goal reality check:

DATA: {financial_data_str}

Check these goals:
1. HOME ₹75L: [POSSIBLE/SHORT/NO] - Need ₹[amount]/month
2. EDUCATION ₹40L: [POSSIBLE/SHORT/NO] - Need ₹[amount]/month  
3. RETIREMENT ₹4Cr: [POSSIBLE/SHORT/NO] - Need ₹[amount]/month
4. EMERGENCY ₹15L: [POSSIBLE/SHORT/NO] - Need ₹[amount]/month

Max 15 words per goal. Just status and SIP amount.
"""

            response = await self._get_ai_response(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"goal_analysis": response}
            
        except Exception as e:
            logger.error(f"Error in AI goal simulation: {e}")
            return {"error": str(e)}
    
    async def analyze_money_personality(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI analyzes behavioral patterns and money personality"""
        try:
            financial_data_str = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
Money personality quick read:

DATA: {financial_data_str}

Tell me:
1. TYPE: [Conservative/Balanced/Aggressive] - Why in 5 words
2. WEAKNESS: [One behavioral flaw] - Costs ₹[amount]/year  
3. STRENGTH: [One good habit] - Saves ₹[amount]/year
4. FIX: [One simple change] - Could gain ₹[amount]

Max 20 words per point. No psychology jargon.
"""

            response = await self._get_ai_response(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"personality_analysis": response}
            
        except Exception as e:
            logger.error(f"Error in AI personality analysis: {e}")
            return {"error": str(e)}
    
    async def _run_agent_analysis(self, agent_type: str, financial_data: str) -> str:
        """Run AI analysis for specific agent type"""
        
        agent_prompts = {
            "analyst": """
You are a Technical Financial Analyst AI. Analyze this portfolio data for:
- Performance metrics and benchmarking
- Asset allocation efficiency
- Technical indicators and trends
- Quantitative assessment of returns
- Specific funds that are underperforming
- Rebalancing recommendations with exact percentages
""",
            "researcher": """
You are a Market Research AI. Analyze this portfolio for:
- Market opportunities being missed
- Sector allocation vs market trends
- Investment themes alignment
- Growth potential assessment
- Alternative investments to consider
- Market timing and strategy recommendations
""",
            "risk_advisor": """
You are a Risk Assessment AI. Analyze this portfolio for:
- Risk concentration and diversification
- Volatility analysis
- Drawdown protection
- Insurance and protection gaps
- Emergency fund adequacy
- Stress testing scenarios
"""
        }
        
        full_prompt = f"""
{agent_prompts.get(agent_type, agent_prompts['analyst'])}

FINANCIAL DATA TO ANALYZE:
{financial_data}

Provide specific insights with calculations and recommendations based on the actual data.
Focus on actionable insights with quantified impact.
"""
        
        return await self._get_ai_response(full_prompt)
    
    async def _generate_ai_unified_summary(self, all_results: List[Any], mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI generates unified summary of all analyses"""
        try:
            results_str = json.dumps({
                "hidden_truths": all_results[0] if not isinstance(all_results[0], Exception) else {},
                "future_projection": all_results[1] if not isinstance(all_results[1], Exception) else {},
                "portfolio_health": all_results[2] if not isinstance(all_results[2], Exception) else {},
                "goal_reality": all_results[3] if not isinstance(all_results[3], Exception) else {},
                "personality": all_results[4] if not isinstance(all_results[4], Exception) else {}
            }, indent=2)
            
            prompt = f"""
Final money truth summary:

RESULTS: {results_str}

Give me:
1. WORST DISCOVERY: [Shocking truth] - Losing ₹[amount]
2. BEST OPPORTUNITY: [Simple action] - Could gain ₹[amount]  
3. URGENT ACTION: [Do this now] - Impact ₹[amount]
4. SUCCESS ODDS: [0-100]% if you follow advice

Max 25 words per point. Make it hit hard.
"""

            response = await self._get_ai_response(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"unified_summary": response}
            
        except Exception as e:
            logger.error(f"Error generating AI unified summary: {e}")
            return {"error": str(e)}
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from Gemini AI"""
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.95,
                    top_k=40
                    # Removed max_output_tokens to fix MAX_TOKENS bug
                )
            )
            
            if response and hasattr(response, 'text') and response.text and response.text.strip():
                return response.text.strip()
            elif response and hasattr(response, 'candidates') and response.candidates:
                # Try to get text from candidates
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text and part.text.strip():
                                    return part.text.strip()
                logger.warning(f"No valid text found in candidates: {response.candidates}")
                return "Quick analysis: Unable to process data format. Please refresh."
            else:
                logger.warning(f"Empty response received: {response}")
                return "Analysis processing... Please try refreshing the card."
                
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return f"Analysis temporarily unavailable. Please refresh to try again."
    
    async def get_real_time_insights(self, mcp_data: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Generate real-time insights based on user query and MCP data"""
        try:
            financial_data_str = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
Quick answer:

QUESTION: {user_query}
DATA: {financial_data_str}

Give me:
1. ANSWER: [Direct response in 10 words]
2. YOUR NUMBERS: ₹[relevant amount from their data]
3. ACTION: [One thing to do now]
4. RESULT: [What happens] - ₹[impact amount]

Max 15 words per point. Use their real numbers.
"""

            response = await self._get_ai_response(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"real_time_insight": response}
            
        except Exception as e:
            logger.error(f"Error generating real-time insights: {e}")
            return {"error": str(e)}