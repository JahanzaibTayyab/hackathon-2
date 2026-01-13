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
    def add_task(title: str, description: str = "") -> dict:
        """
        Create a new task for the user.

        Args:
            title: Task title (required)
            description: Task description (optional)

        Returns:
            Dictionary with task_id, status, and title
        """
        with Session(engine) as session:
            task_service = TaskService(session=session, user_id=user_id)
            task_data = TaskCreate(title=title, description=description)
            task = task_service.create_task(task_data=task_data)

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }

    @function_tool
    def list_tasks(status: str = "all") -> list[dict]:
        """
        Retrieve tasks from the user's task list.

        Args:
            status: Filter by status - "all", "pending", or "completed" (default: "all")

        Returns:
            List of task dictionaries with id, title, and completed status
        """
        with Session(engine) as session:
            task_service = TaskService(session=session, user_id=user_id)
            tasks = task_service.list_tasks(status=status)

            return [
                {"id": task.id, "title": task.title, "completed": task.completed}
                for task in tasks
            ]

    @function_tool
    def complete_task(task_id: int) -> dict:
        """
        Mark a task as complete.

        Args:
            task_id: ID of the task to complete

        Returns:
            Dictionary with task_id, status, and title if successful
            Dictionary with error message if task not found
        """
        with Session(engine) as session:
            task_service = TaskService(session=session, user_id=user_id)

            task = task_service.get_task(task_id)
            if task is None:
                return {"error": "Task not found", "task_id": task_id}

            task_data = TaskComplete(completed=True)
            updated_task = task_service.toggle_complete(task_id, task_data)
            if updated_task is None:
                return {"error": "Failed to complete task", "task_id": task_id}

            return {
                "task_id": updated_task.id,
                "status": "completed" if updated_task.completed else "incomplete",
                "title": updated_task.title,
            }

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
- Create new tasks
- List their tasks (all, pending, or completed)
- Mark tasks as complete
- Delete tasks
- Update task titles or descriptions

When users ask about their tasks or want to manage them, use the appropriate tools.
Be friendly, concise, and helpful. Confirm actions after completing them.

Examples:
- "Add a task to buy groceries" -> Use add_task tool
- "Show me all my tasks" -> Use list_tasks tool
- "Mark task 3 as complete" -> Use complete_task tool
- "Delete task 5" -> Use delete_task tool
- "Update task 2 title to 'Call mom tonight'" -> Use update_task tool""",
        tools=[add_task, list_tasks, complete_task, delete_task, update_task],
    )

    return agent
