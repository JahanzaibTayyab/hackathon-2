"""MCP server with task management tools."""

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from src.core.database import engine
from src.schemas.task import TaskComplete, TaskCreate, TaskUpdate
from src.services.task_service import TaskService

# Initialize FastMCP server
mcp_server = FastMCP("Todo Task Manager")


@mcp_server.tool()
def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str = "medium",
    due_date: str | None = None,
    tags: str | None = None,
) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        title: Task title (1-200 chars)
        description: Optional task description (max 1000 chars)
        priority: Priority level - "low", "medium", "high", or "urgent" (default: "medium")
        due_date: Due date in ISO format like "2026-01-20" (optional)
        tags: Comma-separated tags like "work,urgent" (optional)

    Returns:
        Dictionary with task_id, status, title, priority, and due_date
    """
    from datetime import datetime

    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Parse tags if provided
    parsed_tags = []
    if tags:
        parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]

    # Validate priority
    valid_priorities = ("low", "medium", "high", "urgent")
    if priority not in valid_priorities:
        priority = "medium"

    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Create task using the service
        task_data = TaskCreate(
            title=title,
            description=description or "",
            priority=priority,  # type: ignore[arg-type]
            due_date=parsed_due_date,
            tags=parsed_tags,
        )
        task = task_service.create_task(task_data=task_data)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags or [],
        }


@mcp_server.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,
    search: str | None = None,
) -> list[dict]:
    """
    Retrieve tasks from the user's task list.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        status: Filter by status - "all", "pending", or "completed" (default: "all")
        priority: Filter by priority - "low", "medium", "high", or "urgent" (optional)
        search: Search in title and description (optional)

    Returns:
        List of task dictionaries with id, title, completed, priority, and due_date
    """
    # Validate status
    valid_statuses = ("all", "pending", "completed")
    if status not in valid_statuses:
        status = "all"

    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Get tasks using the service with filters
        tasks = task_service.list_tasks(
            status=status,  # type: ignore[arg-type]
            priority=priority,
            search=search,
        )

        return [
            {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags or [],
            }
            for task in tasks
        ]


@mcp_server.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as complete.

    For recurring tasks, completing them will create the next instance.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        task_id: ID of the task to complete

    Returns:
        Dictionary with task_id, status, title, and next_task_id (for recurring tasks)
        Dictionary with error message if task not found
    """
    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Get the task first to check if it exists
        task = task_service.get_task(task_id)
        if task is None:
            return {"error": "Task not found", "task_id": task_id}

        # Complete the task (toggle completion state)
        task_data = TaskComplete(completed=True)
        updated_task, next_task = task_service.toggle_complete(task_id, task_data)
        if updated_task is None:
            return {"error": "Failed to complete task", "task_id": task_id}

        result = {
            "task_id": updated_task.id,
            "status": "completed" if updated_task.completed else "incomplete",
            "title": updated_task.title,
        }

        # Include info about next recurring task if created
        if next_task:
            result["next_task_id"] = next_task.id
            result["next_due_date"] = (
                next_task.due_date.isoformat() if next_task.due_date else None
            )

        return result


@mcp_server.tool()
def delete_task(user_id: str, task_id: int) -> dict:
    """
    Remove a task from the user's task list.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        task_id: ID of the task to delete

    Returns:
        Dictionary with task_id, status, and title if successful
        Dictionary with error message if task not found
    """
    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Get the task first to get its title before deletion
        task = task_service.get_task(task_id)
        if task is None:
            return {"error": "Task not found", "task_id": task_id}

        task_title = task.title

        # Delete the task
        success = task_service.delete_task(task_id)
        if not success:
            return {"error": "Failed to delete task", "task_id": task_id}

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": task_title,
        }


@mcp_server.tool()
def update_task(
    user_id: str, task_id: int, title: str | None = None, description: str | None = None
) -> dict:
    """
    Modify task title or description.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        Dictionary with task_id, status, and title if successful
        Dictionary with error message if task not found
    """
    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Get the task first to check if it exists
        task = task_service.get_task(task_id)
        if task is None:
            return {"error": "Task not found", "task_id": task_id}

        # Update the task
        task_data = TaskUpdate(title=title, description=description)
        updated_task = task_service.update_task(task_id=task_id, task_data=task_data)
        if updated_task is None:
            return {"error": "Failed to update task", "task_id": task_id}

        return {
            "task_id": updated_task.id,
            "status": "updated",
            "title": updated_task.title,
        }
