"""AI agent configuration for task management chatbot."""

from agents import Agent, function_tool
from sqlmodel import Session

from src.core.database import engine
from src.schemas.task import TaskComplete, TaskCreate, TaskUpdate
from src.services.task_service import TaskService


def create_chat_agent(user_id: str) -> Agent:
    """
    Create a chat agent for the given user with task management tools.

    Args:
        user_id: User ID for task isolation

    Returns:
        Configured Agent instance
    """

    # Define tool functions that will be available to the agent
    @function_tool
    def add_task(
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: str | None = None,
        tags: str | None = None,
    ) -> dict:
        """
        Create a new task for the user.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Priority level - "low", "medium", "high", or "urgent" (default: "medium")
            due_date: Due date in ISO format like "2026-01-20" or "2026-01-20T14:00:00" (optional)
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
            task_data = TaskCreate(
                title=title,
                description=description,
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

    @function_tool
    def list_tasks(
        status: str = "all",
        priority: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        """
        Retrieve tasks from the user's task list.

        Args:
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

    @function_tool
    def complete_task(task_id: int) -> dict:
        """
        Mark a task as complete.

        For recurring tasks, completing them will create the next instance.

        Args:
            task_id: ID of the task to complete

        Returns:
            Dictionary with task_id, status, title, and next_task_id (for recurring tasks)
            Dictionary with error message if task not found
        """
        with Session(engine) as session:
            task_service = TaskService(session=session, user_id=user_id)

            task = task_service.get_task(task_id)
            if task is None:
                return {"error": "Task not found", "task_id": task_id}

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

    @function_tool
    def delete_task(task_id: int) -> dict:
        """
        Remove a task from the user's task list.

        Args:
            task_id: ID of the task to delete

        Returns:
            Dictionary with task_id, status, and title if successful
            Dictionary with error message if task not found
        """
        with Session(engine) as session:
            task_service = TaskService(session=session, user_id=user_id)

            task = task_service.get_task(task_id)
            if task is None:
                return {"error": "Task not found", "task_id": task_id}

            task_title = task.title
            success = task_service.delete_task(task_id)
            if not success:
                return {"error": "Failed to delete task", "task_id": task_id}

            return {
                "task_id": task_id,
                "status": "deleted",
                "title": task_title,
            }

    @function_tool
    def update_task(task_id: int, title: str | None = None, description: str | None = None) -> dict:
        """
        Modify task title or description.

        Args:
            task_id: ID of the task to update
            title: New task title (optional)
            description: New task description (optional)

        Returns:
            Dictionary with task_id, status, and title if successful
            Dictionary with error message if task not found
        """
        with Session(engine) as session:
            task_service = TaskService(session=session, user_id=user_id)

            task = task_service.get_task(task_id)
            if task is None:
                return {"error": "Task not found", "task_id": task_id}

            task_data = TaskUpdate(title=title, description=description)
            updated_task = task_service.update_task(task_id=task_id, task_data=task_data)
            if updated_task is None:
                return {"error": "Failed to update task", "task_id": task_id}

            return {
                "task_id": updated_task.id,
                "status": "updated",
                "title": updated_task.title,
            }

    # Create the agent with tools and instructions
    agent = Agent(
        name="Todo Assistant",
        instructions="""You are a helpful todo task management assistant. You can help users:
- Create new tasks with optional due dates, priorities, and tags
- List their tasks with filters (status, priority, search)
- Mark tasks as complete (recurring tasks auto-create next instance)
- Delete tasks
- Update task titles, descriptions, priorities, due dates, or tags

When users ask about their tasks or want to manage them, use the appropriate tools.
Be friendly, concise, and helpful. Confirm actions after completing them.

Priority levels: low, medium, high, urgent
Due dates: Use ISO format like "2026-01-20" or "2026-01-20T14:00:00"
Tags: Comma-separated like "work,urgent"

Examples:
- "Add a task to buy groceries" -> Use add_task tool
- "Add high priority task to submit report by January 20" -> Use add_task with priority="high" and due_date="2026-01-20"
- "Show me all my tasks" -> Use list_tasks tool
- "Show my high priority tasks" -> Use list_tasks with priority="high"
- "Search for tasks about meeting" -> Use list_tasks with search="meeting"
- "Mark task 3 as complete" -> Use complete_task tool
- "Delete task 5" -> Use delete_task tool
- "Update task 2 title to 'Call mom tonight'" -> Use update_task tool""",
        tools=[add_task, list_tasks, complete_task, delete_task, update_task],
    )

    return agent
