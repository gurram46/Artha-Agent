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

# Import core money truth agents
from agents.money_truth_agents.portfolio_health_agent import PortfolioHealthAgent
from agents.money_truth_agents.risk_assessment_agent import RiskAssessmentAgent
from agents.money_truth_agents.trip_planning_agent import TripPlanningAgent

logger = logging.getLogger(__name__)


class MoneyTruthEngine:
    """Pure AI-driven engine for analyzing user's financial data and revealing hidden truths"""
    
    def __init__(self, gemini_client):
        """Initialize with core AI agents"""
        self.gemini_client = gemini_client
        
        # Initialize core agents
        self.portfolio_health_agent = PortfolioHealthAgent(gemini_client)
        self.risk_assessment_agent = RiskAssessmentAgent(gemini_client)
        self.trip_planning_agent = TripPlanningAgent(gemini_client)
        
        logger.info("MoneyTruthEngine initialized with 3 core AI agents")
    
    async def analyze_complete(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete AI-driven analysis using core financial agents"""
        try:
            logger.info("🔍 MONEY TRUTH ENGINE: Starting analysis with core AI agents")
            logger.info(f"📊 Input data size: {len(str(mcp_data))} characters")
            
            # Log agent initialization
            logger.info("🤖 Initializing core Money Truth agents:")
            logger.info("  - 🏥 Portfolio Health Agent")
            logger.info("  - ⚠️ Risk Assessment Agent")
            logger.info("  - 🧳 Trip Planning Agent")
            
            # Run core AI agents in parallel
            logger.info("🚀 Launching core agents for financial analysis...")
            start_time = datetime.now()
            
            tasks = [
                self.portfolio_health_agent.analyze(mcp_data),
                self.risk_assessment_agent.analyze(mcp_data),
                self.trip_planning_agent.analyze(mcp_data)
            ]
            
            logger.info("⏳ Waiting for core agents to complete analysis...")
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⚡ Core agents completed in {analysis_time:.2f} seconds")
            
            # Extract results with detailed logging
            agent_names = ["Portfolio Health", "Risk Assessment", "Trip Planning"]
            agent_emojis = ["🏥", "⚠️", "🧳"]
            
            logger.info("📋 ANALYSIS RESULTS:")
            
            portfolio_health = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
            if isinstance(results[0], Exception):
                logger.error(f"❌ {agent_emojis[0]} {agent_names[0]} Agent FAILED: {str(results[0])}")
            else:
                logger.info(f"✅ {agent_emojis[0]} {agent_names[0]} Agent completed successfully")
                
            risk_assessment = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
            if isinstance(results[1], Exception):
                logger.error(f"❌ {agent_emojis[1]} {agent_names[1]} Agent FAILED: {str(results[1])}")
            else:
                logger.info(f"✅ {agent_emojis[1]} {agent_names[1]} Agent completed successfully")
                
            trip_planning = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
            if isinstance(results[2], Exception):
                logger.error(f"❌ {agent_emojis[2]} {agent_names[2]} Agent FAILED: {str(results[2])}")
            else:
                logger.info(f"✅ {agent_emojis[2]} {agent_names[2]} Agent completed successfully")
            
            successful_count = sum(1 for result in results if not isinstance(result, Exception))
            failed_count = sum(1 for result in results if isinstance(result, Exception))
            
            logger.info(f"📊 FINAL RESULTS: {successful_count} successful, {failed_count} failed out of 3 core agents")
            
            return {
                "portfolio_health": portfolio_health,
                "risk_assessment": risk_assessment,
                "trip_planning": trip_planning,
                "analysis_metadata": {
                    "total_agents": 3,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "successful_analyses": sum(1 for result in results if not isinstance(result, Exception)),
                    "failed_analyses": sum(1 for result in results if isinstance(result, Exception))
                }
            }
            
        except Exception as e:
            logger.error(f"Complete Money Truth Engine analysis failed: {e}")
            return {
                "portfolio_health": {"error": f"Analysis failed: {str(e)}"},
                "risk_assessment": {"error": f"Analysis failed: {str(e)}"},
                "trip_planning": {"error": f"Analysis failed: {str(e)}"},
                "analysis_metadata": {
                    "total_agents": 3,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "successful_analyses": 0,
                    "failed_analyses": 3,
                    "error": str(e)
                }
            }
    
    # Individual agent analysis methods for core agents only
    
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
    
    async def plan_smart_trip(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan financially smart trips using specialized agent"""
        logger.info("🧳 TRIP PLANNING AGENT: Starting travel analysis...")
        start_time = datetime.now()
        try:
            result = await self.trip_planning_agent.analyze(mcp_data)
            analysis_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🧳 TRIP PLANNING: Completed in {analysis_time:.2f}s - Travel plan generated")
            return result
        except Exception as e:
            logger.error(f"🧳 TRIP PLANNING AGENT FAILED: {str(e)}")
            raise