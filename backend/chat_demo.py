"""
Chat System Demo for Artha AI
=============================

Demonstrates chat saving functionality using the existing cache infrastructure.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatManager:
    """
    Simple chat manager that demonstrates chat saving functionality
    """
    
    def __init__(self):
        self.conversations = {}
        self.message_counter = 0
        
    def create_conversation(self, user_id: str, agent_mode: str = "research") -> str:
        """Create a new conversation"""
        conversation_id = f"conv_{len(self.conversations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "user_id": user_id,
            "agent_mode": agent_mode,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "is_active": True,
            "is_favorite": False,
            "total_tokens": 0
        }
        
        logger.info(f"✅ Created conversation: {conversation_id}")
        return conversation_id
    
    def add_message(self, conversation_id: str, message_type: str, content: str, 
                   tokens_used: int = 0, metadata: Dict = None) -> str:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        self.message_counter += 1
        message_id = f"msg_{self.message_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        message = {
            "id": message_id,
            "type": message_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "tokens_used": tokens_used,
            "metadata": metadata or {}
        }
        
        self.conversations[conversation_id]["messages"].append(message)
        self.conversations[conversation_id]["total_tokens"] += tokens_used
        
        logger.info(f"✅ Added {message_type} message: {message_id}")
        return message_id
    
    def get_conversation_history(self, conversation_id: str) -> Dict:
        """Get conversation history"""
        if conversation_id not in self.conversations:
            return None
        
        return self.conversations[conversation_id]
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        user_conversations = []
        for conv in self.conversations.values():
            if conv["user_id"] == user_id:
                # Return summary without full messages
                summary = {
                    "id": conv["id"],
                    "agent_mode": conv["agent_mode"],
                    "created_at": conv["created_at"],
                    "message_count": len(conv["messages"]),
                    "total_tokens": conv["total_tokens"],
                    "is_favorite": conv["is_favorite"]
                }
                user_conversations.append(summary)
        
        return user_conversations
    
    def toggle_favorite(self, conversation_id: str) -> bool:
        """Toggle favorite status"""
        if conversation_id in self.conversations:
            current_status = self.conversations[conversation_id]["is_favorite"]
            self.conversations[conversation_id]["is_favorite"] = not current_status
            return not current_status
        return False
    
    def search_conversations(self, user_id: str, query: str) -> List[Dict]:
        """Search conversations by content"""
        results = []
        query_lower = query.lower()
        
        for conv in self.conversations.values():
            if conv["user_id"] != user_id:
                continue
                
            # Search in messages
            for message in conv["messages"]:
                if query_lower in message["content"].lower():
                    results.append({
                        "conversation_id": conv["id"],
                        "message_id": message["id"],
                        "snippet": message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"],
                        "created_at": message["created_at"]
                    })
                    break  # Only add conversation once
        
        return results
    
    def save_to_file(self, filename: str = "chat_history.json"):
        """Save conversations to file (simulating database persistence)"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Chat history saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save chat history: {e}")
            return False
    
    def load_from_file(self, filename: str = "chat_history.json"):
        """Load conversations from file (simulating database loading)"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
                logger.info(f"✅ Chat history loaded from {filename}")
                return True
            else:
                logger.info(f"📝 No existing chat history file found")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to load chat history: {e}")
            return False

def demo_chat_system():
    """
    Demonstrate the chat saving system
    """
    logger.info("🚀 Starting Chat System Demo...")
    
    # Initialize chat manager
    chat_manager = ChatManager()
    
    # Load existing chat history if available
    chat_manager.load_from_file()
    
    # Demo user
    user_id = "demo_user_123"
    
    try:
        # Demo 1: Create a conversation about investment planning
        logger.info("\n📝 Demo 1: Creating investment planning conversation...")
        conv1_id = chat_manager.create_conversation(user_id, "research")
        
        # Add user message
        chat_manager.add_message(
            conv1_id, 
            "user", 
            "I'm 30 years old and want to start investing for retirement. What should I consider?",
            tokens_used=20,
            metadata={"source": "web_interface", "user_age": 30}
        )
        
        # Add assistant response
        chat_manager.add_message(
            conv1_id,
            "assistant",
            """Great question! At 30, you have a significant advantage with time on your side. Here are key considerations:

**1. Emergency Fund First**
- Build 3-6 months of expenses in a high-yield savings account
- This provides financial security before investing

**2. Retirement Account Strategy**
- Maximize employer 401(k) match (free money!)
- Consider Roth IRA for tax-free growth
- Target 10-15% of income for retirement savings

**3. Investment Allocation**
- At 30, you can handle more risk for higher returns
- Consider 80% stocks, 20% bonds
- Diversify across domestic and international markets

**4. Low-Cost Index Funds**
- Start with broad market index funds (S&P 500)
- Keep expense ratios under 0.2%
- Avoid frequent trading

**5. Automate Everything**
- Set up automatic contributions
- Dollar-cost averaging reduces timing risk
- Increase contributions with salary raises

