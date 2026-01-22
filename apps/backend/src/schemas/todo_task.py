from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Shared properties
class TodoTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False

# Properties to receive via API on creation
class TodoTaskCreate(TodoTaskBase):
    title: str

# Properties to receive via API on update
class TodoTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TodoTaskInDBBase(TodoTaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Additional properties to return via API
class TodoTask(TodoTaskInDBBase):
    pass

# Additional properties stored in DB
class TodoTaskInDB(TodoTaskInDBBase):
    pass