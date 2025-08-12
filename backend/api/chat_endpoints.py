"""
Chat API Endpoints for Artha AI
===============================

FastAPI endpoints for managing chat conversations, messages, and analytics.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from services.chat_service import ChatService

logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = ChatService()

# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Pydantic models for request/response
class CreateConversationRequest(BaseModel):
    user_id: str
    agent_mode: str = "quick"
    financial_context: Optional[Dict[str, Any]] = None

class AddMessageRequest(BaseModel):
    conversation_id: str
    message_type: str  # 'user', 'assistant', 'system'
    content: str
    agent_mode: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    financial_snapshot: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    agent_mode: str
    created_at: str
    updated_at: str
    last_message_at: str
    is_active: bool
    is_archived: bool
    is_favorite: bool
    message_count: int
    total_tokens_used: int
    summary: Optional[str]
    tags: Optional[List[str]]

class MessageResponse(BaseModel):
    id: str
    type: str
    content: str
    created_at: str
    agent_mode: Optional[str]
    tokens_used: int
    processing_time: float
    metadata: Optional[Dict[str, Any]]
    is_edited: bool

class ConversationHistoryResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]
    financial_context: Optional[Dict[str, Any]]

class AddFeedbackRequest(BaseModel):
    user_id: str
    message_id: str
    feedback_type: str
    rating: Optional[int] = None
    feedback_text: Optional[str] = None

@router.post("/conversations", response_model=Dict[str, str])
async def create_conversation(request: CreateConversationRequest):
    """
    Create a new chat conversation
    """
    try:
        conversation_id = chat_service.create_conversation(
            user_id=request.user_id,
            agent_mode=request.agent_mode,
            financial_context=request.financial_context
        )
        
        return {
            "conversation_id": conversation_id,
            "message": "Conversation created successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@router.post("/messages", response_model=Dict[str, str])
async def add_message(request: AddMessageRequest):
    """
    Add a message to a conversation
    """
    try:
        message_id = chat_service.add_message(
            conversation_id=request.conversation_id,
            message_type=request.message_type,
            content=request.content,
            agent_mode=request.agent_mode,
            tokens_used=request.tokens_used,
            processing_time=request.processing_time,
            metadata=request.metadata,
            financial_snapshot=request.financial_snapshot
        )
        
        return {
            "message_id": message_id,
            "message": "Message added successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to add message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")

@router.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    user_id: str = Query(..., description="User ID"),
    include_deleted: bool = Query(False, description="Include deleted messages")
):
    """
    Get conversation history with all messages
    """
    try:
        history = chat_service.get_conversation_history(
            user_id=user_id,
            conversation_id=conversation_id,
            include_deleted=include_deleted
        )
        
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation": history,
            "message": "Conversation history retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@router.get("/conversations")
async def get_user_conversations(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, description="Maximum number of conversations"),
    include_archived: bool = Query(False, description="Include archived conversations")
):
    """
    Get all conversations for a user
    """
    try:
        conversations = chat_service.get_user_conversations(
            user_id=user_id,
            limit=limit,
            include_archived=include_archived
        )
        
        return {
            "conversations": conversations,
            "count": len(conversations),
            "message": "Conversations retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get user conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/search")
async def search_conversations(
    user_id: str = Query(..., description="User ID"),
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum results")
):
    """
    Search conversations by content
    """
    try:
        results = chat_service.search_conversations(
            user_id=user_id,
            query=query,
            limit=limit
        )
        
        return {
            "results": results,
            "count": len(results),
            "query": query,
            "message": "Search completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to search conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.put("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    Archive a conversation
    """
    try:
        success = chat_service.archive_conversation(
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "message": "Conversation archived successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to archive conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to archive conversation: {str(e)}")

@router.put("/conversations/{conversation_id}/favorite")
async def toggle_favorite(
    conversation_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    Toggle favorite status of a conversation
    """
    try:
        is_favorite = chat_service.toggle_favorite(
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        return {
            "is_favorite": is_favorite,
            "message": f"Conversation {'added to' if is_favorite else 'removed from'} favorites"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to toggle favorite: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    Delete a conversation and all its messages
    """
    try:
        success = chat_service.delete_conversation(
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "message": "Conversation deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@router.get("/analytics")
async def get_chat_analytics(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, description="Number of days to analyze")
):
    """
    Get chat analytics for a user
    """
    try:
        analytics = chat_service.get_chat_analytics(
            user_id=user_id,
            days=days
        )
        
        return {
            "analytics": analytics,
            "message": "Analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/feedback")
async def add_feedback(request: AddFeedbackRequest):
    """
    Add feedback for a message
    """
    try:
        feedback_id = chat_service.add_feedback(
            user_id=request.user_id,
            message_id=request.message_id,
            feedback_type=request.feedback_type,
            rating=request.rating,
            feedback_text=request.feedback_text
        )
        
        return {
            "feedback_id": feedback_id,
            "message": "Feedback added successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to add feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add feedback: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_conversations(
    days: int = Query(90, description="Delete conversations older than this many days")
):
    """
    Clean up old archived conversations (Admin endpoint)
    """
    try:
        deleted_count = chat_service.cleanup_old_conversations(days=days)
        
        return {
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} old conversations"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def chat_health_check():
    """
    Health check for chat service
    """
    try:
        # Test database connection
        with chat_service.SessionLocal() as session:
            session.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "chat_service",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Chat service is operational"
        }
        
    except Exception as e:
        logger.error(f"❌ Chat service health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Chat service unhealthy: {str(e)}")

