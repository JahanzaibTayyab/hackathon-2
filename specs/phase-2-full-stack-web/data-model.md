# Data Model: Phase 2 - Todo Full-Stack Web Application

**Date**: 2025-01-27  
**Feature**: Phase 2 Full-Stack Web Application

## Database: Neon Serverless PostgreSQL

### Users Table

Managed by Better Auth (frontend library). Backend receives user information via JWT token payload.

**Note**: Better Auth creates and manages the users table. Backend only needs to verify JWT tokens and extract user_id from the token payload.

**Expected Structure** (for reference):

- `id` (UUID or integer): Unique identifier for the user
- `email` (string): User's email address (unique, required)
- `name` (string, optional): User's display name
- `password_hash` (string): Hashed password (managed by Better Auth)
- `created_at` (timestamp): Account creation timestamp

### Tasks Table

**Table Name**: `tasks`

**Fields**:

- `id` (integer, primary key, auto-increment): Unique identifier for the task
- `user_id` (UUID or integer, foreign key → users.id): Owner of the task
- `title` (varchar(200), not null): The main description of the task. Required, 1-200 characters.
- `description` (text, nullable): Additional details about the task. Optional, max 1000 characters.
- `completed` (boolean, default false): Whether the task is completed. Default: False.
- `created_at` (timestamp, not null, default now()): Timestamp when the task was created. Auto-set on creation.
- `updated_at` (timestamp, not null, default now()): Timestamp when the task was last modified. Auto-updated on any change.

**Indexes**:

- Primary key on `id`
- Index on `user_id` (for filtering tasks by user)
- Index on `completed` (for filtering by status)
- Index on `created_at` (for sorting)
- Composite index on `(user_id, completed)` (for efficient user + status filtering)

**Constraints**:

- `user_id` foreign key constraint to `users.id` (with CASCADE on delete)
- `title` must not be empty (application-level validation, database CHECK constraint optional)
- `title` length between 1-200 characters (application-level validation)
- `description` max 1000 characters (application-level validation)

**Validation Rules**:

- `title` must not be empty or None
- `title` must be between 1-200 characters after trimming whitespace
- `description` is optional but if provided, must be max 1000 characters
- `user_id` must reference an existing user
- `id` must be unique within the system
- `created_at` must be set on creation and never changed
- `updated_at` must be updated whenever any field changes

**State Transitions**:

- **Creation**: New task starts with `completed=False`, `created_at=now()`, `updated_at=now()`
- **Completion Toggle**: `completed` can toggle between `True` and `False`, `updated_at` changes
- **Update**: Any field update changes `updated_at` but not `created_at`
- **Deletion**: Task is permanently deleted from database (hard delete)

**Relationships**:

- **belongs_to User**: Each task belongs to exactly one user
- **User has_many Tasks**: Each user can have many tasks

## SQLModel Models

### Task Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, index=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Pydantic Schemas

**TaskCreate** (for POST /api/v1/tasks):

```python
class TaskCreate(SQLModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
```

**TaskUpdate** (for PUT /api/v1/tasks/{id}):

```python
class TaskUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
```

**TaskResponse** (for all GET responses):

```python
class TaskResponse(SQLModel):
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

**TaskComplete** (for PATCH /api/v1/tasks/{id}/complete):

```python
class TaskComplete(SQLModel):
    completed: Optional[bool] = None  # If None, toggle current status
```

## Data Flow

```
Frontend (Next.js)
    ↓ (JWT token in Authorization header)
Backend API (FastAPI)
    ↓ (JWT verification, extract user_id)
Service Layer
    ↓ (Filter by user_id)
Database Layer (SQLModel)
    ↓
Neon PostgreSQL
    ↓
Tasks Table
```

## User Isolation

**Critical Security Requirement**: All database queries MUST filter by `user_id` extracted from JWT token.

**Example Query Pattern**:

```python
# CORRECT: Filter by user_id
tasks = session.query(Task).filter(Task.user_id == current_user_id).all()

# WRONG: No user filter (security vulnerability)
tasks = session.query(Task).all()  # ❌ Never do this
```

## Example Data

```python
# Task instance
Task(
    id=1,
    user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False,
    created_at=datetime(2025, 1, 27, 10, 30, 0),
    updated_at=datetime(2025, 1, 27, 10, 30, 0)
)

# Database representation
{
    "id": 1,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-01-27T10:30:00Z",
    "updated_at": "2025-01-27T10:30:00Z"
}
```

## Migration Strategy

1. Create `tasks` table with all fields and indexes
2. Add foreign key constraint to `users.id`
3. Set up auto-update trigger for `updated_at` (or handle in application code)
4. Create indexes for performance optimization

## Future Considerations (Out of Scope for Phase 2)

- Categories/Tags: Would require additional `task_categories` and `task_tags` tables
- Due dates: Would add `due_date` datetime field to Task
- Priorities: Would add `priority` enum/field to Task
- Task sharing: Would require `task_shares` junction table
- Soft delete: Would add `deleted_at` field and filter logic
- Task comments: Would require `task_comments` table
- Task attachments: Would require `task_attachments` table
- Recurring tasks: Would add `recurrence_pattern` field
