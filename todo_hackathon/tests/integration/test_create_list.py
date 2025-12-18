"""Integration tests for create and list workflow."""

from todo_hackathon.storage import TodoStorage


class TestCreateListWorkflow:
    """Test create and list todo workflow."""
    
    def test_create_and_list_single_todo(self):
        """Test creating a todo and listing it."""
        storage = TodoStorage()
        
        # Create todo
        todo = storage.create("Buy groceries")
        
        # List todos
        todos = storage.get_all()
        
        assert len(todos) == 1
        assert todos[0].id == todo.id
        assert todos[0].title == "Buy groceries"
        assert todos[0].completed is False
    
    def test_create_and_list_multiple_todos(self):
        """Test creating multiple todos and listing them."""
        storage = TodoStorage()
        
        # Create multiple todos
        todo1 = storage.create("Buy groceries")
        todo2 = storage.create("Complete project", "Finish the todo app")
        todo3 = storage.create("Call dentist")
        
        # List todos
        todos = storage.get_all()
        
        assert len(todos) == 3
        assert todos[0].id == 1
        assert todos[0].title == "Buy groceries"
        assert todos[1].id == 2
        assert todos[1].title == "Complete project"
        assert todos[1].description == "Finish the todo app"
        assert todos[2].id == 3
        assert todos[2].title == "Call dentist"
    
    def test_list_empty_storage(self):
        """Test listing todos when storage is empty."""
        storage = TodoStorage()
        todos = storage.get_all()
        
        assert len(todos) == 0
        assert todos == []

