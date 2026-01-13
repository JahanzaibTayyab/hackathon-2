# Data Model: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-13
**Feature**: Phase 3 AI-Powered Todo Chatbot

## Database: Neon Serverless PostgreSQL

### New Tables for Phase 3

#### Conversations Table

**Table Name**: `conversations`

**Fields**:

- `id` (integer, primary key, auto-increment): Unique identifier for the conversation
- `user_id` (string, foreign key -> users.id): Owner of the conversation
- `created_at` (timestamp, not null, default now()): Timestamp when the conversation was created
- `updated_at` (timestamp, not null, default now()): Timestamp when the conversation was last modified

**Indexes**:

- Primary key on `id`
- Index on `user_id` (for filtering conversations by user)
- Index on `created_at` (for sorting conversations)

**Constraints**:

- `user_id` must reference an existing user

---

#### Messages Table

**Table Name**: `messages`

**Fields**:

- `id` (integer, primary key, auto-increment): Unique identifier for the message
- `conversation_id` (integer, foreign key -> conversations.id): Parent conversation
- `user_id` (string, foreign key -> users.id): Owner of the message
- `role` (varchar(20), not null): Either "user" or "assistant"
- `content` (text, not null): The message content
- `tool_calls` (jsonb, nullable): Array of tool calls made by the assistant (if any)
- `created_at` (timestamp, not null, default now()): Timestamp when the message was created

**Indexes**:

- Primary key on `id`
- Index on `conversation_id` (for fetching messages by conversation)
- Index on `user_id` (for filtering messages by user)
- Index on `created_at` (for ordering messages)

**Constraints**:

- `conversation_id` must reference an existing conversation
- `user_id` must reference an existing user
- `role` must be either "user" or "assistant"
- `content` must not be empty

---

### Existing Tables (From Phase 2)

#### Tasks Table (Unchanged)

The tasks table remains the same as Phase 2. The MCP tools will interact with this table.

---

## SQLModel Models

### Conversation Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Message Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, List, Any

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str
    tool_calls: Optional[str] = Field(default=None)  # JSON string of tool calls
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Pydantic Schemas

### ChatRequest Schema

```python
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
```

### ChatResponse Schema

```python
from pydantic import BaseModel
from typing import List, Optional, Any

class ToolCall(BaseModel):
    tool_name: str
    arguments: dict
    result: Any

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[ToolCall] = []
```

### ConversationResponse Schema

```python
from pydantic import BaseModel
from datetime import datetime
from typing import List

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

class ConversationResponse(BaseModel):
    id: int
    user_id: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime
```

---

## MCP Tool Schemas

### add_task Tool

**Purpose**: Create a new task

**Parameters**:
- `user_id` (string, required): User ID from JWT token
- `title` (string, required): Task title (1-200 chars)
- `description` (string, optional): Task description (max 1000 chars)

**Returns**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

### list_tasks Tool

**Purpose**: Retrieve tasks from the list

**Parameters**:
- `user_id` (string, required): User ID from JWT token
- `status` (string, optional): "all" | "pending" | "completed" (default: "all")

**Returns**:
```json
[
  {"id": 1, "title": "Buy groceries", "completed": false},
  {"id": 2, "title": "Call mom", "completed": true}
]
```

### complete_task Tool

**Purpose**: Mark a task as complete

**Parameters**:
- `user_id` (string, required): User ID from JWT token
- `task_id` (integer, required): ID of the task to complete

**Returns**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

### delete_task Tool

**Purpose**: Remove a task from the list

**Parameters**:
- `user_id` (string, required): User ID from JWT token
- `task_id` (integer, required): ID of the task to delete

**Returns**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

### update_task Tool

**Purpose**: Modify task title or description

**Parameters**:
- `user_id` (string, required): User ID from JWT token
- `task_id` (integer, required): ID of the task to update
- `title` (string, optional): New task title
- `description` (string, optional): New task description

**Returns**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

---

## Data Flow

```
Frontend (ChatKit UI)
    ↓ (POST /api/v1/chat with JWT token)
Backend Chat Endpoint (FastAPI)
    ↓ (Fetch conversation history from DB)
    ↓ (Build message array for agent)
OpenAI Agents SDK
    ↓ (Agent processes message)
    ↓ (Agent calls MCP tools as needed)
MCP Server (MCP SDK)
    ↓ (Execute tool with user_id)
Task Service (SQLModel)
    ↓ (CRUD operations filtered by user_id)
Neon PostgreSQL (tasks, conversations, messages)
    ↓
Response flows back up the chain
    ↓ (Store assistant message in DB)
    ↓ (Return response to frontend)
```

---

## Stateless Architecture

**Critical Requirement**: The server must be stateless. All conversation state is persisted to the database.

**Request Cycle**:

1. **Receive** user message via POST /api/v1/chat
2. **Fetch** conversation history from database (if conversation_id provided)
3. **Build** message array for agent (history + new message)
4. **Store** user message in database
5. **Run** agent with MCP tools
6. **Agent invokes** appropriate MCP tool(s)
7. **Store** assistant response in database
8. **Return** response to client
9. **Server holds NO state** (ready for next request)

**Benefits**:
- Scalability: Any server instance can handle any request
- Resilience: Server restarts don't lose conversation state
- Horizontal scaling: Load balancer can route to any backend
- Testability: Each request is independent and reproducible

---

## Example Data

### Conversation Instance

```python
Conversation(
    id=1,
    user_id="123e4567-e89b-12d3-a456-426614174000",
    created_at=datetime(2026, 1, 13, 10, 30, 0),
    updated_at=datetime(2026, 1, 13, 11, 45, 0)
)
```

### Message Instance

```python
Message(
    id=1,
    conversation_id=1,
    user_id="123e4567-e89b-12d3-a456-426614174000",
    role="user",
    content="Add a task to buy groceries",
    tool_calls=None,
    created_at=datetime(2026, 1, 13, 10, 30, 0)
)

Message(
    id=2,
    conversation_id=1,
    user_id="123e4567-e89b-12d3-a456-426614174000",
    role="assistant",
    content="I've created a new task 'Buy groceries' for you. Is there anything else you'd like to add?",
    tool_calls='[{"tool": "add_task", "args": {"title": "Buy groceries"}, "result": {"task_id": 5}}]',
    created_at=datetime(2026, 1, 13, 10, 30, 5)
)
```

---

## Migration Strategy

1. Create `conversations` table with all fields and indexes
2. Create `messages` table with all fields and indexes
3. Add foreign key constraints
4. Verify existing `tasks` table is compatible with MCP tools
5. Test conversation persistence across server restarts
