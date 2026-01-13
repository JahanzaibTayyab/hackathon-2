# API Contracts: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-13
**Feature**: Phase 3 AI-Powered Todo Chatbot

## Chat API Endpoint

### POST /api/v1/chat

Send a message and get AI response.

**Authentication**: Required (JWT token in Authorization header)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 1  // Optional - creates new conversation if not provided
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's natural language message |
| conversation_id | integer | No | Existing conversation ID (creates new if not provided) |

**Response (200 OK)**:
```json
{
  "conversation_id": 1,
  "response": "I've created a new task 'Buy groceries' for you. Is there anything else you'd like to add?",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {
        "title": "Buy groceries"
      },
      "result": {
        "task_id": 5,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | integer | The conversation ID |
| response | string | AI assistant's response |
| tool_calls | array | List of MCP tools invoked (may be empty) |

**Error Responses**:

- `400 Bad Request`: Missing or invalid message
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: OpenAI API error or server error

---

## Conversation API Endpoints

### GET /api/v1/conversations

List all conversations for the authenticated user.

**Authentication**: Required

**Response (200 OK)**:
```json
{
  "conversations": [
    {
      "id": 1,
      "created_at": "2026-01-13T10:30:00Z",
      "updated_at": "2026-01-13T11:45:00Z",
      "message_count": 10
    },
    {
      "id": 2,
      "created_at": "2026-01-12T09:00:00Z",
      "updated_at": "2026-01-12T09:30:00Z",
      "message_count": 5
    }
  ]
}
```

---

### GET /api/v1/conversations/{id}

Get a specific conversation with all messages.

**Authentication**: Required

**Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T11:45:00Z",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Add a task to buy groceries",
      "created_at": "2026-01-13T10:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "I've created a new task 'Buy groceries' for you.",
      "created_at": "2026-01-13T10:30:05Z"
    }
  ]
}
```

**Error Responses**:

- `404 Not Found`: Conversation not found or belongs to another user

---

### DELETE /api/v1/conversations/{id}

Delete a conversation and all its messages.

**Authentication**: Required

**Response (204 No Content)**: Success

**Error Responses**:

- `404 Not Found`: Conversation not found or belongs to another user

---

## MCP Tools Specification

The MCP server exposes the following tools that the AI agent can invoke.

### Tool: add_task

**Purpose**: Create a new task

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID from JWT token |
| title | string | Yes | Task title (1-200 chars) |
| description | string | No | Task description (max 1000 chars) |

**Example Input**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Example Output**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

---

### Tool: list_tasks

**Purpose**: Retrieve tasks from the list

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID from JWT token |
| status | string | No | "all", "pending", or "completed" (default: "all") |

**Example Input**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending"
}
```

**Example Output**:
```json
[
  {"id": 1, "title": "Buy groceries", "completed": false},
  {"id": 3, "title": "Pay bills", "completed": false}
]
```

---

### Tool: complete_task

**Purpose**: Mark a task as complete

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID from JWT token |
| task_id | integer | Yes | ID of the task to complete |

**Example Input**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": 3
}
```

**Example Output**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

**Error Output** (task not found):
```json
{
  "error": "Task not found",
  "task_id": 999
}
```

---

### Tool: delete_task

**Purpose**: Remove a task from the list

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID from JWT token |
| task_id | integer | Yes | ID of the task to delete |

**Example Input**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": 2
}
```

**Example Output**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

---

### Tool: update_task

**Purpose**: Modify task title or description

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID from JWT token |
| task_id | integer | Yes | ID of the task to update |
| title | string | No | New task title |
| description | string | No | New task description |

**Example Input**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}
```

**Example Output**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

---

## Agent Behavior Specification

The AI agent should interpret user messages and call appropriate MCP tools.

| User Says | Agent Should |
|-----------|--------------|
| "Add a task to buy groceries" | Call `add_task` with title "Buy groceries" |
| "Show me all my tasks" | Call `list_tasks` with status "all" |
| "What's pending?" | Call `list_tasks` with status "pending" |
| "Mark task 3 as complete" | Call `complete_task` with task_id 3 |
| "Delete the meeting task" | Call `list_tasks` first, then `delete_task` |
| "Change task 1 to 'Call mom tonight'" | Call `update_task` with new title |
| "I need to remember to pay bills" | Call `add_task` with title "Pay bills" |
| "What have I completed?" | Call `list_tasks` with status "completed" |

---

## HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| 200 | OK | Successful GET/POST request |
| 201 | Created | New conversation created |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request body |
| 401 | Unauthorized | Missing or invalid JWT |
| 404 | Not Found | Conversation not found |
| 500 | Internal Server Error | Server or OpenAI API error |
