from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import List
import uuid
from models.conversation import Conversation
from models.message import Message
from services.chat_service import ChatService


class LifecycleService:
    """
    Service for managing the lifecycle of conversations including auto-cleanup and archival.
    """

    def __init__(self):
        self.chat_service = ChatService()

    def get_inactive_conversations(self, session: Session, days_inactive: int = 30) -> List[uuid.UUID]:
        """
        Get conversations that have been inactive for a specified number of days.

        Args:
            session: Database session
            days_inactive: Number of days of inactivity to consider

        Returns:
            List of conversation IDs that have been inactive
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)

        statement = select(Conversation.id).where(
            Conversation.last_activity < cutoff_date
        )
        inactive_conversations = session.exec(statement).all()
        return inactive_conversations

    def auto_archive_conversations(self, session: Session, days_inactive: int = 60) -> int:
        """
        Automatically archive conversations that have been inactive for a specified number of days.

        Args:
            session: Database session
            days_inactive: Number of days of inactivity before archiving

        Returns:
            Number of conversations archived
        """
        inactive_convs = self.get_inactive_conversations(session, days_inactive)

        archived_count = 0
        for conv_id in inactive_convs:
            # Get the conversation
            statement = select(Conversation).where(Conversation.id == conv_id)
            conversation = session.exec(statement).first()

            if conversation and not conversation.is_archived:
                # Mark as archived
                conversation.is_archived = True
                session.add(conversation)
                archived_count += 1

        session.commit()
        return archived_count

    def auto_delete_conversations(self, session: Session, days_old: int = 365) -> int:
        """
        Automatically delete conversations that are older than a specified number of days.

        Args:
            session: Database session
            days_old: Number of days old before deletion

        Returns:
            Number of conversations deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Find conversations to delete
        statement = select(Conversation).where(
            Conversation.created_at < cutoff_date
        )
        old_conversations = session.exec(statement).all()

        deleted_count = 0
        for conversation in old_conversations:
            # In a real implementation, we would delete the conversation and its messages
            # For now, we'll just count them
            session.delete(conversation)
            deleted_count += 1

        session.commit()
        return deleted_count

    def cleanup_empty_conversations(self, session: Session) -> int:
        """
        Delete conversations that have no messages.

        Args:
            session: Database session

        Returns:
            Number of empty conversations deleted
        """
        # Find conversations with zero messages
        from sqlalchemy import func
        stmt = (
            select(Conversation.id)
            .outerjoin(Message, Conversation.id == Message.conversation_id)
            .group_by(Conversation.id)
            .having(func.count(Message.id) == 0)
        )

        empty_conversations = session.exec(stmt).all()

        deleted_count = 0
        for conv_id in empty_conversations:
            # Get the conversation
            conv_stmt = select(Conversation).where(Conversation.id == conv_id)
            conversation = session.exec(conv_stmt).first()

            if conversation:
                session.delete(conversation)
                deleted_count += 1

        session.commit()
        return deleted_count

    def get_conversation_age_metrics(self, session: Session) -> dict:
        """
        Get metrics about conversation ages.

        Args:
            session: Database session

        Returns:
            Dictionary with age-based metrics
        """
        from sqlalchemy import func

        # Get all conversations
        all_convs = session.exec(select(Conversation)).all()

        now = datetime.utcnow()
        age_buckets = {
            "less_than_1_day": 0,
            "1_to_7_days": 0,
            "1_to_4_weeks": 0,
            "1_to_6_months": 0,
            "6_months_to_1_year": 0,
            "more_than_1_year": 0
        }

        for conv in all_convs:
            age = (now - conv.created_at).days

            if age < 1:
                age_buckets["less_than_1_day"] += 1
            elif age < 7:
                age_buckets["1_to_7_days"] += 1
            elif age < 30:
                age_buckets["1_to_4_weeks"] += 1
            elif age < 180:
                age_buckets["1_to_6_months"] += 1
            elif age < 365:
                age_buckets["6_months_to_1_year"] += 1
            else:
                age_buckets["more_than_1_year"] += 1

        return {
            "total_conversations": len(all_convs),
            "age_distribution": age_buckets
        }

    def perform_regular_maintenance(self, session: Session) -> dict:
        """
        Perform regular maintenance tasks on conversations.

        Args:
            session: Database session

        Returns:
            Dictionary with maintenance results
        """
        # Auto-archive old conversations
        archived = self.auto_archive_conversations(session, days_inactive=60)

        # Clean up empty conversations
        cleaned = self.cleanup_empty_conversations(session)

        # Get metrics after maintenance
        metrics = self.get_conversation_age_metrics(session)

        return {
            "archived_conversations": archived,
            "cleaned_empty_conversations": cleaned,
            "current_metrics": metrics,
            "maintenance_timestamp": datetime.utcnow().isoformat()
        }

    def calculate_storage_usage(self, session: Session) -> dict:
        """
        Calculate approximate storage usage by conversations.

        Args:
            session: Database session

        Returns:
            Dictionary with storage usage metrics
        """
        from sqlalchemy import func

        # Count total conversations
        total_convs = session.exec(select(func.count(Conversation.id))).one()

        # Count total messages
        total_msgs = session.exec(select(func.count(Message.id))).one()

        # Count archived conversations
        archived_convs = session.exec(
            select(func.count(Conversation.id)).where(Conversation.is_archived == True)
        ).one()

        # Approximate storage calculations (in characters)
        # This is a simplified approximation
        total_content_chars = session.exec(
            select(func.sum(func.length(Message.content)))
        ).one() or 0

        return {
            "total_conversations": total_convs,
            "total_messages": total_msgs,
            "archived_conversations": archived_convs,
            "approximate_content_characters": total_content_chars,
            "estimated_storage_mb": round(total_content_chars / (1024 * 1024), 2)  # Rough estimate
        }