@router.get("/conversations/{conversation_id}/export/pdf")
async def export_conversation_to_pdf(
    conversation_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    Export conversation to PDF report
    """
    try:
        logger.info(f"📄 Exporting conversation {conversation_id} to PDF for user: {user_id}")
        
        # Get conversation data
        conversation = chat_service.get_conversation(user_id, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get conversation messages
        messages = chat_service.get_conversation_messages(user_id, conversation_id)
        
        # Prepare conversation data for PDF
        conversation_data = {
            'metadata': {
                'id': conversation_id,
                'date': conversation.get('created_at', datetime.utcnow()).isoformat() if isinstance(conversation.get('created_at'), datetime) else str(conversation.get('created_at', 'Unknown')),
                'agent_mode': conversation.get('agent_mode', 'Unknown'),
                'duration': 'N/A',  # Could calculate based on message timestamps
                'title': f"Conversation {conversation_id[:8]}"
            },
            'messages': []
        }
        
        # Process messages for PDF
        for msg in messages:
            conversation_data['messages'].append({
                'type': msg.get('sender_type', 'unknown'),
                'content': msg.get('content', ''),
                'timestamp': msg.get('created_at', datetime.utcnow()).isoformat() if isinstance(msg.get('created_at'), datetime) else str(msg.get('created_at', 'Unknown'))
            })
        
        # Generate PDF
        from services.pdf_service import get_pdf_service
        pdf_service = get_pdf_service()
        
        pdf_bytes = pdf_service.generate_chat_conversation_report(conversation_data)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"artha_chat_{conversation_id[:8]}_{timestamp}.pdf"
        
        def generate_pdf():
            yield pdf_bytes
        
        return StreamingResponse(
            generate_pdf(),
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to export conversation to PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")

@router.get("/export/all-conversations/pdf")
async def export_all_conversations_to_pdf(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, description="Number of days of conversations to export")
):
    """
    Export all user conversations from the last N days to PDF
    """
    try:
        logger.info(f"📄 Exporting all conversations to PDF for user: {user_id}")
        
        # Get user conversations
        conversations = chat_service.get_user_conversations(user_id)
        
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found")
        
        # Filter conversations by date if needed
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filtered_conversations = [
            conv for conv in conversations 
            if conv.get('created_at') and conv['created_at'] >= cutoff_date
        ] if days > 0 else conversations
        
        # Prepare comprehensive conversation data
        all_conversations_data = {
            'metadata': {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'total_conversations': len(filtered_conversations),
                'date_range': f"Last {days} days",
                'title': f"Complete Chat History Export"
            },
            'conversations': []
        }
        
        # Process each conversation
        for conv in filtered_conversations[:20]:  # Limit to 20 conversations for PDF size
            conv_id = conv.get('id')
            messages = chat_service.get_conversation_messages(user_id, conv_id)
            
            conv_data = {
                'id': conv_id,
                'created_at': conv.get('created_at', 'Unknown'),
                'agent_mode': conv.get('agent_mode', 'Unknown'),
                'message_count': len(messages),
                'messages': []
            }
            
            # Add first few messages from each conversation
            for msg in messages[:10]:  # Limit messages per conversation
                conv_data['messages'].append({
                    'type': msg.get('sender_type', 'unknown'),
                    'content': msg.get('content', '')[:500],  # Truncate long messages
                    'timestamp': msg.get('created_at', 'Unknown')
                })
            
            all_conversations_data['conversations'].append(conv_data)
        
        # Generate comprehensive PDF
        from services.pdf_service import get_pdf_service
        pdf_service = get_pdf_service()
        
        # For now, we'll use the single conversation format but could extend for multiple
        # This is a simplified version - you could create a new method in pdf_service for multiple conversations
        sample_conversation = {
            'metadata': all_conversations_data['metadata'],
            'messages': []
        }
        
        # Combine messages from all conversations
        for conv in all_conversations_data['conversations'][:5]:  # Limit for demo
            sample_conversation['messages'].extend(conv['messages'][:5])  # Add first 5 messages from each
        
        pdf_bytes = pdf_service.generate_chat_conversation_report(sample_conversation)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"artha_all_chats_{user_id[:8]}_{timestamp}.pdf"
        
        def generate_pdf():
            yield pdf_bytes
        
        return StreamingResponse(
            generate_pdf(),
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to export all conversations to PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")