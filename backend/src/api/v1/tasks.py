"""Task API endpoints."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from src.models.task import Task

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from src.core.database import SessionDep
from src.core.dependencies import CurrentUserDep
from src.events.producer import event_producer
from src.schemas.task import (
    PriorityType,
    TaskComplete,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def _publish_event_safe(coro):
    """Safely execute an event publishing coroutine, logging any errors."""
    try:
        await coro
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: SessionDep,
    user_id: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> TaskResponse:
    """
    Create a new task.

    Args:
        task_data: Task creation data (including optional due_date, priority, tags, recurrence)
        session: Database session
        user_id: Current authenticated user ID
        background_tasks: Background task runner

    Returns:
        Created task
    """
    service = TaskService(session, user_id)
    task = service.create_task(task_data)
    response = TaskResponse.from_task(task)

    # Publish event in background
    background_tasks.add_task(
        _publish_event_safe,
        event_producer.publish_task_created(
            task_id=task.id,
            user_id=user_id,
            data=task_data.model_dump(mode="json")
        )
    )

    return response


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,
    task_status: Literal["all", "pending", "completed"] = Query(
        "all", alias="status", description="Filter by completion status"
    ),
    priority: PriorityType | None = Query(
        None, description="Filter by priority level"
    ),
    tags: str | None = Query(
        None, description="Filter by tags (comma-separated)"
    ),
    due_before: datetime | None = Query(
        None, description="Filter tasks due before this date"
    ),
    due_after: datetime | None = Query(
        None, description="Filter tasks due after this date"
    ),
    search: str | None = Query(
        None, min_length=1, max_length=100, description="Search in title and description"
    ),
    sort_by: Literal["created_at", "due_date", "priority", "title"] = Query(
        "created_at", description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
) -> TaskListResponse:
    """
    List all tasks for authenticated user with advanced filtering.

    Args:
        session: Database session
        user_id: Current authenticated user ID
        task_status: Filter by status (all, pending, completed)
        priority: Filter by priority level (low, medium, high, urgent)
        tags: Filter by tags (comma-separated list)
        due_before: Filter tasks due before this date
        due_after: Filter tasks due after this date
        search: Search in title and description
        sort_by: Field to sort by (created_at, due_date, priority, title)
        order: Sort order (asc, desc)

    Returns:
        List of tasks with total count
    """
    service = TaskService(session, user_id)

    # Parse tags from comma-separated string
    tags_list = [t.strip() for t in tags.split(",")] if tags else None

    tasks = service.list_tasks(
        status=task_status,
        priority=priority,
        tags=tags_list,
        due_before=due_before,
        due_after=due_after,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return TaskListResponse(
        tasks=[TaskResponse.from_task(task) for task in tasks],
        total=len(tasks),
    )


@router.get("/tags", response_model=list[str])
async def get_tags(
    session: SessionDep,
    user_id: CurrentUserDep,
) -> list[str]:
    """
    Get all unique tags used by the current user.

    Returns:
        List of unique tag names
    """
    service = TaskService(session, user_id)
    return service.get_all_tags()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
) -> TaskResponse:
    """
    Get task by ID.

    Args:
        task_id: Task ID
        session: Database session
        user_id: Current authenticated user ID

    Returns:
        Task details

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    service = TaskService(session, user_id)
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.from_task(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: SessionDep,
    user_id: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> TaskResponse:
    """
    Update task by ID.

    Args:
        task_id: Task ID
        task_data: Task update data (including optional due_date, priority, tags, recurrence)
        session: Database session
        user_id: Current authenticated user ID
        background_tasks: Background task runner

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    service = TaskService(session, user_id)
    task = service.update_task(task_id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    response = TaskResponse.from_task(task)

    # Publish event in background
    background_tasks.add_task(
        _publish_event_safe,
        event_producer.publish_task_updated(
            task_id=task_id,
            user_id=user_id,
            data=task_data.model_dump(mode="json", exclude_unset=True)
        )
    )

    return response


class ToggleCompleteResponse(TaskResponse):
    """Response for toggle complete endpoint, includes next recurring task."""

    next_task: TaskResponse | None = None

    @classmethod
    def from_task_with_next(
        cls, task: "Task", next_task: "Task | None" = None  # noqa: F821
    ) -> "ToggleCompleteResponse":
        """Create response from task with optional next recurring task."""
        base = TaskResponse.from_task(task)
        return cls(
            **base.model_dump(),
            next_task=TaskResponse.from_task(next_task) if next_task else None
        )


@router.patch("/{task_id}/complete", response_model=ToggleCompleteResponse)
async def toggle_complete(
    task_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
    background_tasks: BackgroundTasks,
    task_data: TaskComplete = TaskComplete(),
) -> ToggleCompleteResponse:
    """
    Toggle task completion status.

    For recurring tasks, completing them will create the next instance.

    Args:
        task_id: Task ID
        task_data: Completion data (optional)
        session: Database session
        user_id: Current authenticated user ID
        background_tasks: Background task runner

    Returns:
        Updated task, with next_task if recurring

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    service = TaskService(session, user_id)
    task, next_task = service.toggle_complete(task_id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    response = ToggleCompleteResponse.from_task_with_next(task, next_task)

    # Publish event in background
    if task.completed:
        background_tasks.add_task(
            _publish_event_safe,
            event_producer.publish_task_completed(task_id=task_id, user_id=user_id)
        )
    else:
        background_tasks.add_task(
            _publish_event_safe,
            event_producer.publish_task_uncompleted(task_id=task_id, user_id=user_id)
        )

    return response


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> None:
    """
    Delete task by ID.

    Args:
        task_id: Task ID
        session: Database session
        user_id: Current authenticated user ID
        background_tasks: Background task runner

    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    service = TaskService(session, user_id)
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Publish event in background
    background_tasks.add_task(
        _publish_event_safe,
        event_producer.publish_task_deleted(task_id=task_id, user_id=user_id)
    )
