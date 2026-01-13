"""Conversation database model for chat sessions."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation model representing a chat session."""

    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to users.id (users table managed by Better Auth)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def mark_updated(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)
