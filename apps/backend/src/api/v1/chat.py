from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import re
from fastapi.responses import StreamingResponse

from ...database import get_session
from ..deps import get_current_active_user
from ...models.user import User
from ...schemas.chat import ChatRequest, ChatResponse
from ...services.chat_service import ChatService
from ...agents.todo_agent import todo_agent
from ...utils.ai_utils import format_conversation_for_ai
from ...utils.logging import log_chat_access_attempt, log_security_event, setup_chat_logging
from ...utils.rate_limit import ai_rate_limiter
import logging

router = APIRouter(tags=["chat"])


def sanitize_input(input_text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        input_text: The raw user input

    Returns:
        Sanitized input text
    """
    # Remove potentially dangerous characters/sequences
    # This is a basic sanitization - in production, consider using a dedicated library
    sanitized = input_text.replace('<script', '&lt;script').replace('</script>', '&lt;/script>')
    sanitized = sanitized.replace('javascript:', 'javascript&#58;')
    sanitized = sanitized.replace('vbscript:', 'vbscript&#58;')
    sanitized = sanitized.replace('onload=', 'onload&#61;')
    sanitized = sanitized.replace('onerror=', 'onerror&#61;')

    # Additional prompt injection prevention
    sanitized = sanitized.replace('---', '—')  # Replace triple dashes that might be used to separate instructions
    sanitized = sanitized.replace('===', '—')  # Replace triple equals
    sanitized = sanitized.replace('System:', 'System&#58;')  # Prevent instruction injection
    sanitized = sanitized.replace('Assistant:', 'Assistant&#58;')
    sanitized = sanitized.replace('Human:', 'Human&#58;')

    return sanitized


@router.post("/{user_id}", response_model=ChatResponse)
async def chat_endpoint(
    user_id: uuid.UUID,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Chat endpoint that handles user messages and returns AI-generated responses.

    Args:
        user_id: The ID of the user (from URL path)
        chat_request: The chat request containing message and optional conversation_id
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        ChatResponse containing conversation_id and AI response
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        from ...utils.logging import log_security_event
        log_security_event("UNAUTHORIZED_ACCESS_ATTEMPT", current_user.id, f"Attempted to access user {user_id}'s chat")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's chat"
        )

    # Validate message content
    if not chat_request.message or not chat_request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )

    # Check message length
    if len(chat_request.message) > 5000:  # 5k character limit to prevent overly long prompts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message exceeds maximum length of 5,000 characters"
        )

    # Sanitize input to prevent injection attacks
    sanitized_message = sanitize_input(chat_request.message)

    # Update the chat request with sanitized message
    chat_request.message = sanitized_message

    # Check for potentially harmful content patterns
    harmful_patterns = [
        r'<script[^>]*>.*?</script>',  # JavaScript
        r'javascript:',                 # JavaScript protocol
        r'on\w+\s*=',                  # Event handlers
        r'eval\s*\(',                   # eval function
        r'exec\s*\(',                   # exec function
        r'expression\s*\(',             # CSS expression
    ]

    for pattern in harmful_patterns:
        if re.search(pattern, chat_request.message, re.IGNORECASE):
            from ...utils.logging import log_security_event
            log_security_event("MALICIOUS_CONTENT_DETECTED", current_user.id, f"Message contained harmful pattern: {pattern}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message contains potentially harmful content"
            )

    # Check rate limit for AI service usage
    if not ai_rate_limiter.is_allowed(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for AI service. Please try again later."
        )

    # Initialize services
    chat_service = ChatService()

    # Determine conversation ID - create new if not provided
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        # Create a new conversation
        conversation = chat_service.create_conversation(
            session=session,
            user_id=current_user.id,
            title=f"Chat started {chat_request.message[:30]}..."
        )
        conversation_id = conversation.id
    else:
        # Validate that the user can access this conversation
        if not chat_service.validate_conversation_access(session, conversation_id, current_user.id):
            from ...utils.logging import log_security_event
            log_security_event("UNAUTHORIZED_CONVERSATION_ACCESS", current_user.id, f"Attempted to access conversation {conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )

    # Persist the user's message to the database
    user_message = chat_service.create_message(
        session=session,
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message
    )

    # Get conversation history for AI context
    conversation_history = chat_service.get_conversation_messages(
        session=session,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    # Truncate conversation history to stay within token limits
    from ...utils.ai_utils import truncate_conversation_history
    truncated_history = truncate_conversation_history(conversation_history[:-1])  # Exclude the current message

    # Format the conversation history for the AI agent
    from ...utils.ai_utils import format_conversation_for_ai
    formatted_history = format_conversation_for_ai(truncated_history)

    # Log the start of AI processing
    logger = logging.getLogger("chat_operations")
    logger.info(f"Processing chat request for user {current_user.id}, conversation {conversation_id}")

    # Process the message with the AI agent using MCP tools
    agent_response = await chat_service.process_agent_chat(
        session=session,
        user_id=current_user.id,
        conversation_id=conversation_id,
        user_message_content=chat_request.message
    )

    ai_response = agent_response["response"]

    # Log successful AI response
    logger.info(f"AI response generated for user {current_user.id}, conversation {conversation_id}")

    # Persist the AI's response to the database
    ai_message = chat_service.create_message(
        session=session,
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )

    # Return the response
    return ChatResponse(
        conversation_id=conversation_id,
        response=ai_response,
        message_id=ai_message.id
    )


@router.get("/{user_id}/conversations", tags=["conversations"])
def get_user_conversations(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get paginated list of user's conversations.

    Args:
        user_id: The ID of the user (from URL path)
        current_user: The authenticated user (from JWT token)
        session: Database session
        skip: Number of conversations to skip (for pagination)
        limit: Maximum number of conversations to return

    Returns:
        List of conversation summaries
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # Get conversations for the user
    from ...models.conversation import Conversation
    from sqlmodel import select

    statement = select(Conversation).where(
        Conversation.user_id == current_user.id
    ).offset(skip).limit(limit)

    conversations = session.exec(statement).all()

    return [{
        "id": str(conv.id),
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
        "last_activity": conv.last_activity.isoformat() if hasattr(conv, 'last_activity') else conv.updated_at.isoformat(),
        "message_count": conv.message_count if hasattr(conv, 'message_count') else 0,
        "is_archived": conv.is_archived if hasattr(conv, 'is_archived') else False
    } for conv in conversations]


@router.get("/{user_id}/conversations/{conversation_id}/messages", tags=["messages"])
def get_conversation_messages_paginated(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get paginated messages from a conversation.

    Args:
        user_id: The ID of the user (from URL path)
        conversation_id: The ID of the conversation
        current_user: The authenticated user (from JWT token)
        session: Database session
        skip: Number of messages to skip (for pagination)
        limit: Maximum number of messages to return

    Returns:
        List of messages in the conversation
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # Verify user has access to the conversation
    chat_service = ChatService()
    conversation = chat_service.get_conversation_by_id(session, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Get paginated messages
    messages = chat_service.get_conversation_messages(
        session=session,
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=limit,
        offset=skip
    )

    return [{
        "id": str(msg.id),
        "role": msg.role,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat(),
        "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') else msg.timestamp.isoformat()
    } for msg in messages]


@router.get("/{user_id}/search", tags=["search"])
def search_conversations(
    user_id: uuid.UUID,
    query: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search conversations and messages by content.

    Args:
        user_id: The ID of the user (from URL path)
        query: Search query string
        current_user: The authenticated user (from JWT token)
        session: Database session
        limit: Maximum number of results to return
        offset: Number of results to skip

    Returns:
        Dictionary with search results
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # Perform the search
    chat_service = ChatService()

    # Search for conversations containing the query
    conversation_ids = chat_service.search_conversations(
        session=session,
        user_id=current_user.id,
        search_term=query,
        limit=limit,
        offset=offset
    )

    # Get detailed information for each conversation
    conversations_detail = []
    for conv_id in conversation_ids:
        # Get conversation details
        from ...models.conversation import Conversation
        from sqlmodel import select

        conv_statement = select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.user_id == current_user.id
        )
        conversation = session.exec(conv_statement).first()

        if conversation:
            conversations_detail.append({
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "last_activity": conversation.last_activity.isoformat() if hasattr(conversation, 'last_activity') else conversation.updated_at.isoformat(),
                "message_count": conversation.message_count if hasattr(conversation, 'message_count') else 0
            })

    # Also search for specific messages within the user's conversations
    # This would require a more complex implementation in a real system
    # For now, we'll return the conversation-level search results
    message_results = []

    return {
        "query": query,
        "conversations": conversations_detail,
        "messages": message_results,
        "total_conversation_results": len(conversations_detail),
        "total_message_results": len(message_results),
        "limit": limit,
        "offset": offset
    }


@router.get("/{user_id}/analytics", tags=["analytics"])
def get_user_analytics(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get analytics for the user's conversations.

    Args:
        user_id: The ID of the user (from URL path)
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        User conversation analytics
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's analytics"
        )

    # In a real implementation, this would calculate analytics
    # For now, we'll return a simple placeholder
    return {
        "user_id": str(user_id),
        "analytics": {
            "total_conversations": 0,
            "total_messages": 0,
            "active_conversations": 0,
            "most_active_day": "N/A"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{user_id}/stream/{conversation_id}")
async def stream_conversation_messages(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Stream messages from a conversation in real-time.

    Args:
        user_id: The ID of the user (from URL path)
        conversation_id: The ID of the conversation to stream
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        Streaming response with conversation messages
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversation stream"
        )

    # Verify user has access to the conversation
    chat_service = ChatService()
    conversation = chat_service.get_conversation_by_id(session, conversation_id, current_user.id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Get all messages in the conversation
    messages = chat_service.get_conversation_messages(
        session=session,
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=1000  # Reasonable limit for streaming
    )

    # Stream the messages
    from fastapi.responses import StreamingResponse
    import json

    def event_stream():
        for msg in messages:
            yield f"data: {json.dumps({ 'id': str(msg.id), 'role': msg.role, 'content': msg.content, 'timestamp': msg.timestamp.isoformat() })}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")