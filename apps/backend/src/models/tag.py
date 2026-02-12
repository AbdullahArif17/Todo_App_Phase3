from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .conversation import Conversation


class ConversationTag(SQLModel, table=True):
    __tablename__ = "conversation_tags"
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class TagBase(SQLModel):
    name: str = Field(max_length=100, nullable=False, unique=True, index=True)
    color: str = Field(default="#007bff", max_length=7)  # Hex color code


class Tag(TagBase, table=True):
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversations
    conversations: List["Conversation"] = Relationship(
        back_populates="tags",
        link_model=ConversationTag
    )


class TagRead(TagBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime