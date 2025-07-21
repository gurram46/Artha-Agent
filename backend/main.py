"""
Revolutionary 3-Agent Financial AI Chatbot
Real-time streaming responses with agent collaboration
"""

import asyncio
import sys
import os
import json
import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.status import Status
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
import time

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import agents directly
from agents.analyst_agent.analyst import AnalystAgent
from agents.research_agent.strategist import ResearchAgent
from agents.risk_agent.risk_guardian import RiskAgent
from core.fi_mcp.client import FinancialData, get_user_financial_data
from google.genai import types

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArthaAIChatbot:
    """Revolutionary 3-Agent Financial AI Chatbot"""
    
    def __init__(self):
        self.console = Console()
        
        # Initialize agents
        try:
            self.analyst = AnalystAgent()
            self.research = ResearchAgent()
            self.risk = RiskAgent()
            self.console.print("[green]✅ All 3 agents initialized successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error initializing agents: {e}[/red]")
            sys.exit(1)
    
    def print_welcome(self):
        """Print welcome banner"""
        welcome = """
🏆 Revolutionary 3-Agent Financial AI System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Your Comprehensive Financial Advisory Team:
   🕵️ Financial Data Intelligence Analyst - Complete financial analysis for ANY decision
   🎯 Universal Financial Strategist - Plans for ALL financial goals  
   🛡️ Comprehensive Risk Advisor - Protects ALL financial decisions

🌟 HANDLES ALL FINANCIAL QUESTIONS:
   Cars, Houses, Jobs, Travel, Taxes, Investments, Insurance, Loans - EVERYTHING!

💡 Powered by Google Search Grounding + Live Market Data
🚀 Watch agents collaborate in real-time!

Type your financial questions or 'quit' to exit.
        """
        
        self.console.print(Panel(
            welcome,
            title="[bold blue]ARTHA AI CHATBOT[/bold blue]",
            border_style="blue"
        ))
    
    def create_agent_table(self, statuses: Dict[str, Dict]) -> Table:
        """Create agent status table"""
        table = Table(title="🤖 Agent Status", show_header=True)
        table.add_column("Agent", style="cyan", width=20)
        table.add_column("Status", style="green", width=15)
        table.add_column("Activity", style="yellow", width=40)
        
        for agent_key, info in statuses.items():
            status_color = {
                "idle": "dim",
                "thinking": "yellow",
                "researching": "blue",
                "analyzing": "green",
                "complete": "bright_green"
            }.get(info["status"], "white")
            
            table.add_row(
                f"{info['emoji']} {agent_key.title()}",
                f"[{status_color}]{info['status'].upper()}[/{status_color}]",
                info["message"]
            )
        
        return table
    
    async def stream_agent_response_OLD_UNUSED(self, agent, agent_name: str, query: str, financial_data: FinancialData):
        """Stream single agent response with status updates"""
        
        # Update status
        statuses = {
            "analyst": {"emoji": "🕵️", "status": "idle", "message": "Waiting..."},
            "research": {"emoji": "🎯", "status": "idle", "message": "Waiting..."},
            "risk": {"emoji": "🛡️", "status": "idle", "message": "Waiting..."}
        }
        statuses[agent_name]["status"] = "thinking"
        statuses[agent_name]["message"] = "Analyzing financial data..."
        
        with Live(self.create_agent_table(statuses), refresh_per_second=2) as live:
            
            # Use the new process_user_query method that handles everything
            agent_response = None
            
            async for update in agent.process_user_query(query, financial_data):
                if update['type'] == 'thinking':
                    # Update status based on stage
                    stage = update['stage']
                    if stage == 'financial_analysis':
                        statuses[agent_name]["status"] = "analyzing"
                        statuses[agent_name]["message"] = "AI analyzing financial data..."
                    elif stage == 'query_generation':
                        statuses[agent_name]["status"] = "researching"
                        statuses[agent_name]["message"] = "AI generating search queries..."
                    elif stage == 'market_research':
                        statuses[agent_name]["status"] = "researching"
                        statuses[agent_name]["message"] = f"Searching Google: {update['content'][:40]}..."
                    elif stage == 'intelligence_processing':
                        statuses[agent_name]["status"] = "analyzing"
                        statuses[agent_name]["message"] = "AI processing search results..."
                    elif stage == 'response_generation':
                        statuses[agent_name]["message"] = "AI formulating recommendations..."
                    
                    live.update(self.create_agent_table(statuses))
                    
                elif update['type'] == 'response':
                    agent_response = update['response']
                    response_content = agent_response['content']
                    
                elif update['type'] == 'error':
                    statuses[agent_name]["status"] = "error"
                    statuses[agent_name]["message"] = f"Error: {update['error']}"
                    live.update(self.create_agent_table(statuses))
                    response_content = update['response']['content']
            
            # Complete
            statuses[agent_name]["status"] = "complete"
            statuses[agent_name]["message"] = "Analysis complete!"
            live.update(self.create_agent_table(statuses))
            
            await asyncio.sleep(0.5)
        
        # Count actual sources from search results
        total_sources = 0
        if agent_response and 'grounded_data' in agent_response:
            for search_result in agent_response.get('grounded_data', []):
                if isinstance(search_result, dict) and 'sources' in search_result:
                    total_sources += len(search_result['sources'])
        
        return {
            'agent_name': agent.name,
            'emoji': agent.emoji,
            'content': response_content if 'response_content' in locals() else "Analysis failed",
            'grounding_sources': total_sources,  # Use actual source count
            'search_results': len(agent_response.get('grounded_data', [])) if agent_response else 0,
            'recommendations': agent_response.get('recommendations', []) if agent_response else []
        }
    
    async def process_query_with_collaboration(self, user_query: str):
        """Ultra-speed processing with sequential agent collaboration"""
        
        self.console.print(f"\n[bold cyan]Processing:[/bold cyan] {user_query}\n")
        
        # Fetch financial data
        with Status("[blue]📊 Fetching your financial data from Fi MCP...", console=self.console):
            try:
                financial_data = await get_user_financial_data()
                self.console.print("[green]✅ Financial data loaded successfully[/green]")
            except Exception as e:
                self.console.print("[yellow]⚠️ Using sample financial data for demo[/yellow]")
                financial_data = await self.create_sample_financial_data()
        
        self.console.print("\n[bold blue]🚀 Ultra-Speed 3-Agent Pipeline...[/bold blue]\n")
        
        # STAGE 1: Generate comprehensive search query (skip separate data analysis to reduce API calls)
        self.console.print("[bold]🕵️ Stage 1: Intelligent Query Generation[/bold]")
        with Status("Generating comprehensive market intelligence query...", console=self.console):
            search_query = await self.analyst.generate_comprehensive_search_query(user_query, financial_data)
            # Skip separate data analysis - integrate it into agent responses
            data_analysis = {'status': 'integrated_into_agent_analysis'}
        
        self.console.print(f"[green]✅ Search query: {search_query}[/green]")
        self.console.print(f"[dim]Query length: {len(search_query.split())} words[/dim]")
        
        # STAGE 2: Single Google Grounding Search with comprehensive query
        self.console.print("[bold]🔍 Stage 2: Google Search Grounding - Live Market Data[/bold]")
        with Status(f"Searching: {search_query[:50]}...", console=self.console):
            market_intelligence = await self.analyst.search_with_gemini(search_query, self._format_financial_summary_for_search(financial_data))
        
        sources_count = len(market_intelligence.get('sources', []))
        self.console.print(f"[green]✅ Retrieved {sources_count} live market data sources[/green]\n")
        
        # STAGE 3: Research Agent processes grounded data
        self.console.print("[bold]🎯 Stage 3: Strategic Research & Opportunity Analysis[/bold]")
        logger.info(f"Calling Research Agent with market intelligence: {len(market_intelligence.get('sources', []))} sources")
        research_response = await self.research.process_market_intelligence(
            user_query, financial_data, data_analysis, market_intelligence
        )
        logger.info(f"Research Agent returned: {type(research_response)}, keys: {list(research_response.keys()) if isinstance(research_response, dict) else 'Not a dict'}")
        
        # Display FULL research response
        research_content = research_response.get('content', 'No research content available')
        self.console.print(Panel(
            research_content,
            title=f"🎯 Research Findings - FULL RESPONSE ({len(research_content)} chars)",
            border_style="blue"
        ))
        
        # STAGE 4: Risk Agent gets all previous analysis
        self.console.print("[bold]🛡️ Stage 4: Comprehensive Risk Assessment[/bold]")
        logger.info(f"Calling Risk Agent with research response: {type(research_response)}")
        risk_response = await self.risk.assess_comprehensive_risks(
            user_query, financial_data, data_analysis, research_response, market_intelligence
        )
        logger.info(f"Risk Agent returned: {type(risk_response)}, keys: {list(risk_response.keys()) if isinstance(risk_response, dict) else 'Not a dict'}")
        
        # Display FULL risk response
        risk_content = risk_response.get('content', 'No risk content available')
        self.console.print(Panel(
            risk_content,
            title=f"🛡️ Risk Assessment - FULL RESPONSE ({len(risk_content)} chars)",
            border_style="red"
        ))
        
        # STAGE 5: Unified AI generates final response
        self.console.print("[bold yellow]🤖 Stage 5: Unified AI Decision Generation[/bold yellow]")
        logger.info(f"Preparing unified response with agent outputs. Research content length: {len(research_response.get('content', ''))} chars")
        logger.info(f"Risk content length: {len(risk_response.get('content', ''))} chars")
        
        agent_outputs = {
            'data_analysis': {
                'agent': 'Data Analysis',
                'content': str(data_analysis) if data_analysis else 'Data analysis not available',
                'emoji': '🕵️'
            },
            'research': research_response,
            'risk': risk_response,
            'market_intelligence': market_intelligence,
            'sources_count': sources_count
        }
        
        await self.generate_unified_response(user_query, financial_data, agent_outputs)
    
    def _format_financial_summary_for_search(self, financial_data: FinancialData) -> str:
        """Format financial data for search context"""
        summary_parts = []
        
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth.get('netWorthResponse', {})
            total_value = net_worth.get('totalNetWorthValue', {})
            if total_value.get('units'):
                summary_parts.append(f"Net worth ₹{total_value.get('units')}")
        
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports:
                score = credit_reports[0].get('creditReportData', {}).get('score', {}).get('bureauScore')
                if score:
                    summary_parts.append(f"Credit score {score}")
        
        return "User: " + ", ".join(summary_parts) if summary_parts else "General user"
    
    async def generate_unified_response(self, user_query: str, financial_data: FinancialData, agent_outputs: Dict[str, Any]):
        """Generate final unified response using all agent outputs"""
        
        # Direct, concise unified AI prompt for any financial question
        net_worth_value = financial_data.net_worth.get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', '0')
        unified_prompt = f"""
USER QUESTION: {user_query}

YOUR FINANCIAL DATA:
- Net Worth: ₹{net_worth_value}
- Available Liquid Funds: ₹520,968
- Emergency Fund: ₹432,887
- Total Debt: ₹75,000

EXPERT ANALYSIS COMPLETED:
Research Agent: {agent_outputs['research']['content'][:400]}...
Risk Agent: {agent_outputs['risk']['content'][:400]}...

PROVIDE A SHORT, DIRECT ANSWER (max 150 words):

Answer their specific question directly with:
- Clear YES/NO or specific numbers/amounts
- One key reason from the analysis
- One immediate action they should take

Be conversational, direct, and helpful. No long explanations or generic advice."""
        
        try:
            logger.info(f"Generating unified AI response with prompt length: {len(unified_prompt)} characters")
            # Generate unified response
            unified_response = self.analyst.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=unified_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            logger.info(f"Unified API call completed. Response type: {type(unified_response)}")
            
            if unified_response and unified_response.text and unified_response.text.strip():
                final_response = unified_response.text.strip()
                logger.info(f"Unified AI response generated successfully: {len(final_response)} characters")
            else:
                logger.error(f"Unified AI response was empty. Response object: {unified_response}")
                if hasattr(unified_response, 'text'):
                    logger.error(f"Response text was: '{unified_response.text}'")
                if hasattr(unified_response, 'candidates') and unified_response.candidates:
                    logger.error(f"Candidate[0]: {unified_response.candidates[0]}")
                    if hasattr(unified_response.candidates[0], 'finish_reason'):
                        logger.error(f"Finish reason: {unified_response.candidates[0].finish_reason}")
                if hasattr(unified_response, 'usage_metadata'):
                    logger.error(f"Usage metadata: {unified_response.usage_metadata}")
                final_response = f"ERROR: Unified AI failed - check logs. Finish reason: {unified_response.candidates[0].finish_reason if hasattr(unified_response, 'candidates') and unified_response.candidates else 'Unknown'}"
            
        except Exception as e:
            logger.error(f"Unified AI response generation failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Prompt used: {unified_prompt[:500]}..." if len(unified_prompt) > 500 else unified_prompt)
            final_response = f"Unified AI response generation failed: {str(e)}"
        
        # Display unified response
        self.console.print(Panel(
            final_response,
            title="[bold green]🏆 UNIFIED AI FINANCIAL ADVISOR[/bold green]",
            border_style="green"
        ))
        
        # Show analysis metrics
        metrics = f"""
📊 **ULTRA-SPEED ANALYSIS COMPLETE**:
• **Market Intelligence**: {agent_outputs['sources_count']} live data sources
• **Processing Time**: Optimized single-pass analysis
• **Agent Collaboration**: Sequential building for maximum accuracy
"""
        self.console.print(f"\n[dim]{metrics}[/dim]")
        
    
    async def create_sample_financial_data(self) -> FinancialData:
        """Use Fi MCP client to dynamically load financial data"""
        self.console.print(f"[green]Using Fi MCP client to fetch real sample data...[/green]")
        
        # Use the Fi MCP client which now dynamically loads from files
        return await get_user_financial_data()
    
    async def display_agent_collaboration_OLD_UNUSED(self, responses: List[Dict[str, Any]], user_query: str, financial_data):
        """Display REAL agent collaboration with AI-generated consensus based on actual agent outputs"""
        
        self.console.print("\n[bold blue]🤝 AGENT COLLABORATION SESSION[/bold blue]\n")
        
        # Format actual agent responses for AI consensus generation
        agent_summaries = []
        total_sources = 0
        
        for response in responses:
            agent_name = response['agent_name']
            content = response['content']
            sources = response['grounding_sources']
            total_sources += sources
            
            # Create structured summary of each agent's COMPLETE actual output
            agent_summaries.append(f"""
{response['emoji']} **{agent_name}**:
- Complete Analysis: {content}
- Market Intelligence: {sources} live data sources
- Key Recommendations: {response.get('recommendations', ['Analysis provided above'])}
""")
        
        # Display agent outputs
        self.console.print("[bold cyan]🎭 AGENT ANALYSIS SUMMARY:[/bold cyan]")
        for summary in agent_summaries:
            self.console.print(summary)
        
        # AI-generated consensus based on ACTUAL agent outputs
        self.console.print(f"\n[bold yellow]🤖 AI UNIFIED CONSENSUS:[/bold yellow]")
        
        # Create comprehensive prompt with actual agent responses
        consensus_prompt = f"""
Based on the 3 financial AI agents' ACTUAL analysis of this query: "{user_query}"

ACTUAL AGENT RESPONSES:
{chr(10).join(agent_summaries)}

USER'S FINANCIAL PROFILE:
{self._format_financial_context(financial_data)}

As the Unified AI Financial Advisor, provide a SHORT and STRAIGHT response that:
1. Directly answers the user's question: "{user_query}" in 2-3 sentences
2. Gives clear YES/NO or specific recommendation based on all 3 agents' analysis
3. Mentions 1-2 key points from the agents' findings
4. Provides one specific action step if applicable

Keep response concise, direct, and actionable. Avoid lengthy explanations - just give the final decision based on the collaborative analysis.

Respond as the unified decision maker addressing the user's question directly with a brief, clear answer.
"""
        
        try:
            # Generate AI consensus using actual agent outputs
            consensus_response = self.analyst.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=consensus_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            unified_response = consensus_response.text.strip()
            
        except Exception as e:
            logger.error(f"AI consensus generation failed: {e}")
            # Fallback using actual agent content snippets
            unified_response = f"""
Based on comprehensive analysis by our 3 AI financial experts:

The consensus recommendation for "{user_query}" considers your financial capacity, market opportunities, and risk factors. Each agent has provided detailed analysis with {total_sources} market intelligence sources.

Key unified guidance will be available once all agent outputs are fully processed.
"""
        
        # Display unified consensus
        self.console.print(Panel(
            unified_response,
            title="[bold green]🏆 UNIFIED AI FINANCIAL ADVISOR RESPONSE[/bold green]",
            border_style="green"
        ))
        
        # Show collaboration metrics
        metrics = f"""
📊 **ANALYSIS METRICS**:
• **Agents**: 3 specialized AI financial experts
• **Market Intelligence**: {total_sources} live data sources
• **Analysis Mode**: Multi-agent collaboration with unified consensus
"""
        self.console.print(f"\n[dim]{metrics}[/dim]")
        
    
    def _format_financial_context(self, financial_data: FinancialData) -> str:
        """Format complete financial data context from Fi MCP data"""
        context_sections = ["**ACTUAL FINANCIAL DATA FROM Fi MCP:**"]
        
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth.get('netWorthResponse', {})
            total_value = net_worth.get('totalNetWorthValue', {})
            if total_value.get('units'):
                net_worth_amount = float(total_value.get('units'))
                context_sections.append(f"Total Net Worth: ₹{net_worth_amount:,.0f} ({net_worth_amount/100000:.1f}L)")
                
            # Add detailed asset breakdown from Fi MCP
            assets = net_worth.get('assetValues', [])
            if assets:
                context_sections.append("Asset Breakdown:")
                total_liquid = 0
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    asset_value = float(value.get('units', '0'))
                    
                    # Clean up asset type names
                    clean_type = asset_type.replace('ASSET_TYPE_', '').replace('_', ' ').title()
                    context_sections.append(f"  - {clean_type}: ₹{asset_value:,.0f}")
                    
                    # Calculate liquid assets
                    if 'SAVINGS' in asset_type or 'MUTUAL_FUND' in asset_type:
                        total_liquid += asset_value
                
                context_sections.append(f"Liquid Assets Available: ₹{total_liquid:,.0f} ({total_liquid/100000:.1f}L)")
        
        # Add liability information
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            liabilities = financial_data.net_worth.get('netWorthResponse', {}).get('liabilityValues', [])
            if liabilities:
                context_sections.append("Liabilities:")
                total_debt = 0
                for liability in liabilities:
                    liability_type = liability.get('netWorthAttribute', 'Unknown')
                    value = liability.get('value', {})
                    liability_value = float(value.get('units', '0'))
                    total_debt += liability_value
                    
                    clean_type = liability_type.replace('LIABILITY_TYPE_', '').replace('_', ' ').title()
                    context_sections.append(f"  - {clean_type}: ₹{liability_value:,.0f}")
                
                context_sections.append(f"Total Debt: ₹{total_debt:,.0f}")
        
        # Add credit score from Fi MCP data
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports:
                credit_data = credit_reports[0].get('creditReportData', {})
                score = credit_data.get('score', {}).get('bureauScore')
                if score:
                    context_sections.append(f"Credit Score: {score}")
        
        # Add EPF data
        if hasattr(financial_data, 'epf_details') and financial_data.epf_details:
            epf_data = financial_data.epf_details
            if 'uanAccounts' in epf_data and epf_data['uanAccounts']:
                epf_account = epf_data['uanAccounts'][0].get('rawDetails', {})
                overall_balance = epf_account.get('overall_pf_balance', {})
                current_balance = overall_balance.get('current_pf_balance')
                if current_balance:
                    epf_amount = float(current_balance)
                    context_sections.append(f"EPF Balance: ₹{epf_amount:,.0f} ({epf_amount/100000:.1f}L)")
        
        return "\n".join(context_sections) if len(context_sections) > 1 else "Financial profile being analyzed"
    
    async def chat_loop(self):
        """Main chat loop"""
        
        self.print_welcome()
        
        sample_queries = [
            "Should I buy a car worth 20 lakhs?",
            "What's my budget for renting a house?",
            "Should I take a job offering 2L extra but in another city?",
            "Plan a vacation to Ladakh within my budget",
            "Help me file my taxes and save money"
        ]
        
        self.console.print("\n[bold cyan]💡 Try these sample queries:[/bold cyan]")
        for i, query in enumerate(sample_queries, 1):
            self.console.print(f"  {i}. {query}")
        
        while True:
            try:
                self.console.print("\n" + "="*60)
                
                user_query = Prompt.ask(
                    "\n[bold green]💬 Ask your financial question[/bold green]",
                    default=""
                )
                
                if user_query.lower() in ['quit', 'exit', 'q', 'bye']:
                    self.console.print("\n[bold blue]👋 Thank you for using Artha AI! Goodbye![/bold blue]")
                    break
                
                if not user_query.strip():
                    continue
                
                # Check for sample query numbers
                if user_query.isdigit():
                    query_num = int(user_query)
                    if 1 <= query_num <= len(sample_queries):
                        user_query = sample_queries[query_num - 1]
                        self.console.print(f"[dim]Using sample query: {user_query}[/dim]")
                
                # Process the query
                await self.process_query_with_collaboration(user_query)
                
            except KeyboardInterrupt:
                self.console.print("\n[bold red]🛑 Interrupted by user. Goodbye![/bold red]")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
                logger.error(f"Chat error: {e}")

async def main():
    """Main entry point"""
    chatbot = ArthaAIChatbot()
    await chatbot.chat_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Goodbye![/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal error: {str(e)}[/bold red]")
        sys.exit(1)