Would you like me to elaborate on any of these strategies or discuss specific investment products?""",
            tokens_used=180,
            metadata={
                "research_sources": 5,
                "confidence_score": 0.95,
                "agent_mode": "research"
            }
        )
        
        # Demo 2: Create a quick stock analysis conversation
        logger.info("\n📈 Demo 2: Creating stock analysis conversation...")
        conv2_id = chat_manager.create_conversation(user_id, "quick")
        
        chat_manager.add_message(
            conv2_id,
            "user",
            "What's your take on Apple stock (AAPL) right now?",
            tokens_used=12
        )
        
        chat_manager.add_message(
            conv2_id,
            "assistant",
            """**Apple (AAPL) Quick Analysis:**

**Strengths:**
- Strong brand loyalty and ecosystem
- Consistent revenue from services (App Store, iCloud)
- Solid balance sheet with massive cash reserves
- Innovation in AI and AR/VR spaces

**Concerns:**
- iPhone sales growth slowing in mature markets
- Regulatory pressure in EU and other regions
- High valuation compared to historical averages
- Dependence on China for manufacturing and sales

**Current Outlook:** Cautiously optimistic. Apple remains a quality company but may face headwinds. Consider it as part of a diversified tech allocation rather than a standalone bet.

**Price Target:** $180-200 range seems reasonable based on current fundamentals.""",
            tokens_used=95,
            metadata={
                "analysis_type": "quick",
                "data_sources": ["financial_statements", "market_data"],
                "last_updated": datetime.now().isoformat()
            }
        )
        
        # Demo 3: Show conversation management features
        logger.info("\n📚 Demo 3: Conversation management...")
        
        # Get all user conversations
        conversations = chat_manager.get_user_conversations(user_id)
        logger.info(f"✅ User has {len(conversations)} conversations:")
        for conv in conversations:
            logger.info(f"   - {conv['id']}: {conv['agent_mode']} mode, {conv['message_count']} messages")
        
        # Toggle favorite on first conversation
        is_favorite = chat_manager.toggle_favorite(conv1_id)
        logger.info(f"✅ Conversation {conv1_id[:12]}... favorite status: {is_favorite}")
        
        # Search conversations
        search_results = chat_manager.search_conversations(user_id, "retirement")
        logger.info(f"✅ Found {len(search_results)} conversations mentioning 'retirement':")
        for result in search_results:
            logger.info(f"   - {result['conversation_id'][:12]}...: {result['snippet']}")
        
        # Demo 4: Show conversation history
        logger.info("\n💬 Demo 4: Conversation history...")
        history = chat_manager.get_conversation_history(conv1_id)
        if history:
            logger.info(f"✅ Conversation {conv1_id[:12]}... has {len(history['messages'])} messages:")
            for i, msg in enumerate(history['messages'], 1):
                logger.info(f"   {i}. {msg['type']}: {msg['content'][:50]}...")
        
        # Demo 5: Save chat history
        logger.info("\n💾 Demo 5: Saving chat history...")
        if chat_manager.save_to_file():
            logger.info("✅ Chat history saved successfully")
            
            # Show file size
            if os.path.exists("chat_history.json"):
                file_size = os.path.getsize("chat_history.json")
                logger.info(f"   File size: {file_size:,} bytes")
        
        # Demo 6: Analytics
        logger.info("\n📊 Demo 6: Chat analytics...")
        total_conversations = len(conversations)
        total_messages = sum(conv['message_count'] for conv in conversations)
        total_tokens = sum(conv['total_tokens'] for conv in conversations)
        
        logger.info(f"✅ Chat Analytics for {user_id}:")
        logger.info(f"   Total Conversations: {total_conversations}")
        logger.info(f"   Total Messages: {total_messages}")
        logger.info(f"   Total Tokens Used: {total_tokens:,}")
        logger.info(f"   Average Messages per Conversation: {total_messages/total_conversations:.1f}")
        
        # Show conversation breakdown by mode
        mode_breakdown = {}
        for conv in conversations:
            mode = conv['agent_mode']
            mode_breakdown[mode] = mode_breakdown.get(mode, 0) + 1
        
        logger.info(f"   Conversations by Mode: {mode_breakdown}")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 CHAT SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("✅ Conversation creation and management")
        logger.info("✅ Message storage and retrieval")
        logger.info("✅ Search functionality")
        logger.info("✅ Favorite and metadata features")
        logger.info("✅ Persistent storage (file-based)")
        logger.info("✅ Analytics and reporting")
        logger.info("✅ Multi-agent mode support")
        
        logger.info("\n🔮 Next Steps for Production:")
        logger.info("   1. Replace file storage with PostgreSQL database")
        logger.info("   2. Add encryption for sensitive chat content")
        logger.info("   3. Implement user authentication and authorization")
        logger.info("   4. Add real-time chat features with WebSockets")
        logger.info("   5. Create chat export/import functionality")
        logger.info("   6. Add conversation summarization and tagging")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Chat system demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Disabled automatic execution to prevent interference with main server
# if __name__ == "__main__":
#     success = demo_chat_system()
#     
#     if success:
#         logger.info("\n🎊 Chat System Demo completed successfully!")
#         logger.info("💡 The chat saving functionality is ready for integration!")
#     else:
#         logger.error("\n💥 Chat System Demo failed!")