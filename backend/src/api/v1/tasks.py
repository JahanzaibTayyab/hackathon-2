"""Task API endpoints."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from src.core.database import SessionDep
from src.core.dependencies import CurrentUserDep
from src.schemas.task import (
    PriorityType,
    TaskComplete,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from src.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: SessionDep,
    user_id: CurrentUserDep,
) -> TaskResponse:
    """
    Create a new task.

    Args:
        task_data: Task creation data (including optional due_date, priority, tags, recurrence)
        session: Database session
        user_id: Current authenticated user ID

    Returns:
        Created task
    """
    service = TaskService(session, user_id)
    task = service.create_task(task_data)
    return TaskResponse.from_task(task)


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
) -> TaskResponse:
    """
    Update task by ID.

    Args:
        task_id: Task ID
        task_data: Task update data (including optional due_date, priority, tags, recurrence)
        session: Database session
        user_id: Current authenticated user ID

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
    return TaskResponse.from_task(task)


class ToggleCompleteResponse(TaskResponse):
    """Response for toggle complete endpoint, includes next recurring task."""

    next_task: TaskResponse | None = None


@router.patch("/{task_id}/complete", response_model=ToggleCompleteResponse)
async def toggle_complete(
    task_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
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

    response = ToggleCompleteResponse.from_task(task)
    if next_task:
        response.next_task = TaskResponse.from_task(next_task)
    return response


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
) -> None:
    """
    Delete task by ID.
    
    Args:
        task_id: Task ID
        session: Database session
        user_id: Current authenticated user ID
        
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
