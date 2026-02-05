from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid
from sqlalchemy import Index, Column, Table, ForeignKey

if TYPE_CHECKING:
    from apps.backend.src.models.user import User
    from apps.backend.src.models.message import Message
    from apps.backend.src.models.tag import Tag

# Association table for many-to-many relationship between Conversation and Tag (defined here to avoid circular imports)
conversation_tag = Table(
    "conversation_tags",
    Column("conversation_id", uuid.UUID, ForeignKey("conversations.id")),
    Column("tag_id", uuid.UUID, ForeignKey("tags.id")),
)


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
        link_model=conversation_tag
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