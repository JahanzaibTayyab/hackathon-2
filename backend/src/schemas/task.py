"""Task Pydantic schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

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


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for list of tasks API response."""

    tasks: list[TaskResponse]
    total: int
