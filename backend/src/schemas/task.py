"""Task Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# Priority type for validation
PriorityType = Literal["low", "medium", "high", "urgent"]

# Recurrence type
RecurrenceType = Literal["daily", "weekly", "monthly", "yearly"]


class RecurrencePattern(BaseModel):
    """Schema for task recurrence configuration."""

    type: RecurrenceType
    interval: int = Field(default=1, ge=1, le=365)
    days_of_week: list[int] | None = Field(
        default=None,
        description="Days of week for weekly recurrence (0=Monday, 6=Sunday)",
    )
    day_of_month: int | None = Field(
        default=None,
        ge=1,
        le=31,
        description="Day of month for monthly recurrence",
    )
    end_date: datetime | None = Field(default=None, description="When recurrence ends")
    occurrences: int | None = Field(
        default=None,
        ge=1,
        description="Max number of occurrences",
    )

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: list[int] | None) -> list[int] | None:
        """Validate days are 0-6."""
        if v is not None:
            if not all(0 <= d <= 6 for d in v):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
            return sorted(set(v))
        return v


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    # Phase V: Advanced fields
    due_date: datetime | None = Field(default=None, description="Task due date")
    priority: PriorityType = Field(default="medium", description="Task priority level")
    tags: list[str] = Field(default=[], max_length=20, description="Task tags")
    recurrence_pattern: RecurrencePattern | None = Field(
        default=None,
        description="Recurrence configuration for repeating tasks",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: str | None) -> str | None:
        """Strip whitespace from description."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and clean tags."""
        cleaned = [tag.strip().lower() for tag in v if tag.strip()]
        # Remove duplicates while preserving order
        seen: set[str] = set()
        unique = []
        for tag in cleaned:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
        return unique


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    # Phase V: Advanced fields
    due_date: datetime | None = Field(default=None, description="Task due date")
    priority: PriorityType | None = Field(default=None, description="Task priority level")
    tags: list[str] | None = Field(default=None, max_length=20, description="Task tags")
    recurrence_pattern: RecurrencePattern | None = Field(
        default=None,
        description="Recurrence configuration",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        """Validate title is not empty after stripping whitespace."""
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            return v.strip()
        return None

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: str | None) -> str | None:
        """Strip whitespace from description."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate and clean tags."""
        if v is None:
            return None
        cleaned = [tag.strip().lower() for tag in v if tag.strip()]
        seen: set[str] = set()
        unique = []
        for tag in cleaned:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
        return unique


class TaskComplete(BaseModel):
    """Schema for toggling task completion status."""

    completed: bool | None = None


class TaskResponse(BaseModel):
    """Schema for task API response."""

    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    # Phase V: Advanced fields
    due_date: datetime | None
    priority: str
    tags: list[str]
    recurrence_pattern: dict[str, Any] | None
    next_occurrence: datetime | None
    reminder_sent: bool
    is_overdue: bool = Field(default=False, description="Whether task is past due date")
    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_task(cls, task: Any) -> "TaskResponse":
        """Create TaskResponse from Task model with computed fields."""
        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            due_date=task.due_date,
            priority=task.priority,
            tags=task.tags or [],
            recurrence_pattern=task.recurrence_pattern,
            next_occurrence=task.next_occurrence,
            reminder_sent=task.reminder_sent,
            is_overdue=task.is_overdue() if hasattr(task, "is_overdue") else False,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskListResponse(BaseModel):
    """Schema for list of tasks API response."""

    tasks: list[TaskResponse]
    total: int


class TaskFilters(BaseModel):
    """Schema for task filtering parameters."""

    status: Literal["pending", "completed", "all"] | None = None
    priority: PriorityType | None = None
    tags: list[str] | None = None
    due_before: datetime | None = None
    due_after: datetime | None = None
    search: str | None = Field(None, min_length=1, max_length=100)
    sort_by: Literal["created_at", "due_date", "priority", "title"] = "created_at"
    order: Literal["asc", "desc"] = "desc"
