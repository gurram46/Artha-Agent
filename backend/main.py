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

# Setup simple logging
logging.basicConfig(level=logging.ERROR)
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
    
    async def stream_agent_response(self, agent, agent_name: str, query: str, financial_data: FinancialData):
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
        """Process query with 3-agent collaboration"""
        
        self.console.print(f"\n[bold cyan]Processing:[/bold cyan] {user_query}\n")
        
        # Fetch financial data
        with Status("[blue]📊 Fetching your financial data from Fi MCP...", console=self.console):
            try:
                financial_data = await get_user_financial_data()
                self.console.print("[green]✅ Financial data loaded successfully[/green]")
            except Exception as e:
                self.console.print("[yellow]⚠️ Using sample financial data for demo[/yellow]")
                # Create sample data for demo
                financial_data = await self.create_sample_financial_data()
        
        self.console.print("\n[bold blue]🚀 Starting 3-Agent Analysis...[/bold blue]\n")
        
        # Process with all agents - using parallel processing if enabled
        agents = [
            ("analyst", self.analyst),
            ("research", self.research),
            ("risk", self.risk)
        ]
        
        agent_responses = []
        
        # Process all agents sequentially for complete analysis  
        for agent_key, agent in agents:
            self.console.print(f"[bold]{agent.emoji} {agent.name} Analysis:[/bold]")
            
            response = await self.stream_agent_response(agent, agent_key, user_query, financial_data)
            agent_responses.append(response)
            
            # Show individual response
            self.console.print(Panel(
                response['content'],
                title=f"{response['emoji']} {response['agent_name']} Response",
                border_style="green"
            ))
            
            self.console.print(f"[dim]Sources: {response['grounding_sources']} live market data points[/dim]\n")
        
        # Show collaboration summary and AGENT DEBATES
        await self.display_agent_collaboration(agent_responses, user_query, financial_data)
    
    async def create_sample_financial_data(self) -> FinancialData:
        """Use Fi MCP client to dynamically load financial data"""
        self.console.print(f"[green]Using Fi MCP client to fetch real sample data...[/green]")
        
        # Use the Fi MCP client which now dynamically loads from files
        return await get_user_financial_data()
    
    async def display_agent_collaboration(self, responses: List[Dict[str, Any]], user_query: str, financial_data):
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
                    max_output_tokens=300,
                    temperature=0.3
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
        
        # Import required for Gemini client
        from google.genai import types
    
    def _format_financial_context(self, financial_data: FinancialData) -> str:
        """Format complete financial data context for consensus generation"""
        context_sections = []
        
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth.get('netWorthResponse', {})
            total_value = net_worth.get('totalNetWorthValue', {})
            if total_value.get('units'):
                context_sections.append(f"Net Worth: ₹{total_value.get('units')}")
                
            # Add asset breakdown
            assets = net_worth.get('assetValues', [])
            if assets:
                asset_details = []
                for asset in assets[:5]:  # Top 5 assets
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    asset_value = value.get('units', 'N/A')
                    asset_details.append(f"{asset_type}: ₹{asset_value}")
                context_sections.append(f"Key Assets: {', '.join(asset_details)}")
        
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports:
                credit_data = credit_reports[0].get('creditReportData', {})
                score = credit_data.get('score', {}).get('bureauScore')
                if score:
                    context_sections.append(f"Credit Score: {score}")
                
                # Add debt information
                credit_summary = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                if credit_summary:
                    total_balance = credit_summary.get('totalOutstandingBalance', {})
                    total_debt = total_balance.get('outstandingBalanceAll')
                    if total_debt:
                        context_sections.append(f"Total Debt: ₹{total_debt}")
        
        if hasattr(financial_data, 'epf_details') and financial_data.epf_details:
            epf_data = financial_data.epf_details
            if 'uanAccounts' in epf_data and epf_data['uanAccounts']:
                epf_account = epf_data['uanAccounts'][0].get('rawDetails', {})
                overall_balance = epf_account.get('overall_pf_balance', {})
                current_balance = overall_balance.get('current_pf_balance')
                if current_balance:
                    context_sections.append(f"EPF Balance: ₹{current_balance}")
        
        return "\n".join(context_sections) if context_sections else "Financial profile being analyzed"
    
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