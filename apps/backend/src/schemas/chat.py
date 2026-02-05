from pydantic import BaseModel
from typing import Optional, List
import uuid


class ChatRequest(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    message: str
    user_id: Optional[uuid.UUID] = None  # Will be extracted from JWT token


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    response: str
    message_id: Optional[uuid.UUID] = None


class ConversationListResponse(BaseModel):
    conversations: List['ConversationRead']


class MessageListResponse(BaseModel):
    messages: List['MessageRead']