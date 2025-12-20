"""Unit tests for database models."""

from datetime import UTC, datetime

import pytest

from src.models.task import Task


class TestTaskModel:
    """Test Task model."""

    def test_task_creation(self):
        """Test creating a task with required fields."""
        task = Task(
            user_id="user-123",
            title="My Task",
            description="Task description",
        )
        assert task.user_id == "user-123"
        assert task.title == "My Task"
        assert task.description == "Task description"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_defaults(self):
        """Test task default values."""
        task = Task(user_id="user-123", title="My Task")
        assert task.completed is False
        assert task.description is None
        assert task.id is None  # Not set until saved
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_mark_updated(self):
        """Test mark_updated updates timestamp."""
        task = Task(user_id="user-123", title="My Task")
        original_updated = task.updated_at
        
        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)
        
        task.mark_updated()
        assert task.updated_at > original_updated

    def test_task_title_max_length(self):
        """Test title field accepts up to 200 characters."""
        long_title = "a" * 200
        task = Task(user_id="user-123", title=long_title)
        assert len(task.title) == 200

    def test_task_description_max_length(self):
        """Test description field accepts up to 1000 characters."""
        long_description = "a" * 1000
        task = Task(user_id="user-123", title="Task", description=long_description)
        assert len(task.description) == 1000
