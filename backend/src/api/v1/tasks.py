"""Task API endpoints."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from src.core.database import SessionDep
from src.core.dependencies import CurrentUserDep
from src.schemas.task import (
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
        task_data: Task creation data
        session: Database session
        user_id: Current authenticated user ID
        
    Returns:
        Created task
    """
    service = TaskService(session, user_id)
    task = service.create_task(task_data)
    return TaskResponse.model_validate(task)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,
    status: Literal["all", "pending", "completed"] = Query("all"),
    sort: Literal["created", "title", "updated"] = Query("created"),
    order: Literal["asc", "desc"] = Query("desc"),
) -> TaskListResponse:
    """
    List all tasks for authenticated user.
    
    Args:
        session: Database session
        user_id: Current authenticated user ID
        status: Filter by status (all, pending, completed)
        sort: Sort field (created, title, updated)
        order: Sort order (asc, desc)
        
    Returns:
        List of tasks with total count
    """
    service = TaskService(session, user_id)
    tasks = service.list_tasks(status=status, sort=sort, order=order)
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
    )


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
    return TaskResponse.model_validate(task)


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
        task_data: Task update data
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
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    task_id: int,
    task_data: TaskComplete = TaskComplete(),
    session: SessionDep = ...,
    user_id: CurrentUserDep = ...,
) -> TaskResponse:
    """
    Toggle task completion status.
    
    Args:
        task_id: Task ID
        task_data: Completion data (optional)
        session: Database session
        user_id: Current authenticated user ID
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: If task not found or doesn't belong to user
    """
    service = TaskService(session, user_id)
    task = service.toggle_complete(task_id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


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
