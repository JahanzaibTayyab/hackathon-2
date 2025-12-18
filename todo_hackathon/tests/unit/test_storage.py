"""Unit tests for TodoStorage."""

import pytest
from todo_hackathon.storage import TodoStorage
from todo_hackathon.exceptions import TodoNotFoundError, TodoValidationError


class TestTodoStorage:
    """Test TodoStorage class."""
    
    def test_create_todo(self):
        """Test creating a todo."""
        storage = TodoStorage()
        todo = storage.create("Buy groceries")
        
        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description is None
        assert todo.completed is False
    
    def test_create_todo_with_description(self):
        """Test creating a todo with description."""
        storage = TodoStorage()
        todo = storage.create("Buy groceries", "Milk, eggs, bread")
        
        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description == "Milk, eggs, bread"
    
    def test_create_todo_with_empty_title_raises_error(self):
        """Test that creating todo with empty title raises error."""
        storage = TodoStorage()
        with pytest.raises(TodoValidationError, match="Todo title cannot be empty"):
            storage.create("")
    
    def test_create_multiple_todos_sequential_ids(self):
        """Test that multiple todos get sequential IDs."""
        storage = TodoStorage()
        todo1 = storage.create("First todo")
        todo2 = storage.create("Second todo")
        todo3 = storage.create("Third todo")
        
        assert todo1.id == 1
        assert todo2.id == 2
        assert todo3.id == 3
    
    def test_get_todo_by_id(self):
        """Test getting a todo by ID."""
        storage = TodoStorage()
        created = storage.create("Buy groceries")
        retrieved = storage.get(1)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == created.title
    
    def test_get_nonexistent_todo_returns_none(self):
        """Test getting a todo that doesn't exist."""
        storage = TodoStorage()
        result = storage.get(999)
        
        assert result is None
    
    def test_get_all_todos_empty_storage(self):
        """Test getting all todos from empty storage."""
        storage = TodoStorage()
        todos = storage.get_all()
        
        assert todos == []
    
    def test_get_all_todos(self):
        """Test getting all todos."""
        storage = TodoStorage()
        todo1 = storage.create("First todo")
        todo2 = storage.create("Second todo")
        todo3 = storage.create("Third todo")
        
        todos = storage.get_all()
        
        assert len(todos) == 3
        assert todos[0].id == 1
        assert todos[1].id == 2
        assert todos[2].id == 3
    
    def test_update_todo_title(self):
        """Test updating a todo's title."""
        storage = TodoStorage()
        storage.create("Buy groceries")
        updated = storage.update(1, title="Buy groceries and cook")
        
        assert updated is not None
        assert updated.title == "Buy groceries and cook"
        assert updated.id == 1
    
    def test_update_todo_description(self):
        """Test updating a todo's description."""
        storage = TodoStorage()
        storage.create("Buy groceries")
        updated = storage.update(1, description="Milk, eggs, bread")
        
        assert updated is not None
        assert updated.description == "Milk, eggs, bread"
    
    def test_update_todo_completed_status(self):
        """Test updating a todo's completed status."""
        storage = TodoStorage()
        storage.create("Buy groceries")
        updated = storage.update(1, completed=True)
        
        assert updated is not None
        assert updated.completed is True
    
    def test_update_nonexistent_todo_raises_error(self):
        """Test updating a todo that doesn't exist."""
        storage = TodoStorage()
        with pytest.raises(TodoNotFoundError, match="Todo #999 not found"):
            storage.update(999, title="New title")
    
    def test_update_todo_with_empty_title_raises_error(self):
        """Test that updating todo with empty title raises error."""
        storage = TodoStorage()
        storage.create("Buy groceries")
        with pytest.raises(TodoValidationError, match="Todo title cannot be empty"):
            storage.update(1, title="")
    
    def test_delete_todo(self):
        """Test deleting a todo."""
        storage = TodoStorage()
        storage.create("Buy groceries")
        result = storage.delete(1)
        
        assert result is True
        assert storage.get(1) is None
    
    def test_delete_nonexistent_todo_returns_false(self):
        """Test deleting a todo that doesn't exist."""
        storage = TodoStorage()
        result = storage.delete(999)
        
        assert result is False

