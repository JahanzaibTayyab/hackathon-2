"""Event schemas for Kafka/Dapr pub/sub."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskEvent(BaseModel):
    """Event schema for task-related events.

    Compatible with CloudEvents specification.
    """

    event_type: Literal[
        "task.created",
        "task.updated",
        "task.completed",
        "task.uncompleted",
        "task.deleted"
    ]
    task_id: int
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any] = Field(default_factory=dict)

    # CloudEvents metadata
    specversion: str = "1.0"
    source: str = "todo-app/backend"

    def to_cloudevent(self) -> dict[str, Any]:
        """Convert to CloudEvents format."""
        return {
            "specversion": self.specversion,
            "type": self.event_type,
            "source": self.source,
            "id": f"{self.task_id}-{self.timestamp.isoformat()}",
            "time": self.timestamp.isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "task_id": self.task_id,
                "user_id": self.user_id,
                **self.data
            }
        }


class ReminderEvent(BaseModel):
    """Event schema for reminder notifications."""

    event_type: Literal["reminder.due_soon", "reminder.overdue"]
    task_id: int
    user_id: str
    due_date: datetime
    title: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # CloudEvents metadata
    specversion: str = "1.0"
    source: str = "todo-app/reminder-service"

    def to_cloudevent(self) -> dict[str, Any]:
        """Convert to CloudEvents format."""
        return {
            "specversion": self.specversion,
            "type": self.event_type,
            "source": self.source,
            "id": f"reminder-{self.task_id}-{self.timestamp.isoformat()}",
            "time": self.timestamp.isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "task_id": self.task_id,
                "user_id": self.user_id,
                "due_date": self.due_date.isoformat(),
                "title": self.title
            }
        }


class TaskUpdateEvent(BaseModel):
    """Event schema for real-time task updates (WebSocket/SSE)."""

    event_type: Literal["task.sync"]
    user_id: str
    action: Literal["create", "update", "delete", "complete"]
    task_id: int
    task_data: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
