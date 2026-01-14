"""Task database model."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from src.models.types import JSONDict, StringArray


class Task(SQLModel, table=True):
    """Task model representing a todo item."""

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to users.id (users table managed by Better Auth)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)

    # Phase V: Advanced task features
    due_date: datetime | None = Field(default=None)
    priority: str = Field(default="medium", max_length=10)  # low, medium, high, urgent
    tags: list[str] = Field(default_factory=list, sa_column=Column(StringArray))
    recurrence_pattern: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONDict))
    next_occurrence: datetime | None = Field(default=None)
    reminder_sent: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def mark_updated(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def is_overdue(self) -> bool:
        """Check if task is overdue (has due_date in the past and not completed)."""
        if self.completed or self.due_date is None:
            return False
        return datetime.now(UTC) > self.due_date

    def is_recurring(self) -> bool:
        """Check if task has a recurrence pattern."""
        return self.recurrence_pattern is not None
