#!/usr/bin/env python3
"""
Interactive Investment Agent Runner
This script allows you to have a conversation with the investment agent locally.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    from investment_agent.agent import root_agent
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Part, UserContent
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed the required dependencies:")
    print("pip install google-adk google-genai python-dotenv")
    sys.exit(1)


async def interactive_chat():
    """Start an interactive chat session with the investment agent."""
    
    # Load environment variables
    load_dotenv()
    
    print("🏦 Investment Agent - Interactive Chat")
    print("=" * 50)
    print("Welcome to your personal Indian investment advisor!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("=" * 50)
    
    try:
        # Create an in-memory runner
        runner = InMemoryRunner(agent=root_agent)
        
        # Create a session
        session = runner.session_service.create_session(
            app_name=runner.app_name, 
            user_id="interactive_user"
        )
        
        print(f"✅ Chat session started!")
        print("\n💡 Try asking about:")
        print("   • Investment strategies for Indian markets")
        print("   • SIP recommendations")
        print("   • Risk assessment")
        print("   • Tax-saving investments")
        print("   • Portfolio diversification")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for using Investment Agent. Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\n🤖 Investment Agent:", end=" ")
                
                # Send the query to the agent
                content = UserContent(parts=[Part(text=user_input)])
                
                async for event in runner.run_async(
                    user_id=session.user_id,
                    session_id=session.id,
                    new_message=content,
                ):
                    if event.content.parts and event.content.parts[0].text:
                        chunk = event.content.parts[0].text
                        print(chunk, end="", flush=True)
                
                print("\n" + "-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error processing your message: {e}")
                print("Please try again or type 'quit' to exit.")
                
    except Exception as e:
        print(f"❌ Error starting investment agent: {e}")
        print("Please check your environment configuration and dependencies.")
        return False
    
    return True


def main():
    """Main function to run the interactive investment agent."""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Please create one based on .env.example")
        print("For local testing, you may need to set up Google Cloud credentials.")
        print()
        
        # Ask if user wants to continue anyway
        response = input("Do you want to continue anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Please set up your .env file and try again.")
            return
        
    try:
        # Run the async chat
        asyncio.run(interactive_chat())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()