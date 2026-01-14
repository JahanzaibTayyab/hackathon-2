"""Unit tests for TaskService."""

import pytest

from src.models.task import Task
from src.schemas.task import TaskComplete, TaskCreate, TaskUpdate


class TestTaskServiceCreate:
    """Test TaskService.create_task."""

    def test_create_task_success(self, task_service, user_id):
        """Test creating a task successfully."""
        task_data = TaskCreate(title="New Task", description="Description")
        task = task_service.create_task(task_data)

        assert task.id is not None
        assert task.title == "New Task"
        assert task.description == "Description"
        assert task.user_id == user_id
        assert task.completed is False

    def test_create_task_minimal(self, task_service, user_id):
        """Test creating a task with only title."""
        task_data = TaskCreate(title="Minimal Task")
        task = task_service.create_task(task_data)

        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.user_id == user_id

    def test_create_task_with_priority(self, task_service, user_id):
        """Test creating a task with priority."""
        task_data = TaskCreate(title="High Priority Task", priority="high")
        task = task_service.create_task(task_data)

        assert task.title == "High Priority Task"
        assert task.priority == "high"

    def test_create_task_with_tags(self, task_service, user_id):
        """Test creating a task with tags."""
        task_data = TaskCreate(title="Tagged Task", tags=["work", "urgent"])
        task = task_service.create_task(task_data)

        assert task.title == "Tagged Task"
        assert task.tags == ["work", "urgent"]


class TestTaskServiceGet:
    """Test TaskService.get_task."""

    def test_get_task_success(self, task_service, sample_task):
        """Test getting a task that exists."""
        task = task_service.get_task(sample_task.id)
        assert task is not None
        assert task.id == sample_task.id
        assert task.title == sample_task.title

    def test_get_task_not_found(self, task_service):
        """Test getting a task that doesn't exist."""
        task = task_service.get_task(99999)
        assert task is None

    def test_get_task_user_isolation(self, session, user_id, other_user_id):
        """Test user isolation - can't get other user's task."""
        from src.services.task_service import TaskService

        # Create task for other user
        other_task = Task(
            user_id=other_user_id,
            title="Other User's Task",
            tags=[],
        )
        session.add(other_task)
        session.commit()
        session.refresh(other_task)

        # Try to get it with different user's service
        service = TaskService(session, user_id)
        task = service.get_task(other_task.id)
        assert task is None  # Should not be accessible


class TestTaskServiceList:
    """Test TaskService.list_tasks."""

    def test_list_tasks_all(self, task_service, sample_task):
        """Test listing all tasks."""
        tasks = task_service.list_tasks(status="all")
        assert len(tasks) >= 1
        assert any(t.id == sample_task.id for t in tasks)

    def test_list_tasks_pending(self, task_service):
        """Test filtering by pending status."""
        # Create completed task
        completed_data = TaskCreate(title="Completed Task")
        completed = task_service.create_task(completed_data)
        task_service.toggle_complete(completed.id, TaskComplete(completed=True))

        # Create pending task
        pending_data = TaskCreate(title="Pending Task")
        pending = task_service.create_task(pending_data)

        # List pending
        tasks = task_service.list_tasks(status="pending")
        assert len(tasks) >= 1
        assert any(t.id == pending.id for t in tasks)
        assert not any(t.id == completed.id for t in tasks)

    def test_list_tasks_completed(self, task_service):
        """Test filtering by completed status."""
        # Create completed task
        completed_data = TaskCreate(title="Completed Task")
        completed = task_service.create_task(completed_data)
        task_service.toggle_complete(completed.id, TaskComplete(completed=True))

        # List completed
        tasks = task_service.list_tasks(status="completed")
        assert len(tasks) >= 1
        assert any(t.id == completed.id for t in tasks)

    def test_list_tasks_sort_created_desc(self, task_service):
        """Test sorting by created_at descending."""
        task1 = task_service.create_task(TaskCreate(title="First"))
        import time
        time.sleep(0.01)
        task2 = task_service.create_task(TaskCreate(title="Second"))

        tasks = task_service.list_tasks(sort_by="created_at", order="desc")
        assert tasks[0].id == task2.id  # Most recent first
        assert tasks[-1].id == task1.id

    def test_list_tasks_sort_created_asc(self, task_service):
        """Test sorting by created_at ascending."""
        task1 = task_service.create_task(TaskCreate(title="First"))
        import time
        time.sleep(0.01)
        task2 = task_service.create_task(TaskCreate(title="Second"))

        tasks = task_service.list_tasks(sort_by="created_at", order="asc")
        assert tasks[0].id == task1.id  # Oldest first
        assert tasks[-1].id == task2.id

    def test_list_tasks_sort_title(self, task_service):
        """Test sorting by title."""
        task_service.create_task(TaskCreate(title="Zebra"))
        task_service.create_task(TaskCreate(title="Apple"))

        tasks = task_service.list_tasks(sort_by="title", order="asc")
        assert tasks[0].title == "Apple"
        assert tasks[-1].title == "Zebra"

    def test_list_tasks_filter_by_priority(self, task_service):
        """Test filtering by priority."""
        task_service.create_task(TaskCreate(title="Low Task", priority="low"))
        high_task = task_service.create_task(TaskCreate(title="High Task", priority="high"))

        tasks = task_service.list_tasks(priority="high")
        assert len(tasks) >= 1
        assert any(t.id == high_task.id for t in tasks)
        assert all(t.priority == "high" for t in tasks)

    def test_list_tasks_filter_by_tags(self, task_service):
        """Test filtering by tags."""
        task_service.create_task(TaskCreate(title="Work Task", tags=["work"]))
        personal_task = task_service.create_task(TaskCreate(title="Personal Task", tags=["personal"]))

        tasks = task_service.list_tasks(tags=["personal"])
        assert len(tasks) >= 1
        assert any(t.id == personal_task.id for t in tasks)

    def test_list_tasks_search(self, task_service):
        """Test search functionality."""
        task_service.create_task(TaskCreate(title="Buy groceries"))
        meeting_task = task_service.create_task(TaskCreate(title="Team meeting", description="Discuss project"))

        tasks = task_service.list_tasks(search="meeting")
        assert len(tasks) >= 1
        assert any(t.id == meeting_task.id for t in tasks)

    def test_list_tasks_user_isolation(self, session, user_id, other_user_id):
        """Test user isolation in list."""
        from src.services.task_service import TaskService

        # Create tasks for both users
        other_service = TaskService(session, other_user_id)
        other_task = other_service.create_task(TaskCreate(title="Other's Task"))

        service = TaskService(session, user_id)
        my_task = service.create_task(TaskCreate(title="My Task"))

        # List should only show my tasks
        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == my_task.id
        assert tasks[0].id != other_task.id


