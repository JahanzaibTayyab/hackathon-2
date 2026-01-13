"""Message database model for chat messages."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """Message model representing a chat message in a conversation."""

    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)  # Foreign key to users.id (users table managed by Better Auth)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str
    tool_calls: str | None = Field(default=None)  # JSON string of tool calls
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
