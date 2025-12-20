"""Task service layer for business logic."""

from sqlmodel import Session, col, select

from src.models.task import Task
from src.schemas.task import TaskComplete, TaskCreate, TaskUpdate


class TaskService:
    """Service for task-related operations."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize task service.
        
        Args:
            session: Database session
            user_id: Current authenticated user ID
        """
        self.session = session
        self.user_id = user_id

    def create_task(self, task_data: TaskCreate) -> Task:
        """
        Create a new task.
        
        Args:
            task_data: Task creation data
            
        Returns:
            Created task
        """
        task = Task(
            user_id=self.user_id,
            title=task_data.title,
            description=task_data.description,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_task(self, task_id: int) -> Task | None:
        """
        Get task by ID for current user.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task if found and belongs to user, None otherwise
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == self.user_id,
        )
        return self.session.exec(statement).first()

    def list_tasks(
        self,
        status: str = "all",
        sort: str = "created",
        order: str = "desc",
    ) -> list[Task]:
        """
        List all tasks for current user with filters.
        
        Args:
            status: Filter by status ("all", "pending", "completed")
            sort: Sort field ("created", "title", "updated")
            order: Sort order ("asc", "desc")
            
        Returns:
            List of tasks
        """
        statement = select(Task).where(Task.user_id == self.user_id)

        # Apply status filter
        if status == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712

        # Apply sorting
        sort_column = {
            "created": Task.created_at,
            "title": col(Task.title).collate("NOCASE"),
            "updated": Task.updated_at,
        }.get(sort, Task.created_at)

        if order == "desc":
            statement = statement.order_by(sort_column.desc())
        else:
            statement = statement.order_by(sort_column.asc())

        return list(self.session.exec(statement).all())

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Task | None:
        """
        Update task by ID for current user.
        
        Args:
            task_id: Task ID
            task_data: Task update data
            
        Returns:
            Updated task if found and belongs to user, None otherwise
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        # Update fields if provided
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description

        task.mark_updated()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def toggle_complete(self, task_id: int, task_data: TaskComplete) -> Task | None:
        """
        Toggle task completion status.
        
        Args:
            task_id: Task ID
            task_data: Completion data (optional completed value)
            
        Returns:
            Updated task if found and belongs to user, None otherwise
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        # Toggle or set completed status
        if task_data.completed is not None:
            task.completed = task_data.completed
        else:
            task.completed = not task.completed

        task.mark_updated()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Delete task by ID for current user.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False if not found or doesn't belong to user
        """
        task = self.get_task(task_id)
        if task is None:
            return False

        self.session.delete(task)
        self.session.commit()
        return True
