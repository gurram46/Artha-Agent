"""
Money Truth Engine - Pure AI-driven analysis engine for revealing hidden financial insights
NO HARDCODING - Everything calculated by specialized AI agents using real MCP data
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from google import genai
from google.genai import types

# Import specialized money truth agents
from agents.money_truth_agents.hidden_truths_agent import HiddenTruthsAgent
from agents.money_truth_agents.future_projection_agent import FutureProjectionAgent
from agents.money_truth_agents.portfolio_health_agent import PortfolioHealthAgent
from agents.money_truth_agents.goal_reality_agent import GoalRealityAgent
from agents.money_truth_agents.money_personality_agent import MoneyPersonalityAgent
from agents.money_truth_agents.money_leaks_agent import MoneyLeaksAgent
from agents.money_truth_agents.risk_assessment_agent import RiskAssessmentAgent

logger = logging.getLogger(__name__)


class MoneyTruthEngine:
    """Pure AI-driven engine for analyzing user's financial data and revealing hidden truths"""
    
    def __init__(self, gemini_client):
        """Initialize with specialized AI agents"""
        self.gemini_client = gemini_client
        
        # Initialize specialized agents
        self.hidden_truths_agent = HiddenTruthsAgent(gemini_client)
        self.future_projection_agent = FutureProjectionAgent(gemini_client)
        self.portfolio_health_agent = PortfolioHealthAgent(gemini_client)
        self.goal_reality_agent = GoalRealityAgent(gemini_client)
        self.money_personality_agent = MoneyPersonalityAgent(gemini_client)
        self.money_leaks_agent = MoneyLeaksAgent(gemini_client)
        self.risk_assessment_agent = RiskAssessmentAgent(gemini_client)
        
        logger.info("MoneyTruthEngine initialized with 7 specialized AI agents")
    
    async def analyze_complete(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete AI-driven analysis revealing all money truths using specialized agents"""
        try:
            logger.info("🔍 MONEY TRUTH ENGINE: Starting complete analysis with 7 specialized AI agents")
            logger.info(f"📊 Input data size: {len(str(mcp_data))} characters")
            
            # Log agent initialization
            logger.info("🤖 Initializing specialized Money Truth agents:")
            logger.info("  - 🚨 Hidden Truths Agent")
            logger.info("  - 🔮 Future Projection Agent") 
            logger.info("  - 🏥 Portfolio Health Agent")
            logger.info("  - 🎯 Goal Reality Agent")
            logger.info("  - 🧠 Money Personality Agent")
            logger.info("  - 🔍 Money Leaks Agent")
            logger.info("  - ⚠️ Risk Assessment Agent")
            
            # Run all specialized AI agents in parallel
            logger.info("🚀 Launching all 7 agents in parallel for maximum efficiency...")
            start_time = datetime.now()
            
            tasks = [
                self.hidden_truths_agent.analyze(mcp_data),
                self.future_projection_agent.analyze(mcp_data),
                self.portfolio_health_agent.analyze(mcp_data),
                self.goal_reality_agent.analyze(mcp_data),
                self.money_personality_agent.analyze(mcp_data),
                self.money_leaks_agent.analyze(mcp_data),
                self.risk_assessment_agent.analyze(mcp_data)
            ]
            
            logger.info("⏳ Waiting for all agents to complete analysis...")
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⚡ All agents completed in {analysis_time:.2f} seconds")
            
            # Extract results with detailed logging
            agent_names = ["Hidden Truths", "Future Projection", "Portfolio Health", "Goal Reality", "Money Personality", "Money Leaks", "Risk Assessment"]
            agent_emojis = ["🚨", "🔮", "🏥", "🎯", "🧠", "🔍", "⚠️"]
            
            logger.info("📋 ANALYSIS RESULTS:")
            
            hidden_truths = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
            if isinstance(results[0], Exception):
                logger.error(f"❌ {agent_emojis[0]} {agent_names[0]} Agent FAILED: {str(results[0])}")
            else:
                logger.info(f"✅ {agent_emojis[0]} {agent_names[0]} Agent completed successfully")
                
            future_projection = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
            if isinstance(results[1], Exception):
                logger.error(f"❌ {agent_emojis[1]} {agent_names[1]} Agent FAILED: {str(results[1])}")
            else:
                logger.info(f"✅ {agent_emojis[1]} {agent_names[1]} Agent completed successfully")
                
            portfolio_health = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
            if isinstance(results[2], Exception):
                logger.error(f"❌ {agent_emojis[2]} {agent_names[2]} Agent FAILED: {str(results[2])}")
            else:
                logger.info(f"✅ {agent_emojis[2]} {agent_names[2]} Agent completed successfully")
                
            goal_reality = results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
            if isinstance(results[3], Exception):
                logger.error(f"❌ {agent_emojis[3]} {agent_names[3]} Agent FAILED: {str(results[3])}")
            else:
                logger.info(f"✅ {agent_emojis[3]} {agent_names[3]} Agent completed successfully")
                
            money_personality = results[4] if not isinstance(results[4], Exception) else {"error": str(results[4])}
            if isinstance(results[4], Exception):
                logger.error(f"❌ {agent_emojis[4]} {agent_names[4]} Agent FAILED: {str(results[4])}")
            else:
                logger.info(f"✅ {agent_emojis[4]} {agent_names[4]} Agent completed successfully")
                
            money_leaks = results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])}
            if isinstance(results[5], Exception):
                logger.error(f"❌ {agent_emojis[5]} {agent_names[5]} Agent FAILED: {str(results[5])}")
            else:
                logger.info(f"✅ {agent_emojis[5]} {agent_names[5]} Agent completed successfully")
                
            risk_assessment = results[6] if not isinstance(results[6], Exception) else {"error": str(results[6])}
            if isinstance(results[6], Exception):
                logger.error(f"❌ {agent_emojis[6]} {agent_names[6]} Agent FAILED: {str(results[6])}")
            else:
                logger.info(f"✅ {agent_emojis[6]} {agent_names[6]} Agent completed successfully")
            
            successful_count = sum(1 for result in results if not isinstance(result, Exception))
            failed_count = sum(1 for result in results if isinstance(result, Exception))
            
            logger.info(f"📊 FINAL RESULTS: {successful_count} successful, {failed_count} failed out of 7 agents")
            
            return {
                "hidden_truths": hidden_truths,
                "future_projection": future_projection,
                "portfolio_health": portfolio_health,
                "goal_reality": goal_reality,
                "money_personality": money_personality,
                "money_leaks": money_leaks,
                "risk_assessment": risk_assessment,
                "analysis_metadata": {
                    "total_agents": 7,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "successful_analyses": sum(1 for result in results if not isinstance(result, Exception)),
                    "failed_analyses": sum(1 for result in results if isinstance(result, Exception))
                }
            }
            
        except Exception as e:
            logger.error(f"Complete Money Truth Engine analysis failed: {e}")
            return {
                "hidden_truths": {"error": f"Analysis failed: {str(e)}"},
                "future_projection": {"error": f"Analysis failed: {str(e)}"},
                "portfolio_health": {"error": f"Analysis failed: {str(e)}"},
                "goal_reality": {"error": f"Analysis failed: {str(e)}"},
                "money_personality": {"error": f"Analysis failed: {str(e)}"},
                "money_leaks": {"error": f"Analysis failed: {str(e)}"},
                "risk_assessment": {"error": f"Analysis failed: {str(e)}"},
                "analysis_metadata": {
                    "total_agents": 7,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "successful_analyses": 0,
                    "failed_analyses": 7,
                    "error": str(e)
                }
            }
    
    # Individual agent analysis methods for backwards compatibility
    async def analyze_hidden_truths(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hidden financial truths using specialized agent"""
        logger.info("🚨 HIDDEN TRUTHS AGENT: Starting analysis...")
        start_time = datetime.now()
        try:
            result = await self.hidden_truths_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🚨 HIDDEN TRUTHS: Completed in {analysis_time:.2f}s - Found {len(str(result))} chars of insights")
            return result
        except Exception as e:
            logger.error(f"🚨 HIDDEN TRUTHS AGENT FAILED: {str(e)}")
            raise
    
    async def calculate_future_wealth(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate future wealth projection using specialized agent"""
        logger.info("🔮 FUTURE PROJECTION AGENT: Starting wealth calculation...")
        start_time = datetime.now()
        try:
            result = await self.future_projection_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🔮 FUTURE PROJECTION: Completed in {analysis_time:.2f}s - Generated projection insights")
            return result
        except Exception as e:
            logger.error(f"🔮 FUTURE PROJECTION AGENT FAILED: {str(e)}")
            raise
    
    async def portfolio_health_check(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform portfolio health check using specialized agent"""
        logger.info("🏥 PORTFOLIO HEALTH AGENT: Starting health diagnosis...")
        start_time = datetime.now()
        try:
            result = await self.portfolio_health_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🏥 PORTFOLIO HEALTH: Completed in {analysis_time:.2f}s - Health diagnosis complete")
            return result
        except Exception as e:
            logger.error(f"🏥 PORTFOLIO HEALTH AGENT FAILED: {str(e)}")
            raise
    
    async def life_goal_simulator(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate life goal achievability using specialized agent"""
        logger.info("🎯 GOAL REALITY AGENT: Starting goal simulation...")
        start_time = datetime.now()
        try:
            result = await self.goal_reality_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🎯 GOAL REALITY: Completed in {analysis_time:.2f}s - Reality check complete")
            return result
        except Exception as e:
            logger.error(f"🎯 GOAL REALITY AGENT FAILED: {str(e)}")
            raise
    
    async def analyze_money_personality(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze money personality using specialized agent"""
        logger.info("🧠 MONEY PERSONALITY AGENT: Starting behavioral analysis...")
        start_time = datetime.now()
        try:
            result = await self.money_personality_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🧠 MONEY PERSONALITY: Completed in {analysis_time:.2f}s - Personality profile ready")
            return result
        except Exception as e:
            logger.error(f"🧠 MONEY PERSONALITY AGENT FAILED: {str(e)}")
            raise
    
    async def detect_money_leaks(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect money leaks using specialized agent"""
        logger.info("🔍 MONEY LEAKS AGENT: Starting leak detection...")
        start_time = datetime.now()
        try:
            result = await self.money_leaks_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🔍 MONEY LEAKS: Completed in {analysis_time:.2f}s - Leak analysis complete")
            return result
        except Exception as e:
            logger.error(f"🔍 MONEY LEAKS AGENT FAILED: {str(e)}")
            raise
    
    async def assess_financial_risks(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess financial risks using specialized agent"""
        logger.info("⚠️ RISK ASSESSMENT AGENT: Starting risk analysis...")
        start_time = datetime.now()
        try:
            result = await self.risk_assessment_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⚠️ RISK ASSESSMENT: Completed in {analysis_time:.2f}s - Risk profile generated")
            return result
        except Exception as e:
            logger.error(f"⚠️ RISK ASSESSMENT AGENT FAILED: {str(e)}")
            raise