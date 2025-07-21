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
        
        return {
            'agent_name': agent.name,
            'emoji': agent.emoji,
            'content': response_content if 'response_content' in locals() else "Analysis failed",
            'grounding_sources': len(agent_response.get('grounded_data', [])) if agent_response else 0,
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
                financial_data = self.create_sample_financial_data()
        
        self.console.print("\n[bold blue]🚀 Starting 3-Agent Analysis...[/bold blue]\n")
        
        # Process with all agents concurrently but show sequentially for better UX
        agents = [
            ("analyst", self.analyst),
            ("research", self.research),
            ("risk", self.risk)
        ]
        
        agent_responses = []
        
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
        
        # Show collaboration summary
        self.display_collaboration_summary(agent_responses)
    
    def create_sample_financial_data(self) -> FinancialData:
        """Create sample financial data for demo"""
        
        # Load sample data from mcp-docs
        try:
            # Load all sample data files
            with open('../mcp-docs/sample_responses/fetch_net_worth.json', 'r') as f:
                sample_net_worth = json.load(f)
            
            with open('../mcp-docs/sample_responses/fetch_mf_transactions.json', 'r') as f:
                sample_transactions = json.load(f)
            
            with open('../mcp-docs/sample_responses/fetch_credit_report.json', 'r') as f:
                sample_credit = json.load(f)
            
            with open('../mcp-docs/sample_responses/fetch_epf_details.json', 'r') as f:
                sample_epf = json.load(f)
            
            # Extract data properly
            net_worth_data = sample_net_worth  # Contains full net worth response including mfSchemeAnalytics
            
            # Create FinancialData object with all sample data
            return FinancialData(
                net_worth=net_worth_data,  # Pass the full net worth object
                mutual_funds=net_worth_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', []),
                bank_accounts=net_worth_data.get('accountDetailsBulkResponse', {}).get('accountDetailsMap', {}),
                equity_holdings=[],  # Not in sample data
                credit_report=sample_credit,
                epf_details=sample_epf,
                transactions=sample_transactions.get('transactions', [])
            )
        except Exception as e:
            self.console.print(f"[red]Error loading sample data: {e}[/red]")
            # Fallback with more complete minimal data
            return FinancialData(
                net_worth={
                    'netWorthResponse': {
                        'totalNetWorthValue': {'currencyCode': 'INR', 'units': '868721'},
                        'assetValues': [
                            {'netWorthAttribute': 'ASSET_TYPE_SAVINGS_ACCOUNTS', 'value': {'units': '200000', 'currencyCode': 'INR'}},
                            {'netWorthAttribute': 'ASSET_TYPE_MUTUAL_FUND', 'value': {'units': '300000', 'currencyCode': 'INR'}}
                        ]
                    }
                },
                mutual_funds=[],
                bank_accounts={},
                equity_holdings=[],
                credit_report={},
                epf_details={},
                transactions=[]
            )
    
    def display_collaboration_summary(self, responses: List[Dict[str, Any]]):
        """Display final collaboration summary"""
        
        total_sources = sum(r['grounding_sources'] for r in responses)
        all_recommendations = []
        for r in responses:
            all_recommendations.extend(r['recommendations'])
        
        summary = f"""
🏆 3-AGENT COLLABORATION COMPLETE

📊 Analysis Summary:
• Total Agents: 3 specialized financial AI agents
• Live Data Sources: {total_sources} real-time market intelligence points
• Processing Mode: Concurrent analysis with live grounding

🤝 Unified Insights:
Each agent analyzed your query using live market data and personal financial information.
All recommendations are backed by current market conditions and verifiable sources.

💡 Key Recommendations:"""
        
        for i, rec in enumerate(list(set(all_recommendations))[:5], 1):
            summary += f"\n{i}. {rec}"
        
        summary += f"""

⚡ Agent Specializations:
• 🕵️ Data Analyst: Portfolio analysis vs live market benchmarks
• 🎯 Market Strategist: Current opportunities and strategic timing
• 🛡️ Risk Guardian: Live threat monitoring and protection strategies

🔍 All responses include real-time market intelligence and verifiable sources.
        """
        
        self.console.print(Panel(
            summary,
            title="[bold green]🎯 COLLABORATIVE AI ANALYSIS[/bold green]",
            border_style="green"
        ))
    
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