"""Event producer for publishing task events to Kafka via Dapr."""

import logging
from datetime import UTC, datetime
from typing import Any

from src.core.dapr import dapr_client
from src.events.schemas import ReminderEvent, TaskEvent, TaskUpdateEvent

logger = logging.getLogger(__name__)

# Topic names
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"
TASK_UPDATES_TOPIC = "task-updates"


class EventProducer:
    """Producer for publishing events to Kafka topics via Dapr."""

    async def publish_task_created(
        self,
        task_id: int,
        user_id: str,
        data: dict[str, Any]
    ) -> bool:
        """
        Publish task.created event.

        Args:
            task_id: ID of the created task
            user_id: ID of the user who created the task
            data: Task data

        Returns:
            True if successful
        """
        event = TaskEvent(
            event_type="task.created",
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.now(UTC),
            data=data
        )
        return await dapr_client.publish(TASK_EVENTS_TOPIC, event.to_cloudevent())

    async def publish_task_updated(
        self,
        task_id: int,
        user_id: str,
        data: dict[str, Any]
    ) -> bool:
        """
        Publish task.updated event.

        Args:
            task_id: ID of the updated task
            user_id: ID of the user who updated the task
            data: Updated task data

        Returns:
            True if successful
        """
        event = TaskEvent(
            event_type="task.updated",
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.now(UTC),
            data=data
        )
        return await dapr_client.publish(TASK_EVENTS_TOPIC, event.to_cloudevent())

    async def publish_task_completed(
        self,
        task_id: int,
        user_id: str
    ) -> bool:
        """
        Publish task.completed event.

        Args:
            task_id: ID of the completed task
            user_id: ID of the user who completed the task

        Returns:
            True if successful
        """
        event = TaskEvent(
            event_type="task.completed",
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.now(UTC),
            data={"completed": True}
        )
        return await dapr_client.publish(TASK_EVENTS_TOPIC, event.to_cloudevent())

    async def publish_task_uncompleted(
        self,
        task_id: int,
        user_id: str
    ) -> bool:
        """
        Publish task.uncompleted event.

        Args:
            task_id: ID of the uncompleted task
            user_id: ID of the user who uncompleted the task

        Returns:
            True if successful
        """
        event = TaskEvent(
            event_type="task.uncompleted",
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.now(UTC),
            data={"completed": False}
        )
        return await dapr_client.publish(TASK_EVENTS_TOPIC, event.to_cloudevent())

    async def publish_task_deleted(
        self,
        task_id: int,
        user_id: str
    ) -> bool:
        """
        Publish task.deleted event.

        Args:
            task_id: ID of the deleted task
            user_id: ID of the user who deleted the task

        Returns:
            True if successful
        """
        event = TaskEvent(
            event_type="task.deleted",
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.now(UTC),
            data={}
        )
        return await dapr_client.publish(TASK_EVENTS_TOPIC, event.to_cloudevent())

    async def publish_reminder_due_soon(
        self,
        task_id: int,
        user_id: str,
        due_date: datetime,
        title: str
    ) -> bool:
        """
        Publish reminder.due_soon event.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            due_date: Task due date
            title: Task title

        Returns:
            True if successful
        """
        event = ReminderEvent(
            event_type="reminder.due_soon",
            task_id=task_id,
            user_id=user_id,
            due_date=due_date,
            title=title,
            timestamp=datetime.now(UTC)
        )
        return await dapr_client.publish(REMINDERS_TOPIC, event.to_cloudevent())

    async def publish_reminder_overdue(
        self,
        task_id: int,
        user_id: str,
        due_date: datetime,
        title: str
    ) -> bool:
        """
        Publish reminder.overdue event.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            due_date: Task due date
            title: Task title

        Returns:
            True if successful
        """
        event = ReminderEvent(
            event_type="reminder.overdue",
            task_id=task_id,
            user_id=user_id,
            due_date=due_date,
            title=title,
            timestamp=datetime.now(UTC)
        )
        return await dapr_client.publish(REMINDERS_TOPIC, event.to_cloudevent())

    async def publish_task_sync(
        self,
        user_id: str,
        action: str,
        task_id: int,
        task_data: dict[str, Any] | None = None
    ) -> bool:
        """
        Publish task sync event for real-time updates.

        Args:
            user_id: ID of the user
            action: Action type (create, update, delete, complete)
            task_id: ID of the task
            task_data: Task data (optional)

        Returns:
            True if successful
        """
        event = TaskUpdateEvent(
            event_type="task.sync",
            user_id=user_id,
            action=action,  # type: ignore
            task_id=task_id,
            task_data=task_data,
            timestamp=datetime.now(UTC)
        )
        return await dapr_client.publish(
            TASK_UPDATES_TOPIC,
            event.model_dump(mode="json")
        )


# Singleton instance
event_producer = EventProducer()
