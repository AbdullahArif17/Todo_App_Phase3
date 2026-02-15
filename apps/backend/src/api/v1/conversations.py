from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Dict, Any
import uuid

from ...database import get_session
from ..deps import get_current_active_user
from ...models.user import User
from ...services.chat_service import ChatService
from ...services.analytics_service import AnalyticsService


router = APIRouter(tags=["conversations"])


@router.get("/", response_model=List[Dict[str, Any]])
def get_my_conversations(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get the authenticated user's conversations.

    Args:
        current_user: The authenticated user (from JWT token)
        session: Database session
        skip: Number of conversations to skip (for pagination)
        limit: Maximum number of conversations to return

    Returns:
        List of user's conversations
    """
    # Get conversations for the user
    from models.conversation import Conversation
    from sqlmodel import select

    statement = select(Conversation).where(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.last_activity.desc()).offset(skip).limit(limit)

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


@router.get("/{conversation_id}", response_model=Dict[str, Any])
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get details of a specific conversation.

    Args:
        conversation_id: The ID of the conversation
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        Conversation details
    """
    # Verify user has access to the conversation
    chat_service = ChatService()
    conversation = chat_service.get_conversation_by_id(session, conversation_id, current_user.id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "user_id": str(conversation.user_id),
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "last_activity": conversation.last_activity.isoformat() if hasattr(conversation, 'last_activity') else conversation.updated_at.isoformat(),
        "message_count": conversation.message_count if hasattr(conversation, 'message_count') else 0,
        "is_archived": conversation.is_archived if hasattr(conversation, 'is_archived') else False,
        "parent_conversation_id": str(conversation.parent_conversation_id) if hasattr(conversation, 'parent_conversation_id') and conversation.parent_conversation_id else None,
        "branch_depth": getattr(conversation, 'branch_depth', 0),
        "is_branch_point": getattr(conversation, 'is_branch_point', False)
    }


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Delete a conversation.

    Args:
        conversation_id: The ID of the conversation to delete
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        Confirmation message
    """
    # Verify user has access to the conversation
    from models.conversation import Conversation
    from sqlmodel import select

    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    conversation = session.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this conversation"
        )

    # Delete the conversation and its messages
    session.delete(conversation)
    session.commit()

    return {"message": "Conversation deleted successfully"}


@router.post("/{conversation_id}/archive")
def archive_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Archive a conversation.

    Args:
        conversation_id: The ID of the conversation to archive
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        Confirmation message
    """
    # Verify user has access to the conversation
    chat_service = ChatService()
    conversation = chat_service.get_conversation_by_id(session, conversation_id, current_user.id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this conversation"
        )

    # Mark as archived
    conversation.is_archived = True
    session.add(conversation)
    session.commit()

    return {"message": "Conversation archived successfully"}


@router.post("/{conversation_id}/tag")
def add_tag_to_conversation(
    conversation_id: uuid.UUID,
    tag_name: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Add a tag to a conversation.

    Args:
        conversation_id: The ID of the conversation
        tag_name: Name of the tag to add
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        Confirmation message
    """
    chat_service = ChatService()

    success = chat_service.add_tag_to_conversation(
        session=session,
        conversation_id=conversation_id,
        user_id=current_user.id,
        tag_name=tag_name
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to tag this conversation or tag creation failed"
        )

    return {"message": f"Tag '{tag_name}' added to conversation successfully"}


@router.get("/{conversation_id}/analytics")
def get_conversation_analytics(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get analytics for a specific conversation.

    Args:
        conversation_id: The ID of the conversation
        current_user: The authenticated user (from JWT token)
        session: Database session

    Returns:
        Conversation analytics
    """
    analytics_service = AnalyticsService()

    analytics = analytics_service.get_conversation_analytics(
        session=session,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if "error" in analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=analytics["error"]
        )

    return analytics