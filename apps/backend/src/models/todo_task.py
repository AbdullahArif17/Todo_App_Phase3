from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class TodoTask(SQLModel, table=True):
    """
    Represents a user's task with title, description, and completion status
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})