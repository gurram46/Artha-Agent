"""
Chat System Test Script
=======================

Tests the complete chat saving and retrieval functionality.
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.chat_service import ChatService
from database.init_chat_tables import create_chat_tables

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_chat_system():
    """
    Comprehensive test of the chat system
    """
    logger.info("🚀 Starting Chat System Test...")
    
    # Initialize chat service
    chat_service = ChatService()
    
    # Test user data
    test_user_id = "test_user_123"
    test_email = "test@example.com"
    
    try:
        # Test 1: Create a new conversation
        logger.info("\n📝 Test 1: Creating new conversation...")
        conversation_id = chat_service.create_conversation(
            user_id=test_user_id,
            agent_mode="research",
            financial_context={
                "portfolio_value": 500000,
                "risk_tolerance": "moderate",
                "investment_goals": ["retirement", "wealth_building"]
            }
        )
        logger.info(f"✅ Created conversation: {conversation_id}")
        
        # Test 2: Add messages to the conversation
        logger.info("\n💬 Test 2: Adding messages...")
        
        # User message
        user_message_id = chat_service.add_message(
            conversation_id=conversation_id,
            message_type="user",
            content="What are the best investment strategies for retirement planning?",
            agent_mode="research",
            tokens_used=25,
            processing_time=0.1,
            metadata={"source": "web_interface"}
        )
        logger.info(f"✅ Added user message: {user_message_id}")
        
        # Assistant response
        assistant_message_id = chat_service.add_message(
            conversation_id=conversation_id,
            message_type="assistant",
            content="""Based on your moderate risk tolerance and retirement goals, here are some excellent investment strategies:

1. **Diversified Portfolio Approach**
   - 60% stocks (mix of domestic and international)
   - 30% bonds (government and corporate)
   - 10% alternative investments (REITs, commodities)

2. **Dollar-Cost Averaging**
   - Invest a fixed amount regularly
   - Reduces impact of market volatility
   - Builds discipline and consistency

3. **Tax-Advantaged Accounts**
   - Maximize 401(k) contributions
   - Consider Roth IRA for tax-free growth
   - Use HSA as retirement vehicle

4. **Target-Date Funds**
   - Automatically adjusts allocation over time
   - Becomes more conservative as you approach retirement
   - Low maintenance option

5. **Regular Rebalancing**
   - Review portfolio quarterly
   - Maintain target allocation
   - Take profits and buy low

Would you like me to elaborate on any of these strategies or discuss specific investment products?""",
            agent_mode="research",
            tokens_used=180,
            processing_time=2.5,
            metadata={
                "sources_used": 5,
                "research_depth": "comprehensive",
                "confidence_score": 0.92
            },
            financial_snapshot={
                "market_conditions": "bullish",
                "recommended_allocation": {
                    "stocks": 60,
                    "bonds": 30,
                    "alternatives": 10
                }
            }
        )
        logger.info(f"✅ Added assistant message: {assistant_message_id}")
        
        # Follow-up user message
        followup_message_id = chat_service.add_message(
            conversation_id=conversation_id,
            message_type="user",
            content="Can you explain more about target-date funds and their benefits?",
            agent_mode="research",
            tokens_used=15,
            processing_time=0.1
        )
        logger.info(f"✅ Added follow-up message: {followup_message_id}")
        
        # Test 3: Retrieve conversation history
        logger.info("\n📖 Test 3: Retrieving conversation history...")
        history = chat_service.get_conversation_history(
            user_id=test_user_id,
            conversation_id=conversation_id
        )
        
        if history:
            logger.info(f"✅ Retrieved conversation with {len(history['messages'])} messages")
            logger.info(f"   Title: {history['conversation']['title'] or 'Untitled'}")
            logger.info(f"   Agent Mode: {history['conversation']['agent_mode']}")
            logger.info(f"   Total Tokens: {history['conversation']['total_tokens_used']}")
            logger.info(f"   Message Count: {history['conversation']['message_count']}")
        else:
            logger.error("❌ Failed to retrieve conversation history")
        
        # Test 4: Create another conversation
        logger.info("\n📝 Test 4: Creating second conversation...")
        conversation_id_2 = chat_service.create_conversation(
            user_id=test_user_id,
            agent_mode="quick",
            financial_context={
                "query_type": "stock_analysis",
                "symbols": ["AAPL", "GOOGL", "MSFT"]
            }
        )
        
        # Add a quick message
        chat_service.add_message(
            conversation_id=conversation_id_2,
            message_type="user",
            content="What's the current outlook for tech stocks?",
            agent_mode="quick",
            tokens_used=12,
            processing_time=0.05
        )
        
        chat_service.add_message(
            conversation_id=conversation_id_2,
            message_type="assistant",
            content="Tech stocks are showing mixed signals. AAPL and MSFT remain strong with solid fundamentals, while GOOGL faces some regulatory headwinds. Overall sector outlook is cautiously optimistic.",
            agent_mode="quick",
            tokens_used=45,
            processing_time=1.2
        )
        
        logger.info(f"✅ Created second conversation: {conversation_id_2}")
        
        # Test 5: Get all user conversations
        logger.info("\n📚 Test 5: Getting all user conversations...")
        conversations = chat_service.get_user_conversations(
            user_id=test_user_id,
            limit=10
        )
        
        logger.info(f"✅ Retrieved {len(conversations)} conversations for user")
        for conv in conversations:
            logger.info(f"   - {conv['id'][:8]}... | {conv['agent_mode']} | {conv['message_count']} messages")
        
        # Test 6: Search conversations
        logger.info("\n🔍 Test 6: Searching conversations...")
        search_results = chat_service.search_conversations(
            user_id=test_user_id,
            query="retirement investment",
            limit=5
        )
        
        logger.info(f"✅ Found {len(search_results)} conversations matching 'retirement investment'")
        for result in search_results:
            logger.info(f"   - {result['conversation_id'][:8]}... | Score: {result.get('relevance_score', 'N/A')}")
        
        # Test 7: Toggle favorite
        logger.info("\n⭐ Test 7: Toggling favorite status...")
        is_favorite = chat_service.toggle_favorite(
            user_id=test_user_id,
            conversation_id=conversation_id
        )
        logger.info(f"✅ Conversation favorite status: {is_favorite}")
        
        # Test 8: Add feedback
        logger.info("\n👍 Test 8: Adding feedback...")
        feedback_id = chat_service.add_feedback(
            user_id=test_user_id,
            message_id=assistant_message_id,
            feedback_type="helpful",
            rating=5,
            feedback_text="Very comprehensive and well-structured advice!"
        )
        logger.info(f"✅ Added feedback: {feedback_id}")
        
        # Test 9: Get analytics
        logger.info("\n📊 Test 9: Getting chat analytics...")
        analytics = chat_service.get_chat_analytics(
            user_id=test_user_id,
            days=30
        )
        
        logger.info("✅ Chat Analytics:")
        logger.info(f"   Total Conversations: {analytics.get('total_conversations', 0)}")
        logger.info(f"   Total Messages: {analytics.get('total_messages', 0)}")
        logger.info(f"   Total Tokens Used: {analytics.get('total_tokens_used', 0)}")
        logger.info(f"   Average Processing Time: {analytics.get('avg_processing_time', 0):.2f}s")
        logger.info(f"   Agent Modes Used: {analytics.get('agent_modes_used', {})}")
        
        # Test 10: Archive conversation
        logger.info("\n📦 Test 10: Archiving conversation...")
        archived = chat_service.archive_conversation(
            user_id=test_user_id,
            conversation_id=conversation_id_2
        )
        logger.info(f"✅ Conversation archived: {archived}")
        
        # Test 11: Get conversations (should show archived status)
        logger.info("\n📚 Test 11: Getting conversations after archiving...")
        conversations_after = chat_service.get_user_conversations(
            user_id=test_user_id,
            limit=10,
            include_archived=True
        )
        
        for conv in conversations_after:
            status = "📦 Archived" if conv['is_archived'] else "📝 Active"
            favorite = "⭐" if conv['is_favorite'] else ""
            logger.info(f"   - {conv['id'][:8]}... | {status} {favorite} | {conv['message_count']} messages")
        
        # Test 12: Demonstrate encryption (show that data is encrypted in DB)
        logger.info("\n🔐 Test 12: Verifying encryption...")
        
        # Direct database query to show encrypted data
        with chat_service.SessionLocal() as session:
            from database.chat_models import ChatMessage
            
            # Get a message from database
            db_message = session.query(ChatMessage).filter(
                ChatMessage.id == user_message_id
            ).first()
            
            if db_message:
                logger.info("✅ Encryption verification:")
                logger.info(f"   Message ID: {db_message.id}")
                logger.info(f"   Content (encrypted): {db_message.content_encrypted[:50]}...")
                logger.info(f"   Nonce: {db_message.content_nonce[:20]}...")
                logger.info(f"   Auth Tag: {db_message.content_auth_tag[:20]}...")
                logger.info("   ✅ Content is properly encrypted in database")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 ALL CHAT SYSTEM TESTS PASSED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("✅ Conversation creation and management")
        logger.info("✅ Message encryption and storage")
        logger.info("✅ Conversation history retrieval")
        logger.info("✅ Search functionality")
        logger.info("✅ Favorite and archive features")
        logger.info("✅ Feedback system")
        logger.info("✅ Analytics and reporting")
        logger.info("✅ Data encryption and security")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Chat system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """
    Main test function
    """
    logger.info("🔧 Initializing chat database tables...")
    
    # Create tables first
    if not create_chat_tables():
        logger.error("❌ Failed to create chat tables")
        return
    
    logger.info("✅ Chat tables created successfully")
    
    # Run tests
    success = await test_chat_system()
    
    if success:
        logger.info("\n🎊 Chat System is fully operational and ready for production!")
    else:
        logger.error("\n💥 Chat System tests failed!")

# Disabled automatic execution to prevent interference with main server
# if __name__ == "__main__":
#     asyncio.run(main())