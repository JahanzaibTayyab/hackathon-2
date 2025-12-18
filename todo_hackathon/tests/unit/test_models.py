"""Unit tests for Todo model."""

import pytest
from datetime import datetime
from todo_hackathon.models import Todo
from todo_hackathon.exceptions import TodoValidationError


class TestTodo:
    """Test Todo model."""
    
    def test_create_todo_with_required_fields(self):
        """Test creating a todo with only required fields."""
        todo = Todo(
            id=1,
            title="Buy groceries"
        )
        
        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description is None
        assert todo.completed is False
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)
    
    def test_create_todo_with_all_fields(self):
        """Test creating a todo with all fields."""
        todo = Todo(
            id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=True,
            created_at=datetime(2025, 1, 27, 10, 0, 0),
            updated_at=datetime(2025, 1, 27, 11, 0, 0)
        )
        
        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description == "Milk, eggs, bread"
        assert todo.completed is True
        assert todo.created_at == datetime(2025, 1, 27, 10, 0, 0)
        assert todo.updated_at == datetime(2025, 1, 27, 11, 0, 0)
    
    def test_create_todo_with_empty_title_raises_error(self):
        """Test that creating a todo with empty title raises error."""
        with pytest.raises(ValueError, match="Todo title cannot be empty"):
            Todo(id=1, title="")
    
    def test_create_todo_with_whitespace_title_raises_error(self):
        """Test that creating a todo with whitespace-only title raises error."""
        with pytest.raises(ValueError, match="Todo title cannot be empty"):
            Todo(id=1, title="   ")
    
    def test_todo_updated_at_not_before_created_at(self):
        """Test that updated_at is adjusted if it's before created_at."""
        created = datetime(2025, 1, 27, 10, 0, 0)
        updated = datetime(2025, 1, 27, 9, 0, 0)  # Before created_at
        
        todo = Todo(
            id=1,
            title="Test",
            created_at=created,
            updated_at=updated
        )
        
        # updated_at should be set to created_at
        assert todo.updated_at == created

