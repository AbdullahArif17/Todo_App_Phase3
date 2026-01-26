from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Shared properties
class UserBase(BaseModel):
    email: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    email: Optional[str] = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str