"""Event consumer endpoints for Dapr pub/sub."""

import logging
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/tasks")
async def handle_task_event(request: Request) -> dict[str, str]:
    """
    Handle task-events topic messages from Dapr.

    This endpoint receives CloudEvents from the task-events Kafka topic.
    Events are used for:
    - Analytics and logging
    - Triggering downstream processes
    - Audit trail

    Args:
        request: Incoming request with CloudEvent payload

    Returns:
        Acknowledgment response
    """
    try:
        event = await request.json()
        event_type = event.get("type", "unknown")
        event_id = event.get("id", "unknown")
        data = event.get("data", {})

        logger.info(
            f"Received task event: type={event_type}, id={event_id}, "
            f"task_id={data.get('task_id')}, user_id={data.get('user_id')}"
        )

        # Process based on event type
        if event_type == "task.created":
            logger.info(f"Task created: {data.get('task_id')}")
            # Could trigger: notifications, analytics, etc.

        elif event_type == "task.updated":
            logger.info(f"Task updated: {data.get('task_id')}")

        elif event_type == "task.completed":
            logger.info(f"Task completed: {data.get('task_id')}")
            # Could trigger: gamification, streak tracking, etc.

        elif event_type == "task.deleted":
            logger.info(f"Task deleted: {data.get('task_id')}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        # Return ok to avoid message redelivery for non-retryable errors
        return {"status": "error", "message": str(e)}


@router.post("/reminders")
async def handle_reminder_event(request: Request) -> dict[str, str]:
    """
    Handle reminders topic messages from Dapr.

    This endpoint receives reminder events for tasks that are:
    - Due soon (configurable threshold)
    - Overdue

    Args:
        request: Incoming request with CloudEvent payload

    Returns:
        Acknowledgment response
    """
    try:
        event = await request.json()
        event_type = event.get("type", "unknown")
        data = event.get("data", {})

        logger.info(
            f"Received reminder event: type={event_type}, "
            f"task_id={data.get('task_id')}, title={data.get('title')}"
        )

        if event_type == "reminder.due_soon":
            logger.info(
                f"Task due soon: {data.get('title')} - "
                f"Due: {data.get('due_date')}"
            )
            # TODO: Create in-app notification
            # TODO: Send email/push notification

        elif event_type == "reminder.overdue":
            logger.warning(
                f"Task overdue: {data.get('title')} - "
                f"Was due: {data.get('due_date')}"
            )
            # TODO: Create urgent notification
            # TODO: Send escalation notification

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/task-updates")
async def handle_task_update_event(request: Request) -> dict[str, str]:
    """
    Handle task-updates topic messages for real-time sync.

    This endpoint receives task sync events that can be:
    - Forwarded to WebSocket connections
    - Used for SSE (Server-Sent Events)
    - Stored for offline sync

    Args:
        request: Incoming request with event payload

    Returns:
        Acknowledgment response
    """
    try:
        event = await request.json()
        user_id = event.get("user_id")
        action = event.get("action")
        task_id = event.get("task_id")

        logger.info(
            f"Received task update: user={user_id}, "
            f"action={action}, task_id={task_id}"
        )

        # TODO: Forward to WebSocket connections for real-time updates
        # TODO: Store for offline sync if user not connected

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing task update event: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/dapr/subscribe")
async def dapr_subscribe() -> list[dict[str, Any]]:
    """
    Dapr subscription configuration endpoint.

    Dapr calls this endpoint to discover which topics this service
    subscribes to. This is an alternative to declarative subscriptions.

    Returns:
        List of subscription configurations
    """
    return [
        {
            "pubsubname": "taskpubsub",
            "topic": "task-events",
            "route": "/events/tasks"
        },
        {
            "pubsubname": "taskpubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        },
        {
            "pubsubname": "taskpubsub",
            "topic": "task-updates",
            "route": "/events/task-updates"
        }
    ]
