from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .todo_task import TodoTask
    from .template import Template
    from .conversation import Conversation

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = Field(default=None)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with todos
    todos: List["TodoTask"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    # Relationship with templates
    templates: List["Template"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    # Relationship with conversations
    conversations: List["Conversation"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

# Model for creating a new user
class UserCreate(UserBase):
    password: str

# Model for user registration response
class UserRegister(UserBase):
    id: uuid.UUID
    created_at: datetime

# Model for user login
class UserLogin(SQLModel):
    email: str
    password: str

# Model for user response (without sensitive data)
class UserResponse(SQLModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

# Model for updating user
class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None