"""In-memory storage for todos."""

from typing import Dict, List, Optional
from datetime import datetime

from .models import Todo
from .exceptions import TodoNotFoundError, TodoValidationError


class TodoStorage:
    """In-memory storage for todo items."""
    
    def __init__(self):
        """Initialize empty storage."""
        self._todos: Dict[int, Todo] = {}
        self._next_id: int = 1
    
    def create(self, title: str, description: Optional[str] = None) -> Todo:
        """
        Create a new todo.
        
        Args:
            title: The todo title (required, cannot be empty)
            description: Optional description
            
        Returns:
            The created Todo instance
            
        Raises:
            TodoValidationError: If title is empty
        """
        if not title or not title.strip():
            raise TodoValidationError("Todo title cannot be empty")
        
        todo = Todo(
            id=self._next_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._todos[self._next_id] = todo
        self._next_id += 1
        
        return todo
    
    def get(self, todo_id: int) -> Optional[Todo]:
        """
        Get a todo by ID.
        
        Args:
            todo_id: The todo ID
            
        Returns:
            The Todo instance if found, None otherwise
        """
        return self._todos.get(todo_id)
    
    def get_all(self) -> List[Todo]:
        """
        Get all todos.
        
        Returns:
            List of all Todo instances
        """
        return list(self._todos.values())
    
    def update(self, todo_id: int, **kwargs) -> Optional[Todo]:
        """
        Update a todo.
        
        Args:
            todo_id: The todo ID
            **kwargs: Fields to update (title, description, completed)
            
        Returns:
            The updated Todo instance if found, None otherwise
            
        Raises:
            TodoNotFoundError: If todo is not found
            TodoValidationError: If validation fails
        """
        todo = self.get(todo_id)
        if not todo:
            raise TodoNotFoundError(f"Todo #{todo_id} not found")
        
        # Update fields
        if 'title' in kwargs:
            new_title = kwargs['title']
            if not new_title or not new_title.strip():
                raise TodoValidationError("Todo title cannot be empty")
            todo.title = new_title.strip()
        
        if 'description' in kwargs:
            desc = kwargs['description']
            todo.description = desc.strip() if desc else None
        
        if 'completed' in kwargs:
            todo.completed = bool(kwargs['completed'])
        
        # Update timestamp
        todo.updated_at = datetime.now()
        
        return todo
    
    def delete(self, todo_id: int) -> bool:
        """
        Delete a todo.
        
        Args:
            todo_id: The todo ID
            
        Returns:
            True if todo was found and deleted, False otherwise
        """
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False

