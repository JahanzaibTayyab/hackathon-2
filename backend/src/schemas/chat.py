"""Chat Pydantic schemas for API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Schema for chat request."""

    message: str = Field(..., min_length=1)
    conversation_id: int | None = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Validate message is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ToolCall(BaseModel):
    """Schema for an MCP tool call made by the assistant."""

    tool_name: str
    arguments: dict[str, Any]
    result: Any


class ChatResponse(BaseModel):
    """Schema for chat response."""

    conversation_id: int
    response: str
    tool_calls: list[ToolCall] = []
