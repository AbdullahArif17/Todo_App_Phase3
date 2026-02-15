from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid
from sqlalchemy import Index

if TYPE_CHECKING:
    from models.user import User
    from models.message import Message
    from models.tag import Tag, ConversationTag

# Using ConversationTag from tag.py would be better, but if we must define it here:
class ConversationTag(SQLModel, table=True):
    __tablename__ = "conversation_tags"
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class ConversationBase(SQLModel):
    title: str = Field(default="New Conversation", max_length=255)
    user_id: uuid.UUID = Field(foreign_key="users.id")


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)  # Add index
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index

    # Additional fields for performance optimization
    last_activity: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index
    message_count: int = Field(default=0, index=True)  # Add index for performance
    is_archived: bool = Field(default=False, index=True)  # Add index for filtering

    # Fields for conversation branching support
    parent_conversation_id: Optional[uuid.UUID] = Field(default=None, foreign_key="conversations.id", index=True)  # For branching
    branch_depth: int = Field(default=0, index=True)  # How deep this conversation is in a branch
    is_branch_point: bool = Field(default=False, index=True)  # Whether this conversation has branches

    # Relationship to tags
    tags: List["Tag"] = Relationship(
        back_populates="conversations",
        link_model=ConversationTag
    )

    # Add table-level indexes
    __table_args__ = (
        Index('idx_conversation_user_activity', 'user_id', 'last_activity'),  # Composite index
        Index('idx_conversation_user_created', 'user_id', 'created_at'),      # Composite index
        Index('idx_conversation_parent', 'parent_conversation_id'),           # Index for branch relationships
        Index('idx_conversation_branch_depth', 'branch_depth'),               # Index for branch depth
    )


class ConversationRead(ConversationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime