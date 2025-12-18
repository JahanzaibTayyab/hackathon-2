# Data Model: Phase 1 - In-Memory Python Console Todo App

**Date**: 2025-01-27  
**Feature**: Phase 1 Console Todo App

## Entities

### Todo

Represents a single task item that users can create, update, and delete.

**Fields**:
- `id` (int): Unique identifier for the todo. Auto-generated, sequential starting from 1.
- `title` (str): The main description of the task. Required, cannot be empty.
- `description` (str, optional): Additional details about the task. Optional, can be empty string or None.
- `completed` (bool): Whether the task is completed. Default: False.
- `created_at` (datetime): Timestamp when the todo was created. Auto-set on creation.
- `updated_at` (datetime): Timestamp when the todo was last modified. Auto-updated on any change.

**Validation Rules**:
- `title` must not be empty or None
- `title` should be a non-empty string after stripping whitespace
- `id` must be unique within the system
- `created_at` must be set on creation and never changed
- `updated_at` must be updated whenever any field changes

**State Transitions**:
- **Creation**: New todo starts with `completed=False`, `created_at=now()`, `updated_at=now()`
- **Completion**: `completed` can toggle between `True` and `False`, `updated_at` changes
- **Update**: Any field update changes `updated_at` but not `created_at`
- **Deletion**: Todo is removed from storage (no soft delete in Phase 1)

**Relationships**:
- None in Phase 1 (standalone entity)

## Storage Model

### In-Memory Storage Structure

**Type**: Python dictionary

**Structure**: `Dict[int, Todo]`
- Key: Todo ID (int)
- Value: Todo instance

**Operations**:
- `create(todo: Todo) -> Todo`: Add todo to dictionary, return created todo
- `get(id: int) -> Todo | None`: Retrieve todo by ID
- `get_all() -> List[Todo]`: Retrieve all todos as list
- `update(id: int, **kwargs) -> Todo | None`: Update todo fields, return updated todo
- `delete(id: int) -> bool`: Remove todo, return True if found and deleted

**ID Generation**:
- Sequential integers starting from 1
- Track highest ID used
- Increment on each creation
- No reuse of deleted IDs in Phase 1

## Data Flow

```
User Input (CLI)
    ↓
Command Parser
    ↓
Command Handler
    ↓
Storage Layer (Dict[int, Todo])
    ↓
Todo Model (dataclass)
```

## Example Data

```python
# Todo instance
Todo(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False,
    created_at=datetime(2025, 1, 27, 10, 30, 0),
    updated_at=datetime(2025, 1, 27, 10, 30, 0)
)

# Storage representation
{
    1: Todo(id=1, title="Buy groceries", ...),
    2: Todo(id=2, title="Complete project", ...),
    3: Todo(id=3, title="Call dentist", completed=True, ...)
}
```

## Future Considerations (Out of Scope for Phase 1)

- Categories/Tags: Would require additional entity and relationship
- Due dates: Would add datetime field to Todo
- Priorities: Would add priority enum/field
- User assignment: Would require User entity and relationship
- Soft delete: Would add `deleted_at` field and filter logic

