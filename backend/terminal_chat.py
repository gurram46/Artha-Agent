#!/usr/bin/env python3
"""
Artha AI Terminal Chat Client
Real-time streaming collaboration with live agent messages
"""

import requests
import json
import sys
import time
from datetime import datetime
from colorama import init, Fore, Back, Style
import threading
import os

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class TerminalChatClient:
    """
    🚀 Revolutionary Terminal Chat Client
    
    Features:
    - Real-time streaming of all agent messages
    - Color-coded agent responses
    - Live collaboration visualization
    - Beautiful terminal UI
    """
    
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.session = requests.Session()
        
        # Color schemes for different agents
        self.colors = {
            'analyst': Fore.CYAN,
            'research': Fore.GREEN, 
            'risk_management': Fore.YELLOW,
            'system': Fore.MAGENTA,
            'collaboration': Fore.BLUE,
            'user': Fore.WHITE,
            'error': Fore.RED,
            'success': Fore.GREEN,
            'info': Fore.BLUE
        }
        
        # Agent display names
        self.agent_names = {
            'analyst': '🕵️  Data Analyst',
            'research': '🎯 Research Strategist', 
            'risk_management': '🛡️  Risk Guardian'
        }
    
    def print_banner(self):
        """Display the revolutionary banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW}🏆 ARTHA AI - REVOLUTIONARY REAL-TIME COLLABORATION TERMINAL{Fore.CYAN}              ║
║                                                                              ║
║  {Fore.GREEN}Watch three AI financial experts collaborate in real-time!{Fore.CYAN}                ║
║  {Fore.WHITE}Every thought, every conflict, every decision - streamed live!{Fore.CYAN}            ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.BLUE}🚀 Framework Version: 4-stage-collaboration-v1.0{Style.RESET_ALL}
{Fore.GREEN}💎 3 Expert Agents Ready: Data Analyst, Research Strategist, Risk Guardian{Style.RESET_ALL}
{Fore.YELLOW}⚡ Real-time Streaming: Active{Style.RESET_ALL}
"""
        print(banner)
    
    def print_separator(self, title="", char="─", length=80):
        """Print a beautiful separator"""
        if title:
            title_len = len(title)
            padding = (length - title_len - 2) // 2
            line = f"{char * padding} {title} {char * padding}"
            if len(line) < length:
                line += char
        else:
            line = char * length
        
        print(f"{Fore.BLUE}{line}{Style.RESET_ALL}")
    
    def check_server_health(self):
        """Check if the server is running"""
        try:
            response = self.session.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"{Fore.GREEN}✅ Server Status: {health_data.get('status', 'unknown')}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}🔗 Connected to: {self.server_url}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Server responded with status: {response.status_code}{Style.RESET_ALL}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Cannot connect to server: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Make sure the server is running: python3 main.py{Style.RESET_ALL}")
            return False
    
    def format_message(self, message_type, title, data):
        """Format different types of messages with colors and styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if message_type == "collaboration_start":
            return f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║ {Fore.YELLOW}🏆 {title}{Fore.CYAN}
║ {Fore.WHITE}Session: {data.get('session_id', 'N/A')}{Fore.CYAN}
║ {Fore.WHITE}Query: "{data.get('user_query', 'N/A')}"{Fore.CYAN}
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        
        elif message_type == "stage_1_start":
            return f"\n{Fore.BLUE}🎯 {title}{Style.RESET_ALL}\n{Fore.CYAN}{data.get('description', '')}{Style.RESET_ALL}\n"
        
        elif message_type == "stage_2_start":
            return f"\n{Fore.YELLOW}⚡ {title}{Style.RESET_ALL}\n{Fore.CYAN}{data.get('description', '')}{Style.RESET_ALL}\n"
        
        elif message_type == "stage_3_start":
            return f"\n{Fore.MAGENTA}🔥 {title}{Style.RESET_ALL}\n{Fore.CYAN}{data.get('description', '')}{Style.RESET_ALL}\n"
        
        elif message_type == "stage_4_start":
            return f"\n{Fore.GREEN}🤝 {title}{Style.RESET_ALL}\n{Fore.CYAN}{data.get('description', '')}{Style.RESET_ALL}\n"
        
        elif message_type == "agent_thinking":
            agent_key = data.get('agent', 'unknown')
            agent_color = self.colors.get(agent_key, Fore.WHITE)
            agent_name = self.agent_names.get(agent_key, agent_key)
            return f"{agent_color}[{timestamp}] {agent_name}: {data.get('thinking', '')}{Style.RESET_ALL}"
        
        elif message_type == "agent_completed":
            agent_key = data.get('agent', 'unknown')
            agent_color = self.colors.get(agent_key, Fore.WHITE)
            agent_name = self.agent_names.get(agent_key, agent_key)
            confidence = data.get('confidence', 0) * 100
            analysis = data.get('analysis_content', 'Analysis completed')
            
            # Format analysis content with proper line breaks
            if len(analysis) > 800:
                # For very long content, show first 800 chars 
                display_analysis = analysis[:800] + "...\n\n[Complete analysis in final summary below]"
            else:
                display_analysis = analysis
            
            # Split into lines and wrap long lines
            lines = []
            for line in display_analysis.split('\n'):
                if len(line) > 70:
                    # Wrap long lines
                    while len(line) > 70:
                        lines.append(line[:70])
                        line = line[70:]
                    if line:
                        lines.append(line)
                else:
                    lines.append(line)
            
            # Format the output
            output = f"\n{agent_color}╭─ {agent_name} - Analysis Complete ─╮\n"
            output += f"│ Confidence: {confidence:.0f}%\n│ \n"
            
            for line in lines[:30]:  # Show max 30 lines
                output += f"│ {line}\n"
            
            if len(lines) > 30:
                output += f"│ ... ({len(lines) - 30} more lines in full summary below)\n"
            
            output += f"╰─{'─' * (len(agent_name) + 25)}─╯{Style.RESET_ALL}\n"
            
            return output
        
        elif message_type == "conflicts_detected":
            conflict_count = data.get('conflict_count', 0)
            conflicts = data.get('conflicts', [])
            
            output = f"\n{Fore.RED}🔍 {conflict_count} Conflicts Detected{Style.RESET_ALL}\n"
            for i, conflict in enumerate(conflicts, 1):
                output += f"{Fore.YELLOW}   {i}. {conflict.get('type', 'unknown')}: {conflict.get('description', '')}{Style.RESET_ALL}\n"
            
            return output
        
        elif message_type == "no_conflicts":
            return f"\n{Fore.GREEN}✅ {title}{Style.RESET_ALL}\n{Fore.CYAN}{data.get('description', '')}{Style.RESET_ALL}\n"
        
        elif message_type == "discussion_message":
            speaker = data.get('speaker', 'Agent')
            message = data.get('message', '')
            round_num = data.get('round', 1)
            confidence = data.get('confidence', 0)
            
            # Determine color based on speaker
            if 'Data Analyst' in speaker:
                color = self.colors['analyst']
                icon = '🕵️ '
            elif 'Research Strategist' in speaker:
                color = self.colors['research'] 
                icon = '🎯'
            elif 'Risk Guardian' in speaker:
                color = self.colors['risk_management']
                icon = '🛡️ '
            else:
                color = self.colors['collaboration']
                icon = '💬'
            
            conf_text = f" (Confidence: {confidence * 100:.0f}%)" if confidence > 0 else ""
            
            return f"""
{color}╭─ {icon} {speaker} - Round {round_num}{conf_text} ─╮
│ 
│ {message}
│ 
╰─{"─" * (len(speaker) + 20)}─╯{Style.RESET_ALL}
"""
        
        elif message_type == "collaboration_complete":
            summary = data.get('collaboration_summary', '')
            agent_insights = data.get('agent_insights', {})
            conflicts_resolved = data.get('conflicts_resolved', 0)
            overall_confidence = data.get('overall_confidence', 0) * 100
            
            # Format the complete summary for better readability
            formatted_summary = summary.replace('\\n', '\n').replace('\\\\n', '\n')
            
            output = f"""
{Fore.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗
║ 🏆 REVOLUTIONARY COLLABORATION COMPLETE! 
║ 
║ Overall Confidence: {overall_confidence:.0f}%
║ Conflicts Resolved: {conflicts_resolved}
║ 
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.WHITE}═══════════════════════════ COMPLETE ANALYSIS RESULTS ═══════════════════════════{Style.RESET_ALL}

