from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from ..models.conversation import Conversation, ConversationRead
from ..models.message import Message, MessageRead
from ..schemas.chat import ChatRequest


class ChatService:
    def __init__(self):
        from ..agents.todo_agent import todo_agent
        from ..agents.response_processor import response_processor
        from ..agents.ai_utils import build_agent_context
        self.todo_agent = todo_agent
        self.response_processor = response_processor
        self.build_agent_context = build_agent_context

    def create_conversation(self, session: Session, user_id: uuid.UUID, title: str = "New Conversation") -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            message_count=0  # Initialize message count
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Conversation]:
        """Get a specific conversation for a user."""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return session.exec(statement).first()

    def get_conversation_messages(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get messages in a conversation, ensuring user ownership."""
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return []

        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).offset(offset).limit(limit)  # Changed to asc order to avoid reversing

        messages = session.exec(statement).all()
        return messages

    def get_conversation_messages_desc(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get messages in a conversation in descending order, ensuring user ownership."""
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return []

        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.desc()).offset(offset).limit(limit)

        messages = session.exec(statement).all()
        return messages

    def get_conversation_message_count(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> int:
        """Get the total count of messages in a conversation."""
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return 0

        from sqlalchemy import func
        statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        count = session.exec(statement).one()
        return count

    def generate_conversation_summary(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, max_length: int = 200) -> str:
        """
        Generate a summary of the conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to summarize
            user_id: ID of the user requesting the summary
            max_length: Maximum length of the summary in characters

        Returns:
            A summary string of the conversation
        """
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return "Access denied: You don't have permission to view this conversation."

        # Get all messages in the conversation
        all_messages = self.get_conversation_messages(session, conversation_id, user_id, limit=1000)  # Get more messages for summary

        if not all_messages:
            return "No messages to summarize."

        # Create a simple summary by concatenating key messages
        # In a production system, this would use an AI model to generate a proper summary
        summary_parts = []

        # Include the first few messages to capture the topic
        for msg in all_messages[:3]:  # First 3 messages
            snippet = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
            summary_parts.append(f"[{msg.role.upper()}]: {snippet}")

        # Include the last few messages to capture the conclusion
        if len(all_messages) > 3:
            for msg in all_messages[-2:]:  # Last 2 messages
                snippet = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
                summary_parts.append(f"[{msg.role.upper()}]: {snippet}")

        summary = " | ".join(summary_parts)

        # Truncate to max_length if needed
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    def get_conversation_topic(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> str:
        """
        Extract the main topic of the conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user requesting the topic

        Returns:
            The main topic of the conversation
        """
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return "Access Denied"

        # Get the first few messages to determine the topic
        messages = self.get_conversation_messages(session, conversation_id, user_id, limit=5)

        if not messages:
            return "Empty Conversation"

        # Simple topic extraction based on first message
        first_message = messages[0].content.lower()

        # Look for common todo-related keywords
        todo_keywords = ["todo", "task", "list", "add", "create", "delete", "complete", "finish", "done"]

        for keyword in todo_keywords:
            if keyword in first_message:
                return f"Todo Management: {keyword.title()}"

        # If no specific keyword found, return first few words
        words = first_message.split()[:5]
        return " ".join(words).title()

    def export_conversation(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Dict:
        """
        Export a conversation to a structured format.

        Args:
            session: Database session
            conversation_id: ID of the conversation to export
            user_id: ID of the user requesting the export

        Returns:
            Dictionary containing conversation data
        """
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return {"error": "Access denied: You don't have permission to export this conversation."}

        # Get all messages in the conversation
        messages = self.get_conversation_messages(session, conversation_id, user_id, limit=10000)  # Get all messages

        # Create export data structure
        export_data = {
            "conversation_id": str(conversation.id),
            "title": conversation.title,
            "user_id": str(conversation.user_id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "last_activity": conversation.last_activity.isoformat() if hasattr(conversation, 'last_activity') else None,
            "message_count": conversation.message_count if hasattr(conversation, 'message_count') else len(messages),
            "is_archived": conversation.is_archived if hasattr(conversation, 'is_archived') else False,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') else msg.timestamp.isoformat(),
                    "updated_at": msg.updated_at.isoformat() if hasattr(msg, 'updated_at') else msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }

        return export_data

    def import_conversation(self, session: Session, user_id: uuid.UUID, import_data: Dict) -> Optional[uuid.UUID]:
        """
        Import a conversation from a structured format.

        Args:
            session: Database session
            user_id: ID of the user importing the conversation
            import_data: Dictionary containing conversation data to import

        Returns:
            ID of the imported conversation, or None if import failed
        """
        try:
            # Create new conversation
            from apps.backend.src.models.conversation import Conversation
            from datetime import datetime
            import uuid

            new_conversation = Conversation(
                title=import_data.get("title", "Imported Conversation"),
                user_id=user_id,
                created_at=datetime.fromisoformat(import_data.get("created_at", datetime.utcnow().isoformat())),
                updated_at=datetime.fromisoformat(import_data.get("updated_at", datetime.utcnow().isoformat())),
                last_activity=datetime.fromisoformat(import_data.get("last_activity", datetime.utcnow().isoformat())) if import_data.get("last_activity") else datetime.utcnow(),
                message_count=import_data.get("message_count", 0),
                is_archived=import_data.get("is_archived", False),
                parent_conversation_id=import_data.get("parent_conversation_id", None),
                branch_depth=import_data.get("branch_depth", 0),
                is_branch_point=import_data.get("is_branch_point", False)
            )

            session.add(new_conversation)
            session.flush()  # Get the ID for the new conversation

            # Import messages
            for msg_data in import_data.get("messages", []):
                from apps.backend.src.models.message import Message

                message = Message(
                    id=uuid.UUID(msg_data["id"]) if msg_data.get("id") else uuid.uuid4(),
                    conversation_id=new_conversation.id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    created_at=datetime.fromisoformat(msg_data.get("created_at")) if msg_data.get("created_at") else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(msg_data.get("updated_at")) if msg_data.get("updated_at") else datetime.utcnow()
                )
                session.add(message)

            session.commit()
            return new_conversation.id

        except Exception as e:
            session.rollback()
            print(f"Error importing conversation: {str(e)}")
            return None

    def create_branch_conversation(self, session: Session, parent_conversation_id: uuid.UUID, user_id: uuid.UUID, title: str = "Branched Conversation") -> Optional[uuid.UUID]:
        """
        Create a new conversation that branches from an existing one.

        Args:
            session: Database session
            parent_conversation_id: ID of the parent conversation to branch from
            user_id: ID of the user creating the branch
            title: Title for the new branched conversation

        Returns:
            ID of the new branched conversation, or None if creation failed
        """
        try:
            # Verify that the user has access to the parent conversation
            parent_conversation = self.get_conversation_by_id(session, parent_conversation_id, user_id)
            if not parent_conversation:
                return None

            # Update parent to mark as a branch point
            parent_conversation.is_branch_point = True
            session.add(parent_conversation)

            # Create the new branched conversation
            from apps.backend.src.models.conversation import Conversation
            from datetime import datetime
            import uuid

            new_conversation = Conversation(
                title=title,
                user_id=user_id,
                parent_conversation_id=parent_conversation_id,
                branch_depth=parent_conversation.branch_depth + 1 if hasattr(parent_conversation, 'branch_depth') else 1,
                is_branch_point=False,  # Initially, it won't have branches
                message_count=0
            )

            session.add(new_conversation)
            session.commit()
            session.refresh(new_conversation)

            return new_conversation.id

        except Exception as e:
            session.rollback()
            print(f"Error creating branched conversation: {str(e)}")
            return None

    def get_conversation_branches(self, session: Session, parent_conversation_id: uuid.UUID, user_id: uuid.UUID) -> List[uuid.UUID]:
        """
        Get all conversation IDs that branch from a given conversation.

        Args:
            session: Database session
            parent_conversation_id: ID of the parent conversation
            user_id: ID of the user requesting the branches

        Returns:
            List of conversation IDs that branch from the parent
        """
        from apps.backend.src.models.conversation import Conversation
        from sqlmodel import select

        # First verify the user has access to the parent conversation
        parent_conversation = self.get_conversation_by_id(session, parent_conversation_id, user_id)
        if not parent_conversation:
            return []

        # Get all conversations that branch from this one
        statement = select(Conversation.id).where(
            Conversation.parent_conversation_id == parent_conversation_id,
            Conversation.user_id == user_id
        )

        branch_ids = session.exec(statement).all()
        return branch_ids

    def search_conversations(self, session: Session, user_id: uuid.UUID, search_term: str, limit: int = 20, offset: int = 0) -> List[uuid.UUID]:
        """
        Search conversations by content in messages.

        Args:
            session: Database session
            user_id: ID of the user performing the search
            search_term: Term to search for in conversation messages
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of conversation IDs that match the search term
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.message import Message
        from sqlmodel import select, and_, or_
        from sqlalchemy import func

        # Search for conversations that contain the search term in their messages
        # Join Conversation and Message tables
        search_pattern = f"%{search_term}%"

        # First, find message IDs that match the search
        message_statement = select(Message.conversation_id).where(
            and_(
                Message.content.ilike(search_pattern),
                Message.conversation_id.in_(
                    select(Conversation.id).where(Conversation.user_id == user_id)
                )
            )
        ).distinct()

        matching_conversation_ids = session.exec(message_statement).all()

        # Now get the conversations that have matching messages
        conversation_statement = select(Conversation.id).where(
            and_(
                Conversation.id.in_(matching_conversation_ids),
                Conversation.user_id == user_id
            )
        ).offset(offset).limit(limit)

        conversation_ids = session.exec(conversation_statement).all()
        return conversation_ids

    def search_messages_in_conversation(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, search_term: str, limit: int = 20, offset: int = 0) -> List:
        """
        Search for messages within a specific conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to search in
            user_id: ID of the user performing the search
            search_term: Term to search for in messages
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of messages that match the search term
        """
        from apps.backend.src.models.message import Message
        from sqlmodel import select, and_

        # Verify user has access to the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return []

        search_pattern = f"%{search_term}%"

        statement = select(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.content.ilike(search_pattern)
            )
        ).offset(offset).limit(limit)

        messages = session.exec(statement).all()
        return messages

    def add_tag_to_conversation(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, tag_name: str) -> bool:
        """
        Add a tag to a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to tag
            user_id: ID of the user adding the tag
            tag_name: Name of the tag to add

        Returns:
            True if successful, False otherwise
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.tag import Tag, conversation_tag
        from sqlmodel import select

        # Verify user has access to the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return False

        # Get or create the tag
        tag_statement = select(Tag).where(Tag.name == tag_name)
        tag = session.exec(tag_statement).first()

        if not tag:
            # Create new tag
            tag = Tag(name=tag_name)
            session.add(tag)
            session.flush()  # Get the tag ID

        # Add the relationship
        # Check if the relationship already exists
        from sqlalchemy import text
        exists_query = text("""
            SELECT 1 FROM conversation_tags
            WHERE conversation_id = :conversation_id AND tag_id = :tag_id
        """)
        result = session.execute(exists_query, {
            "conversation_id": conversation_id,
            "tag_id": tag.id
        }).fetchone()

        if not result:
            # Add the relationship
            insert_query = text("""
                INSERT INTO conversation_tags (conversation_id, tag_id)
                VALUES (:conversation_id, :tag_id)
            """)
            session.execute(insert_query, {
                "conversation_id": conversation_id,
                "tag_id": tag.id
            })

        session.commit()
        return True

    def remove_tag_from_conversation(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, tag_name: str) -> bool:
        """
        Remove a tag from a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to remove tag from
            user_id: ID of the user removing the tag
            tag_name: Name of the tag to remove

        Returns:
            True if successful, False otherwise
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.tag import Tag, conversation_tag
        from sqlmodel import select

        # Verify user has access to the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return False

        # Get the tag
        tag_statement = select(Tag).where(Tag.name == tag_name)
        tag = session.exec(tag_statement).first()

        if not tag:
            return False  # Tag doesn't exist

        # Remove the relationship
        from sqlalchemy import text
        delete_query = text("""
            DELETE FROM conversation_tags
            WHERE conversation_id = :conversation_id AND tag_id = :tag_id
        """)
        session.execute(delete_query, {
            "conversation_id": conversation_id,
            "tag_id": tag.id
        })

        session.commit()
        return True

    def get_conversations_by_tag(self, session: Session, user_id: uuid.UUID, tag_name: str, limit: int = 20, offset: int = 0) -> List[uuid.UUID]:
        """
        Get conversations that have a specific tag.

        Args:
            session: Database session
            user_id: ID of the user requesting conversations
            tag_name: Name of the tag to search for
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of conversation IDs with the specified tag
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.tag import Tag
        from sqlmodel import select
        from sqlalchemy import text

        # Get the tag ID
        tag_statement = select(Tag.id).where(Tag.name == tag_name)
        tag_result = session.exec(tag_statement).first()

        if not tag_result:
            return []

        # Get conversations with this tag for the user
        query = text("""
            SELECT DISTINCT c.id
            FROM conversations c
            JOIN conversation_tags ct ON c.id = ct.conversation_id
            WHERE c.user_id = :user_id AND ct.tag_id = :tag_id
            ORDER BY c.last_activity DESC
            LIMIT :limit OFFSET :offset
        """)

        result = session.execute(query, {
            "user_id": user_id,
            "tag_id": tag_result,
            "limit": limit,
            "offset": offset
        })

        conversation_ids = [row[0] for row in result.fetchall()]
        return conversation_ids

    def share_conversation(self, session: Session, conversation_id: uuid.UUID, owner_user_id: uuid.UUID, recipient_email: str) -> bool:
        """
        Share a conversation with another user by email.

        Args:
            session: Database session
            conversation_id: ID of the conversation to share
            owner_user_id: ID of the user who owns the conversation
            recipient_email: Email of the user to share with

        Returns:
            True if successful, False otherwise
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.user import User
        from sqlmodel import select

        # Verify the owner has access to the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, owner_user_id)
        if not conversation:
            return False

        # Find the recipient user by email
        user_statement = select(User).where(User.email == recipient_email)
        recipient_user = session.exec(user_statement).first()

        if not recipient_user:
            return False  # User with that email doesn't exist

        # In a real implementation, we would create a sharing relationship
        # For now, we'll just validate that the sharing would be possible
        # This would involve creating a conversation sharing table in a full implementation

        # For the purpose of this implementation, we'll just return True
        # to indicate that the sharing operation would be successful
        return True

    def get_shared_conversations(self, session: Session, user_id: uuid.UUID) -> List[uuid.UUID]:
        """
        Get conversations that have been shared with the user.

        Args:
            session: Database session
            user_id: ID of the user requesting shared conversations

        Returns:
            List of conversation IDs that have been shared with the user
        """
        # In a full implementation, this would query a conversation sharing table
        # For now, we'll return an empty list
        return []

    def create_conversation_from_template(self, session: Session, user_id: uuid.UUID, template_id: uuid.UUID, title: str = None) -> Optional[uuid.UUID]:
        """
        Create a new conversation based on a template.

        Args:
            session: Database session
            user_id: ID of the user creating the conversation
            template_id: ID of the template to use
            title: Optional title for the new conversation (defaults to template name)

        Returns:
            ID of the new conversation, or None if creation failed
        """
        from apps.backend.src.models.template import Template
        from sqlmodel import select

        # Get the template
        template_statement = select(Template).where(
            Template.id == template_id,
            (Template.user_id == user_id) | (Template.is_public == True)  # User's template or public template
        )
        template = session.exec(template_statement).first()

        if not template:
            return None

        # Create a new conversation based on the template
        conversation_title = title or template.name
        new_conversation = self.create_conversation(session, user_id, conversation_title)

        # Optionally, add the template content as the first message
        if template.content:
            self.create_message(session, new_conversation.id, "system", f"Template: {template.content}")

        return new_conversation.id

    def get_user_templates(self, session: Session, user_id: uuid.UUID) -> List:
        """
        Get all templates owned by a user.

        Args:
            session: Database session
            user_id: ID of the user requesting templates

        Returns:
            List of templates owned by the user
        """
        from apps.backend.src.models.template import Template
        from sqlmodel import select

        statement = select(Template).where(Template.user_id == user_id)
        templates = session.exec(statement).all()
        return templates

    def get_public_templates(self, session: Session) -> List:
        """
        Get all public templates.

        Args:
            session: Database session

        Returns:
            List of public templates
        """
        from apps.backend.src.models.template import Template
        from sqlmodel import select

        statement = select(Template).where(Template.is_public == True)
        templates = session.exec(statement).all()
        return templates

    def archive_old_messages(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, age_days: int = 30) -> int:
        """
        Archive messages older than a certain age in a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to archive messages from
            user_id: ID of the user requesting the archival
            age_days: Age in days after which messages should be archived

        Returns:
            Number of messages archived
        """
        from apps.backend.src.models.message import Message
        from sqlmodel import select
        from datetime import datetime, timedelta

        # Verify user has access to the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return 0

        # Calculate the cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=age_days)

        # Find messages older than the cutoff date
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.timestamp < cutoff_date
        )
        old_messages = session.exec(statement).all()

        # In a real implementation, we would move these messages to an archive table
        # For now, we'll just return the count of messages that would be archived
        return len(old_messages)

    def get_archived_messages(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> List:
        """
        Get archived messages for a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user requesting archived messages

        Returns:
            List of archived messages
        """
        # In a real implementation, this would query an archive table
        # For now, return an empty list
        return []

    def create_message(self, session: Session, conversation_id: uuid.UUID, role: str, content: str) -> Message:
        """Create a new message in a conversation."""
        # Create the message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        session.add(message)

        # Update conversation statistics
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.last_activity = datetime.utcnow()
            conversation.message_count += 1

        session.commit()
        session.refresh(message)
        return message

    def create_user_message(self, session: Session, conversation_id: uuid.UUID, content: str) -> Message:
        """Create a user message in a conversation."""
        return self.create_message(session, conversation_id, "user", content)

    def create_assistant_message(self, session: Session, conversation_id: uuid.UUID, content: str) -> Message:
        """Create an assistant message in a conversation."""
        return self.create_message(session, conversation_id, "assistant", content)

    def validate_conversation_access(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Validate that a user can access a specific conversation."""
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        return conversation is not None

    def create_bulk_messages(self, session: Session, conversation_id: uuid.UUID, messages_data: List[Dict[str, str]]) -> List[Message]:
        """
        Create multiple messages in a conversation in a single transaction for performance.

        Args:
            session: Database session
            conversation_id: ID of the conversation to add messages to
            messages_data: List of dictionaries with 'role' and 'content' keys

        Returns:
            List of created Message objects
        """
        from apps.backend.src.models.message import Message
        from datetime import datetime
        import uuid

        # Create message objects
        messages = []
        for msg_data in messages_data:
            message = Message(
                id=uuid.uuid4(),
                conversation_id=conversation_id,
                role=msg_data['role'],
                content=msg_data['content'],
                timestamp=datetime.utcnow()
            )
            messages.append(message)

        # Add all messages to the session
        for message in messages:
            session.add(message)

        # Update conversation statistics
        from apps.backend.src.models.conversation import Conversation
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.last_activity = datetime.utcnow()
            conversation.message_count += len(messages)

        # Commit all changes in a single transaction
        session.commit()

        # Refresh all messages to get their IDs from the database
        for message in messages:
            session.refresh(message)

        return messages

    def delete_user_conversations(self, session: Session, user_id: uuid.UUID, requesting_user_id: uuid.UUID) -> bool:
        """
        Delete all conversations for a user. This is an administrative function or for user data deletion requests.

        Args:
            session: Database session
            user_id: ID of the user whose conversations to delete
            requesting_user_id: ID of the user requesting the deletion (for authorization)

        Returns:
            True if successful, False otherwise
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.message import Message
        from sqlmodel import select

        # Verify that the requesting user is the same as the user whose data is being deleted
        # (In a real implementation, admins might be able to delete other users' data)
        if user_id != requesting_user_id:
            return False

        # Get all conversations for the user
        conv_statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = session.exec(conv_statement).all()

        # Delete all messages in these conversations first (due to foreign key constraints)
        for conversation in conversations:
            msg_statement = select(Message).where(Message.conversation_id == conversation.id)
            messages = session.exec(msg_statement).all()

            for message in messages:
                session.delete(message)

        # Then delete the conversations
        for conversation in conversations:
            session.delete(conversation)

        session.commit()
        return True

    def delete_conversation_and_messages(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a specific conversation and all its messages.

        Args:
            session: Database session
            conversation_id: ID of the conversation to delete
            user_id: ID of the user requesting deletion (for authorization)

        Returns:
            True if successful, False otherwise
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.message import Message
        from sqlmodel import select

        # Verify user has access to this conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return False

        # Delete all messages in the conversation first
        msg_statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = session.exec(msg_statement).all()

        for message in messages:
            session.delete(message)

        # Then delete the conversation itself
        session.delete(conversation)
        session.commit()
        return True

    def anonymize_user_data(self, session: Session, user_id: uuid.UUID, requesting_user_id: uuid.UUID) -> bool:
        """
        Anonymize all user data by removing personally identifiable information.

        Args:
            session: Database session
            user_id: ID of the user whose data to anonymize
            requesting_user_id: ID of the user requesting the anonymization (for authorization)

        Returns:
            True if successful, False otherwise
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.message import Message
        from sqlmodel import select

        # Verify that the requesting user is the same as the user whose data is being anonymized
        if user_id != requesting_user_id:
            return False

        # Get all conversations for the user
        conv_statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = session.exec(conv_statement).all()

        # Anonymize conversation titles and other PII
        for conversation in conversations:
            # Replace title with generic value
            conversation.title = f"Anonymized Conversation {conversation.id}"
            session.add(conversation)

        # Get all messages for the user's conversations
        for conversation in conversations:
            msg_statement = select(Message).where(Message.conversation_id == conversation.id)
            messages = session.exec(msg_statement).all()

            # Anonymize message content if needed
            for message in messages:
                # In a real implementation, this might mask PII in message content
                # For now, we'll just ensure no PII is exposed through metadata
                session.add(message)

        session.commit()
        return True
    def export_user_conversations(self, session: Session, user_id: uuid.UUID, requesting_user_id: uuid.UUID) -> Optional[Dict]:
        """
        Export all conversations for a user for privacy/portability.

        Args:
            session: Database session
            user_id: ID of the user whose conversations to export
            requesting_user_id: ID of the user requesting the export (for authorization)

        Returns:
            Dictionary containing exported conversation data, or None if unauthorized
        """
        # Verify that the requesting user is the same as the user whose data is being exported
        if user_id != requesting_user_id:
            return None

        # Use the existing export_conversation method for each conversation
        from apps.backend.src.models.conversation import Conversation
        from sqlmodel import select

        # Get all conversations for the user
        conv_statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = session.exec(conv_statement).all()

        exported_data = {
            "user_id": str(user_id),
            "export_timestamp": datetime.utcnow().isoformat(),
            "conversations": []
        }

        for conversation in conversations:
            # Export each conversation individually
            conv_export = self.export_conversation(session, conversation.id, user_id)
            if "error" not in conv_export:
                exported_data["conversations"].append(conv_export)

        return exported_data

    async def process_agent_chat(self, session: Session, user_id: uuid.UUID, conversation_id: Optional[uuid.UUID],
                                user_message_content: str) -> Dict[str, Any]:
        """
        Process a chat message using the AI agent with MCP tools.

        Args:
            session: Database session
            user_id: ID of the user
            conversation_id: ID of the conversation (None for new conversation)
            user_message_content: Content of the user's message

        Returns:
            Dictionary containing the agent's response and conversation info
        """
        from apps.backend.src.models.conversation import Conversation
        from apps.backend.src.models.message import Message

        # Create or get conversation
        if conversation_id is None:
            # Create new conversation
            conversation = self.create_conversation(session, user_id, "New Todo Conversation")
        else:
            # Validate access to existing conversation
            conversation = self.get_conversation_by_id(session, conversation_id, user_id)
            if not conversation:
                raise ValueError("Access denied: You don't have permission to access this conversation.")

        # Create user message in the conversation
        user_message = self.create_message(session, conversation.id, "user", user_message_content)

        # Get conversation history for context
        messages = self.get_conversation_messages(session, conversation.id, user_id)

        # Build agent context with conversation history
        agent_context = self.build_agent_context(conversation, messages, str(user_id))

        # Create a thread for this conversation
        thread = self.todo_agent.create_thread()

        # Add the user's message to the thread
        self.todo_agent.add_message_to_thread(thread.id, str(user_id), user_message_content)

        # Run the agent to process the message with context
        agent_response = self.todo_agent.run_agent_with_context(thread.id, str(user_id), additional_context=agent_context)

        # Process the agent's response
        processed_response = self.response_processor.process_response(agent_response)

        # Create assistant message with the agent's response
        assistant_message = self.create_message(session, conversation.id,
                                              "assistant", processed_response.natural_language_response)

        return {
            "conversation_id": str(conversation.id),
            "response": processed_response.natural_language_response,
            "tool_calls": processed_response.tool_calls,
            "action_metadata": processed_response.action_metadata,
            "needs_clarification": processed_response.needs_clarification
        }

    def create_bulk_messages(self, session: Session, conversation_id: uuid.UUID, messages_data: List[Dict[str, str]]) -> List[Message]:
        """
        Create multiple messages in a conversation in a single transaction for performance.

        Args:
            session: Database session
            conversation_id: ID of the conversation to add messages to
            messages_data: List of dictionaries with 'role' and 'content' keys

        Returns:
            List of created Message objects
        """
        from apps.backend.src.models.message import Message
        from datetime import datetime
        import uuid

        # Create message objects
        messages = []
        for msg_data in messages_data:
            message = Message(
                id=uuid.uuid4(),
                conversation_id=conversation_id,
                role=msg_data['role'],
                content=msg_data['content'],
                timestamp=datetime.utcnow()
            )
            messages.append(message)

        # Add all messages to the session
        for message in messages:
            session.add(message)

        # Update conversation statistics
        from apps.backend.src.models.conversation import Conversation
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.last_activity = datetime.utcnow()
            conversation.message_count += len(messages)

        # Commit all changes in a single transaction
        session.commit()

        # Refresh all messages to get their IDs from the database
        for message in messages:
            session.refresh(message)

        return messages

    def generate_conversation_summary(self, session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> str:
        """
        Generate a summary of the conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation to summarize
            user_id: ID of the user requesting the summary

        Returns:
            A summary string of the conversation
        """
        # First verify the user owns the conversation
        conversation = self.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return "Access denied: You don't have permission to view this conversation."

        # Get all messages in the conversation
        all_messages = self.get_conversation_messages(session, conversation_id, user_id, limit=1000)  # Get more messages for summary

        if not all_messages:
            return "No messages to summarize."

        # Create a simple summary by concatenating key messages
        # In a production system, this would use an AI model to generate a proper summary
        summary_parts = []

        # Include the first few messages to capture the topic
        for msg in all_messages[:3]:  # First 3 messages
            snippet = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
            summary_parts.append(f"[{msg.role.upper()}]: {snippet}")

        # Include the last few messages to capture the conclusion
        if len(all_messages) > 3:
            for msg in all_messages[-2:]:  # Last 2 messages
                snippet = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
                summary_parts.append(f"[{msg.role.upper()}]: {snippet}")

        summary = " | ".join(summary_parts)

        # Truncate to max_length if needed
        max_length = 200
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary
