from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
import uuid
from sqlalchemy import Index
if TYPE_CHECKING:
    from apps.backend.src.models.conversation import Conversation


class MessageBase(SQLModel):
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)  # Add index
    role: str = Field(sa_column_kwargs={"index": True})  # Add index
    content: str = Field(sa_column_kwargs={"nullable": False, "index": True})  # Add index for search
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index


class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation: "Conversation" = Relationship(back_populates="messages")

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index

    # Tool integration fields (for AI agent)
    tool_calls: Optional[str] = Field(default=None, sa_column_kwargs={"index": True})  # JSON string of tool calls
    tool_results: Optional[str] = Field(default=None, sa_column_kwargs={"index": True})  # JSON string of tool results
    needs_clarification: bool = Field(default=False, index=True)  # Whether agent needs clarification from user

    # Add table-level indexes
    __table_args__ = (
        Index('idx_message_conversation_timestamp', 'conversation_id', 'timestamp'),  # Composite index
        Index('idx_message_conversation_role', 'conversation_id', 'role'),            # Composite index
        Index('idx_message_role_timestamp', 'role', 'timestamp'),                    # Composite index
        Index('idx_message_needs_clarification', 'needs_clarification'),             # Index for clarification needs
    )


class MessageRead(MessageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tool_calls: Optional[str] = None
    tool_results: Optional[str] = None
    needs_clarification: bool