{Fore.CYAN}{formatted_summary}{Style.RESET_ALL}

{Fore.WHITE}═══════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}

{Fore.BLUE}📊 Agent Performance Summary:{Style.RESET_ALL}
"""
            
            for agent_key, insights in agent_insights.items():
                agent_name = insights.get('agent_name', agent_key)
                confidence = insights.get('confidence', 0) * 100
                color = self.colors.get(agent_key, Fore.WHITE)
                output += f"{color}   • {agent_name}: {confidence:.0f}% confidence{Style.RESET_ALL}\n"
            
            return output
        
        elif message_type == "connection_start":
            return f"{Fore.GREEN}🔗 {title} - Query: {data.get('query', 'N/A')}{Style.RESET_ALL}\n"
        
        elif message_type == "error":
            error_msg = data.get('error', 'Unknown error')
            return f"\n{Fore.RED}❌ Error: {error_msg}{Style.RESET_ALL}\n"
        
        else:
            return f"\n{Fore.WHITE}[{timestamp}] {title}: {data}{Style.RESET_ALL}\n"
    
    def stream_chat(self, user_message):
        """Stream chat with real-time agent collaboration"""
        print(f"\n{Fore.WHITE}You: {user_message}{Style.RESET_ALL}")
        self.print_separator("INITIATING 4-STAGE COLLABORATION")
        
        try:
            # Make streaming request with better headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            response = self.session.post(
                f"{self.server_url}/api/chat-stream",
                json={"message": user_message, "user_id": "terminal_user"},
                headers=headers,
                stream=True,
                timeout=120  # Increased timeout
            )
            
            if response.status_code != 200:
                print(f"{Fore.RED}❌ Request failed with status: {response.status_code}{Style.RESET_ALL}")
                if response.text:
                    print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}✅ Connected to collaboration stream...{Style.RESET_ALL}\n")
            
            # Process streaming response with better chunk handling
            buffer = ""
            message_count = 0
            
            try:
                # Use iter_lines instead of iter_content for better line handling
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.strip():
                        line = line.strip()
                        
                        if line.startswith('data: '):
                            try:
                                json_str = line[6:].strip()  # Remove 'data: ' prefix and strip whitespace
                                if json_str:  # Skip empty data lines
                                    # Clean any extra newlines or characters
                                    json_str = json_str.split('\n')[0]  # Take only first line if multiple
                                    
                                    # Parse JSON
                                    json_data = json.loads(json_str)
                                    message_type = json_data.get('type', '')
                                    title = json_data.get('title', '')
                                    data = json_data.get('data', {})
                                    
                                    # Format and display the message
                                    formatted_message = self.format_message(message_type, title, data)
                                    print(formatted_message)
                                    
                                    message_count += 1
                                    
                                    # Add small delay for better readability
                                    if message_type in ['agent_thinking', 'agent_completed', 'discussion_message']:
                                        time.sleep(0.1)
                                        
                            except json.JSONDecodeError as e:
                                # Try to extract just the JSON part if there's extra data
                                try:
                                    json_str = line[6:].strip()
                                    # Find the end of the JSON object
                                    brace_count = 0
                                    json_end = -1
                                    for i, char in enumerate(json_str):
                                        if char == '{':
                                            brace_count += 1
                                        elif char == '}':
                                            brace_count -= 1
                                            if brace_count == 0:
                                                json_end = i + 1
                                                break
                                    
                                    if json_end > 0:
                                        clean_json = json_str[:json_end]
                                        json_data = json.loads(clean_json)
                                        message_type = json_data.get('type', '')
                                        title = json_data.get('title', '')
                                        data = json_data.get('data', {})
                                        
                                        formatted_message = self.format_message(message_type, title, data)
                                        print(formatted_message)
                                        message_count += 1
                                    else:
                                        print(f"{Fore.YELLOW}⚠️  Could not parse JSON: {str(e)}{Style.RESET_ALL}")
                                except:
                                    print(f"{Fore.YELLOW}⚠️  JSON decode warning: {str(e)}{Style.RESET_ALL}")
                                    
                            except Exception as e:
                                print(f"{Fore.RED}❌ Stream processing error: {str(e)}{Style.RESET_ALL}")
            
            except Exception as stream_error:
                print(f"{Fore.RED}❌ Stream reading error: {str(stream_error)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Messages received before error: {message_count}{Style.RESET_ALL}")
            
            self.print_separator("COLLABORATION COMPLETE")
            print(f"{Fore.BLUE}📊 Total messages processed: {message_count}{Style.RESET_ALL}")
            
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}❌ Request timeout - The collaboration is taking longer than expected{Style.RESET_ALL}")
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}❌ Connection error - Please check if the server is running{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Network error: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔄 Attempting fallback to regular chat...{Style.RESET_ALL}")
            self.fallback_chat(user_message)
        except Exception as e:
            print(f"{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔄 Attempting fallback to regular chat...{Style.RESET_ALL}")
            self.fallback_chat(user_message)
    
    def fallback_chat(self, user_message):
        """Fallback to regular chat if streaming fails"""
        try:
            print(f"{Fore.BLUE}📡 Using regular collaboration API...{Style.RESET_ALL}")
            
            response = self.session.post(
                f"{self.server_url}/api/chat",
                json={"message": user_message, "user_id": "terminal_user"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display the collaboration summary
                summary = result.get('collaboration_summary', 'No summary available')
                print(f"\n{Fore.GREEN}🏆 Collaboration Result:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{summary}{Style.RESET_ALL}")
                
                # Display agent insights
                agent_insights = result.get('agent_insights', {})
                if agent_insights:
                    print(f"\n{Fore.BLUE}📊 Agent Insights:{Style.RESET_ALL}")
                    for agent_key, insights in agent_insights.items():
                        agent_name = insights.get('agent_name', agent_key)
                        confidence = insights.get('confidence', 0) * 100
                        findings = insights.get('key_findings', [])
                        color = self.colors.get(agent_key, Fore.WHITE)
                        
                        print(f"{color}   • {agent_name}: {confidence:.0f}% confidence{Style.RESET_ALL}")
                        for finding in findings[:2]:  # Show top 2 findings
                            print(f"     - {finding}")
                
                # Display conflict information
                conflicts_resolved = result.get('conflicts_resolved', 0)
                if conflicts_resolved > 0:
                    print(f"\n{Fore.YELLOW}⚡ Conflicts resolved: {conflicts_resolved}{Style.RESET_ALL}")
                
            else:
                print(f"{Fore.RED}❌ Fallback request failed with status: {response.status_code}{Style.RESET_ALL}")
                
        except Exception as fallback_error:
            print(f"{Fore.RED}❌ Fallback error: {str(fallback_error)}{Style.RESET_ALL}")
    
    def run(self):
        """Main chat loop"""
        self.print_banner()
        
        # Check server connection
        if not self.check_server_health():
            return
        
        print(f"\n{Fore.GREEN}🚀 Ready for revolutionary collaboration!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Type your financial questions and watch the agents collaborate in real-time{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📝 Type 'quit', 'exit', or 'q' to end the session{Style.RESET_ALL}")
        
        # Sample questions
        print(f"\n{Fore.BLUE}💰 Sample Questions:{Style.RESET_ALL}")
        samples = [
            "How is my portfolio performing?",
            "Can I buy a car worth 5 crores?", 
            "Should I invest ₹50,000 in mutual funds?",
            "What are the major risks in my financial situation?",
            "How should I rebalance my portfolio?"
        ]
        
        for i, sample in enumerate(samples, 1):
            print(f"{Fore.CYAN}   {i}. {sample}{Style.RESET_ALL}")
        
        print()
        
        try:
            while True:
                # Get user input
                user_input = input(f"\n{Fore.GREEN}💬 Your Question: {Style.RESET_ALL}").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q', '']:
                    print(f"\n{Fore.YELLOW}👋 Thank you for using Artha AI! Goodbye!{Style.RESET_ALL}")
                    break
                
                # Process the question
                start_time = time.time()
                self.stream_chat(user_input)
                end_time = time.time()
                
                print(f"\n{Fore.BLUE}⏱️  Total collaboration time: {end_time - start_time:.2f} seconds{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Session interrupted. Goodbye!{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Chat error: {str(e)}{Style.RESET_ALL}")

def main():
    """Main entry point"""
    # Check if colorama is available
    try:
        import colorama
    except ImportError:
        print("Installing colorama for colored output...")
        os.system("pip install colorama")
        import colorama
    
    # Create and run the chat client
    client = TerminalChatClient()
    client.run()

if __name__ == "__main__":
    main()