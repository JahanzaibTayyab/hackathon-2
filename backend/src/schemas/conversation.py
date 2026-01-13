"""Conversation Pydantic schemas for API responses."""

from datetime import datetime

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Schema for message in conversation response."""

    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    """Schema for conversation summary in list response."""

    id: int
    created_at: datetime
    updated_at: datetime
    message_count: int


class ConversationListResponse(BaseModel):
    """Schema for list of conversations response."""

    conversations: list[ConversationSummary]


class ConversationResponse(BaseModel):
    """Schema for conversation with messages response."""

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

    model_config = {"from_attributes": True}
