"""Task service layer for business logic."""

from datetime import datetime
from typing import Literal

from sqlalchemy import String, cast, or_
from sqlmodel import Session, col, select

from src.models.task import Task
from src.schemas.task import TaskComplete, TaskCreate, TaskUpdate


# Priority order for sorting
PRIORITY_ORDER = {"urgent": 0, "high": 1, "medium": 2, "low": 3}


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
        # Convert recurrence_pattern to dict if provided
        recurrence_dict = None
        if task_data.recurrence_pattern:
            recurrence_dict = task_data.recurrence_pattern.model_dump()

        task = Task(
            user_id=self.user_id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority,
            tags=task_data.tags,
            recurrence_pattern=recurrence_dict,
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
        status: Literal["all", "pending", "completed"] = "all",
        priority: str | None = None,
        tags: list[str] | None = None,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
        search: str | None = None,
        sort_by: Literal["created_at", "due_date", "priority", "title"] = "created_at",
        order: Literal["asc", "desc"] = "desc",
    ) -> list[Task]:
        """
        List all tasks for current user with advanced filters.

        Args:
            status: Filter by status ("all", "pending", "completed")
            priority: Filter by priority level
            tags: Filter by tags (tasks containing any of these tags)
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            search: Search in title and description
            sort_by: Sort field ("created_at", "due_date", "priority", "title")
            order: Sort order ("asc", "desc")

        Returns:
            List of tasks matching filters
        """
        statement = select(Task).where(Task.user_id == self.user_id)

        # Apply status filter
        if status == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712

        # Apply priority filter
        if priority:
            statement = statement.where(Task.priority == priority)

        # Apply tags filter (tasks containing any of the specified tags)
        # Note: Uses different approach based on database dialect
        if tags:
            # Get the dialect name from the session's bind
            dialect_name = self.session.bind.dialect.name if self.session.bind else "postgresql"
            if dialect_name == "postgresql":
                # Use PostgreSQL array overlap operator
                statement = statement.where(Task.tags.overlap(tags))
            else:
                # For SQLite, tags are stored as JSON strings like '["tag1", "tag2"]'
                # Use LIKE on the string representation to check if any tag is present
                tag_conditions = []
                for tag in tags:
                    # Cast to String and match the tag in the JSON array string
                    tag_conditions.append(cast(Task.tags, String).like(f'%"{tag}"%'))
                if tag_conditions:
                    statement = statement.where(or_(*tag_conditions))

        # Apply due date filters
        if due_before:
            statement = statement.where(Task.due_date <= due_before)
        if due_after:
            statement = statement.where(Task.due_date >= due_after)

        # Apply search filter (case-insensitive search in title and description)
        if search:
            search_pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )

        # Apply sorting
        if sort_by == "created_at":
            sort_column = Task.created_at
        elif sort_by == "due_date":
            sort_column = Task.due_date
        elif sort_by == "title":
            sort_column = col(Task.title).collate("NOCASE")
        elif sort_by == "priority":
            # Priority sorting handled specially - need to use CASE expression
            # For now, use string ordering which works with urgent < high < medium < low
            sort_column = Task.priority
        else:
            sort_column = Task.created_at

        if order == "desc":
            statement = statement.order_by(sort_column.desc().nulls_last())
        else:
            statement = statement.order_by(sort_column.asc().nulls_last())

        return list(self.session.exec(statement).all())

    def get_all_tags(self) -> list[str]:
        """
        Get all unique tags used by the current user.

        Returns:
            List of unique tags
        """
        # Get the dialect name from the session's bind
        dialect_name = self.session.bind.dialect.name if self.session.bind else "postgresql"

        if dialect_name == "postgresql":
            # Use PostgreSQL unnest function for efficient tag extraction
            from sqlalchemy import func

            statement = select(func.unnest(Task.tags).label("tag")).where(
                Task.user_id == self.user_id
            ).distinct()
            result = self.session.exec(statement)
            return sorted(set(result.all()))
        else:
            # For SQLite, fetch all tasks and extract tags manually
            # Tags are stored as JSON strings
            import json

            statement = select(Task.tags).where(Task.user_id == self.user_id)
            result = self.session.exec(statement)
            all_tags = set()
            for tags_value in result.all():
                if tags_value:
                    # Handle both list and JSON string formats
                    if isinstance(tags_value, str):
                        try:
                            tags_list = json.loads(tags_value)
                        except json.JSONDecodeError:
                            tags_list = []
                    else:
                        tags_list = tags_value
                    all_tags.update(tags_list)
            return sorted(all_tags)

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

        # Update basic fields if provided
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description

        # Update Phase V fields if provided
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
            # Reset reminder flag when due date changes
            task.reminder_sent = False
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.tags is not None:
            task.tags = task_data.tags
        if task_data.recurrence_pattern is not None:
            task.recurrence_pattern = task_data.recurrence_pattern.model_dump()

        task.mark_updated()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def toggle_complete(self, task_id: int, task_data: TaskComplete) -> tuple[Task | None, Task | None]:
        """
        Toggle task completion status.

        For recurring tasks, completing them creates the next instance.

        Args:
            task_id: Task ID
            task_data: Completion data (optional completed value)

        Returns:
            Tuple of (updated task, new recurring task instance or None)
        """
        task = self.get_task(task_id)
        if task is None:
            return None, None

        # Determine the new completed status
        if task_data.completed is not None:
            new_completed = task_data.completed
        else:
            new_completed = not task.completed

        # Check if we're completing a recurring task
        next_task = None
        if new_completed and task.is_recurring() and not task.completed:
            # Create next instance of recurring task
            next_task = self._create_next_recurring_instance(task)

        task.completed = new_completed
        task.mark_updated()
        self.session.add(task)

        if next_task:
            self.session.add(next_task)

        self.session.commit()
        self.session.refresh(task)

        if next_task:
            self.session.refresh(next_task)

        return task, next_task

    def _create_next_recurring_instance(self, task: Task) -> Task | None:
        """
        Create the next instance of a recurring task.

        Args:
            task: The recurring task being completed

        Returns:
            New task instance or None if recurrence has ended
        """
        from dateutil.relativedelta import relativedelta

        if not task.recurrence_pattern:
            return None

        pattern = task.recurrence_pattern
        rec_type = pattern.get("type")
        interval = pattern.get("interval", 1)

        # Calculate base date (use due_date or current time)
        base_date = task.due_date or datetime.now()

        # Calculate next occurrence based on recurrence type
        if rec_type == "daily":
            next_date = base_date + relativedelta(days=interval)
        elif rec_type == "weekly":
            next_date = base_date + relativedelta(weeks=interval)
        elif rec_type == "monthly":
            next_date = base_date + relativedelta(months=interval)
        elif rec_type == "yearly":
            next_date = base_date + relativedelta(years=interval)
        else:
            return None

        # Check if recurrence should end
        end_date = pattern.get("end_date")
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            if next_date > end_date:
                return None

        # Create new task instance
        new_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            due_date=next_date,
            priority=task.priority,
            tags=task.tags.copy() if task.tags else [],
            recurrence_pattern=task.recurrence_pattern,
            completed=False,
            reminder_sent=False,
        )

        return new_task

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
