"""Command handlers for todo operations."""

from typing import List, Optional
from todo_hackathon.storage import TodoStorage
from todo_hackathon.models import Todo
from todo_hackathon.exceptions import TodoNotFoundError, TodoValidationError


class TodoCommands:
    """Command handlers for todo operations."""
    
    def __init__(self, storage: TodoStorage):
        """Initialize with storage instance."""
        self.storage = storage
    
    def add(self, title: str, description: Optional[str] = None) -> str:
        """
        Create a new todo.
        
        Args:
            title: The todo title
            description: Optional description
            
        Returns:
            Success message
        """
        try:
            todo = self.storage.create(title, description)
            return f"Todo created: #{todo.id} - {todo.title}"
        except TodoValidationError as e:
            return f"Error: {e}"
    
    def list_todos(self) -> str:
        """
        List all todos.
        
        Returns:
            Formatted list of todos or empty message
        """
        todos = self.storage.get_all()
        
        if not todos:
            return "No todos yet. Create one with 'add <title>'"
        
        lines = []
        for todo in todos:
            status = "[x]" if todo.completed else "[ ]"
            desc = f" ({todo.description})" if todo.description else ""
            lines.append(f"{todo.id}. {status} {todo.title}{desc}")
        
        return "\n".join(lines)
    
    def view(self, todo_id: int) -> str:
        """
        View a single todo.
        
        Args:
            todo_id: The todo ID
            
        Returns:
            Formatted todo details or error message
        """
        todo = self.storage.get(todo_id)
        if not todo:
            return f"Error: Todo #{todo_id} not found"
        
        status = "Completed" if todo.completed else "Incomplete"
        desc = todo.description if todo.description else "(no description)"
        
        return f"""Todo #{todo.id}
Title: {todo.title}
Description: {desc}
Status: {status}
Created: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Updated: {todo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def complete(self, todo_id: int) -> str:
        """
        Mark a todo as completed.
        
        Args:
            todo_id: The todo ID
            
        Returns:
            Success or error message
        """
        try:
            self.storage.update(todo_id, completed=True)
            return f"Todo #{todo_id} marked as completed"
        except TodoNotFoundError:
            return f"Error: Todo #{todo_id} not found"
    
    def incomplete(self, todo_id: int) -> str:
        """
        Mark a todo as incomplete.
        
        Args:
            todo_id: The todo ID
            
        Returns:
            Success or error message
        """
        try:
            self.storage.update(todo_id, completed=False)
            return f"Todo #{todo_id} marked as incomplete"
        except TodoNotFoundError:
            return f"Error: Todo #{todo_id} not found"
    
    def update(self, todo_id: int, field: str, value: str) -> str:
        """
        Update a todo field.
        
        Args:
            todo_id: The todo ID
            field: Field to update (title or description)
            value: New value
            
        Returns:
            Success or error message
        """
        try:
            if field == "title":
                self.storage.update(todo_id, title=value)
            elif field == "description":
                self.storage.update(todo_id, description=value)
            else:
                return f"Error: Unknown field '{field}'. Use 'title' or 'description'"
            
            return f"Todo #{todo_id} updated"
        except TodoNotFoundError:
            return f"Error: Todo #{todo_id} not found"
        except TodoValidationError as e:
            return f"Error: {e}"
    
    def delete(self, todo_id: int) -> str:
        """
        Delete a todo.
        
        Args:
            todo_id: The todo ID
            
        Returns:
            Success or error message
        """
        if self.storage.delete(todo_id):
            return f"Todo #{todo_id} deleted"
        else:
            return f"Error: Todo #{todo_id} not found"
    
    def help(self) -> str:
        """
        Show help message.
        
        Returns:
            Help text
        """
        return """Available commands:
  add <title> [description]  - Create a new todo
  list                       - List all todos
  view <id>                  - View a single todo
  complete <id>              - Mark todo as completed
  incomplete <id>            - Mark todo as incomplete
  update <id> <field> <value> - Update todo field (title/description)
  delete <id>                 - Delete a todo
  help                       - Show this help message
  exit                       - Exit the application"""

