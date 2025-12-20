"""Task database model."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task model representing a todo item."""

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to users.id (users table managed by Better Auth)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def mark_updated(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)
