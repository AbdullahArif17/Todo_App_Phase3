from sqlmodel import Session, select
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid
from apps.backend.src.models.conversation import Conversation
from apps.backend.src.models.message import Message


class AnalyticsService:
    """
    Service for collecting and analyzing conversation metrics and analytics.
    """

    def get_user_conversation_stats(self, session: Session, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get conversation statistics for a specific user.

        Args:
            session: Database session
            user_id: ID of the user to get stats for

        Returns:
            Dictionary containing user conversation statistics
        """
        # Get total number of conversations
        conv_statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = session.exec(conv_statement).all()
        total_conversations = len(conversations)

        # Get total number of messages
        msg_statement = select(Message).where(
            Message.conversation_id.in_([conv.id for conv in conversations])
        )
        messages = session.exec(msg_statement).all()
        total_messages = len(messages)

        # Calculate average messages per conversation
        avg_messages_per_conv = total_messages / total_conversations if total_conversations > 0 else 0

        # Get conversations created in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_conv_statement = select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.created_at >= thirty_days_ago
        )
        recent_conversations = session.exec(recent_conv_statement).all()
        recent_convs_count = len(recent_conversations)

        # Get message distribution by role
        role_distribution = {}
        for msg in messages:
            role = msg.role
            role_distribution[role] = role_distribution.get(role, 0) + 1

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "average_messages_per_conversation": round(avg_messages_per_conv, 2),
            "recent_conversations_count": recent_convs_count,
            "message_distribution": role_distribution,
            "active_days_count": len(set(msg.timestamp.date() for msg in messages))
        }

    def get_conversation_analytics(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to analyze
            user_id: ID of the user requesting analytics (for authorization)

        Returns:
            Dictionary containing conversation analytics
        """
        # Verify user has access to the conversation
        conv_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(conv_statement).first()

        if not conversation:
            return {"error": "Access denied: You don't have permission to view analytics for this conversation."}

        # Get all messages in the conversation
        msg_statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        messages = session.exec(msg_statement).all()

        if not messages:
            return {"message_count": 0, "duration_minutes": 0, "role_distribution": {}}

        # Calculate duration of conversation
        start_time = messages[0].timestamp
        end_time = messages[-1].timestamp
        duration_minutes = (end_time - start_time).total_seconds() / 60

        # Calculate message statistics
        role_distribution = {}
        user_msg_count = 0
        ai_msg_count = 0

        for msg in messages:
            role = msg.role
            role_distribution[role] = role_distribution.get(role, 0) + 1

            if role == "user":
                user_msg_count += 1
            elif role == "assistant":
                ai_msg_count += 1

        # Calculate response time between user and AI messages (approximately)
        total_response_time = 0
        response_count = 0

        for i in range(len(messages) - 1):
            current_msg = messages[i]
            next_msg = messages[i + 1]

            # If current is user and next is AI, calculate response time
            if current_msg.role == "user" and next_msg.role == "assistant":
                response_time = (next_msg.timestamp - current_msg.timestamp).total_seconds()
                total_response_time += response_time
                response_count += 1

        avg_response_time = total_response_time / response_count if response_count > 0 else 0

        return {
            "conversation_id": str(conversation_id),
            "message_count": len(messages),
            "duration_minutes": round(duration_minutes, 2),
            "role_distribution": role_distribution,
            "user_message_count": user_msg_count,
            "ai_message_count": ai_msg_count,
            "average_ai_response_time_seconds": round(avg_response_time, 2),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

    def get_platform_analytics(self, session: Session) -> Dict[str, Any]:
        """
        Get platform-wide analytics (admin level).

        Args:
            session: Database session

        Returns:
            Dictionary containing platform analytics
        """
        # Get total users (by counting distinct user_ids in conversations)
        from apps.backend.src.models.user import User
        user_statement = select(User).distinct()
        users = session.exec(user_statement).all()
        total_users = len(users)

        # Get total conversations
        conv_statement = select(Conversation)
        all_conversations = session.exec(conv_statement).all()
        total_convs = len(all_conversations)

        # Get total messages
        msg_statement = select(Message)
        all_messages = session.exec(msg_statement).all()
        total_msgs = len(all_messages)

        # Calculate averages
        avg_msgs_per_user = total_msgs / total_users if total_users > 0 else 0
        avg_convs_per_user = total_convs / total_users if total_users > 0 else 0

        # Get active users in the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_users_statement = select(Conversation.user_id).where(
            Conversation.last_activity >= seven_days_ago
        ).distinct()
        active_user_ids = session.exec(active_users_statement).all()
        weekly_active_users = len(active_user_ids)

        return {
            "total_users": total_users,
            "total_conversations": total_convs,
            "total_messages": total_msgs,
            "average_messages_per_user": round(avg_msgs_per_user, 2),
            "average_conversations_per_user": round(avg_convs_per_user, 2),
            "weekly_active_users": weekly_active_users,
            "timestamp": datetime.utcnow().isoformat()
        }