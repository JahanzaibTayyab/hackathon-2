"""MCP server with task management tools."""

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from src.core.database import engine
from src.schemas.task import TaskComplete, TaskCreate, TaskUpdate
from src.services.task_service import TaskService

# Initialize FastMCP server
mcp_server = FastMCP("Todo Task Manager")


@mcp_server.tool()
def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        title: Task title (1-200 chars)
        description: Optional task description (max 1000 chars)

    Returns:
        Dictionary with task_id, status, and title
    """
    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Create task using the service
        task_data = TaskCreate(title=title, description=description or "")
        task = task_service.create_task(task_data=task_data)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
        }


@mcp_server.tool()
def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """
    Retrieve tasks from the user's task list.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        status: Filter by status - "all", "pending", or "completed" (default: "all")

    Returns:
        List of task dictionaries with id, title, and completed status
    """
    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)

        # Get tasks using the service
        tasks = task_service.list_tasks(status=status)

        return [
            {"id": task.id, "title": task.title, "completed": task.completed} for task in tasks
        ]


@mcp_server.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as complete.

    Args:
        user_id: User ID from JWT token (required for user isolation)
        task_id: ID of the task to complete

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

        # Complete the task (toggle completion state)
        task_data = TaskComplete(completed=True)
        updated_task = task_service.toggle_complete(task_id, task_data)
        if updated_task is None:
            return {"error": "Failed to complete task", "task_id": task_id}

        return {
            "task_id": updated_task.id,
            "status": "completed" if updated_task.completed else "incomplete",
            "title": updated_task.title,
        }


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