class TestTaskServiceUpdate:
    """Test TaskService.update_task."""

    def test_update_task_success(self, task_service, sample_task):
        """Test updating a task successfully."""
        update_data = TaskUpdate(title="Updated Title", description="Updated Desc")
        updated = task_service.update_task(sample_task.id, update_data)

        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == "Updated Desc"
        assert updated.updated_at >= sample_task.updated_at

    def test_update_task_partial(self, task_service, sample_task):
        """Test partial update (only title)."""
        update_data = TaskUpdate(title="New Title")
        updated = task_service.update_task(sample_task.id, update_data)

        assert updated.title == "New Title"
        assert updated.description == sample_task.description  # Unchanged

    def test_update_task_priority(self, task_service, sample_task):
        """Test updating task priority."""
        update_data = TaskUpdate(priority="urgent")
        updated = task_service.update_task(sample_task.id, update_data)

        assert updated.priority == "urgent"

    def test_update_task_tags(self, task_service, sample_task):
        """Test updating task tags."""
        update_data = TaskUpdate(tags=["work", "important"])
        updated = task_service.update_task(sample_task.id, update_data)

        assert updated.tags == ["work", "important"]

    def test_update_task_not_found(self, task_service):
        """Test updating non-existent task."""
        update_data = TaskUpdate(title="New Title")
        result = task_service.update_task(99999, update_data)
        assert result is None

    def test_update_task_user_isolation(self, session, user_id, other_user_id, sample_task):
        """Test user isolation in update."""
        from src.services.task_service import TaskService

        other_service = TaskService(session, other_user_id)
        result = other_service.update_task(sample_task.id, TaskUpdate(title="Hacked"))
        assert result is None  # Should not be able to update


class TestTaskServiceToggleComplete:
    """Test TaskService.toggle_complete."""

    def test_toggle_complete_success(self, task_service, sample_task):
        """Test toggling completion status."""
        assert sample_task.completed is False

        # toggle_complete returns (task, next_recurring_task)
        task, next_task = task_service.toggle_complete(sample_task.id, TaskComplete(completed=True))
        assert task.completed is True
        assert next_task is None  # No recurrence pattern

        task, _ = task_service.toggle_complete(sample_task.id, TaskComplete(completed=False))
        assert task.completed is False

    def test_toggle_complete_default(self, task_service, sample_task):
        """Test toggle without explicit value."""
        assert sample_task.completed is False

        # toggle_complete returns (task, next_recurring_task)
        task, _ = task_service.toggle_complete(sample_task.id, TaskComplete())
        assert task.completed is True  # Should toggle

    def test_toggle_complete_not_found(self, task_service):
        """Test toggling non-existent task."""
        result = task_service.toggle_complete(99999, TaskComplete(completed=True))
        assert result == (None, None)


class TestTaskServiceDelete:
    """Test TaskService.delete_task."""

    def test_delete_task_success(self, task_service, sample_task):
        """Test deleting a task."""
        task_id = sample_task.id
        result = task_service.delete_task(task_id)
        assert result is True

        # Verify deleted
        task = task_service.get_task(task_id)
        assert task is None

    def test_delete_task_not_found(self, task_service):
        """Test deleting non-existent task."""
        result = task_service.delete_task(99999)
        assert result is False

    def test_delete_task_user_isolation(self, session, user_id, other_user_id, sample_task):
        """Test user isolation in delete."""
        from src.services.task_service import TaskService

        other_service = TaskService(session, other_user_id)
        result = other_service.delete_task(sample_task.id)
        assert result is False  # Should not be able to delete

        # Verify still exists
        service = TaskService(session, user_id)
        task = service.get_task(sample_task.id)
        assert task is not None


class TestTaskServiceGetAllTags:
    """Test TaskService.get_all_tags."""

    def test_get_all_tags_empty(self, task_service):
        """Test getting tags when no tasks have tags."""
        tags = task_service.get_all_tags()
        assert tags == []

    def test_get_all_tags_success(self, task_service):
        """Test getting all unique tags."""
        task_service.create_task(TaskCreate(title="Task 1", tags=["work", "urgent"]))
        task_service.create_task(TaskCreate(title="Task 2", tags=["personal", "work"]))

        tags = task_service.get_all_tags()
        assert "work" in tags
        assert "urgent" in tags
        assert "personal" in tags
