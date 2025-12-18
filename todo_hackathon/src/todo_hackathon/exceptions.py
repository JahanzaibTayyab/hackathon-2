"""Custom exceptions for todo-hackathon."""


class TodoError(Exception):
    """Base exception for todo-related errors."""
    pass


class TodoNotFoundError(TodoError):
    """Raised when a todo is not found."""
    pass


class TodoValidationError(TodoError):
    """Raised when todo validation fails."""
    pass

