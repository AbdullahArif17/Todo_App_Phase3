from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
import uuid
from sqlalchemy import Index

if TYPE_CHECKING:
    from models.user import User


class TemplateBase(SQLModel):
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: str = Field(nullable=False)  # The template content
    user_id: uuid.UUID = Field(foreign_key="users.id")  # Templates are user-specific
    is_public: bool = Field(default=False)  # Whether the template is public


class Template(TemplateBase, table=True):
    __tablename__ = "templates"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationship to user who owns the template
    user: "User" = Relationship(back_populates="templates")

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Add table-level indexes
    __table_args__ = (
        Index('idx_template_user', 'user_id'),  # Index for user-specific queries
        Index('idx_template_public', 'is_public'),  # Index for public templates
        Index('idx_template_user_public', 'user_id', 'is_public'),  # Composite index
    )


class TemplateRead(TemplateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime