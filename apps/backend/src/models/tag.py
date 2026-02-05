from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List
from datetime import datetime
import uuid
from sqlalchemy import Column, Table, ForeignKey

if TYPE_CHECKING:
    from apps.backend.src.models.conversation import Conversation


# Association table for many-to-many relationship between Conversation and Tag
conversation_tag = Table(
    "conversation_tags",
    Column("conversation_id", uuid.UUID, ForeignKey("conversations.id")),
    Column("tag_id", uuid.UUID, ForeignKey("tags.id"))
)


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
        link_model=conversation_tag
    )


class TagRead(TagBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime