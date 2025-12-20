# API Contracts: Phase 2 - Todo Full-Stack Web Application

**Date**: 2025-01-27  
**Feature**: Phase 2 Full-Stack Web Application  
**Base URL**:

- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

## Authentication

All endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

**JWT Token Format**:

- Issued by: Better Auth (frontend)
- Shared secret: `BETTER_AUTH_SECRET` (environment variable)
- Token payload includes: `user_id`, `email`, `exp` (expiration)
- Default expiration: 7 days

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
- `401 Unauthorized`: Expired JWT token

## Endpoints

### Task Management

#### GET /api/v1/tasks

List all tasks for the authenticated user.

**Query Parameters**:

- `status` (optional, string): Filter by status
  - Values: `"all"` | `"pending"` | `"completed"`
  - Default: `"all"`
- `sort` (optional, string): Sort field
  - Values: `"created"` | `"title"` | `"updated"`
  - Default: `"created"`
- `order` (optional, string): Sort order
  - Values: `"asc"` | `"desc"`
  - Default: `"desc"`

**Request Headers**:

```
Authorization: Bearer <jwt_token>
```

**Response**: `200 OK`

```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-01-27T10:30:00Z",
      "updated_at": "2025-01-27T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token

---

#### POST /api/v1/tasks

Create a new task for the authenticated user.

**Request Headers**:

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Validation Rules**:

- `title` (required): String, 1-200 characters, cannot be empty
- `description` (optional): String, max 1000 characters

**Response**: `201 Created`

```json
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

**Error Responses**:

- `400 Bad Request`: Validation error (e.g., empty title, title too long)
  ```json
  {
    "detail": "Title must be between 1 and 200 characters"
  }
  ```
- `401 Unauthorized`: Missing or invalid JWT token

---

#### GET /api/v1/tasks/{task_id}

Get task details by ID.

**Path Parameters**:

- `task_id` (integer): Task ID

**Request Headers**:

```
Authorization: Bearer <jwt_token>
```

**Response**: `200 OK`

```json
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

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Task not found or belongs to another user
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

#### PUT /api/v1/tasks/{task_id}

Update task (title and/or description).

**Path Parameters**:

- `task_id` (integer): Task ID

**Request Headers**:

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:

```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread, chicken"
}
```

**Validation Rules**:

- `title` (optional): String, 1-200 characters if provided
- `description` (optional): String, max 1000 characters if provided
- At least one field must be provided

**Response**: `200 OK`

```json
{
  "id": 1,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread, chicken",
  "completed": false,
  "created_at": "2025-01-27T10:30:00Z",
  "updated_at": "2025-01-27T11:00:00Z"
}
```

**Error Responses**:

- `400 Bad Request`: Validation error
  ```json
  {
    "detail": "Title must be between 1 and 200 characters"
  }
  ```
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Task not found or belongs to another user

---

#### PATCH /api/v1/tasks/{task_id}/complete

Toggle task completion status.

**Path Parameters**:

- `task_id` (integer): Task ID

**Request Headers**:

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body** (optional):

```json
{
  "completed": true
}
```

If `completed` is not provided, the status is toggled (incomplete → completed, completed → incomplete).

**Response**: `200 OK`

```json
{
  "id": 1,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2025-01-27T10:30:00Z",
  "updated_at": "2025-01-27T11:15:00Z"
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Task not found or belongs to another user

---

#### DELETE /api/v1/tasks/{task_id}

Delete a task.

**Path Parameters**:

- `task_id` (integer): Task ID

**Request Headers**:

```
Authorization: Bearer <jwt_token>
```

**Response**: `204 No Content` (empty body)

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Task not found or belongs to another user

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (400 Bad Request), additional field-level errors may be included:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title must be between 1 and 200 characters",
      "type": "value_error"
    }
  ]
}
```

## HTTP Status Codes

- `200 OK`: Successful GET, PUT, PATCH request
- `201 Created`: Successful POST request (resource created)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error or malformed request
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Valid token but insufficient permissions (not used in Phase 2)
- `404 Not Found`: Resource not found or belongs to another user
- `500 Internal Server Error`: Server error (should not expose internal details)

## Rate Limiting

Not implemented in Phase 2. Can be added in future phases.

## CORS Configuration

Backend must allow requests from frontend origin:

- Development: `http://localhost:3000`
- Production: Frontend domain (e.g., `https://yourdomain.com`)

**CORS Headers**:

```
Access-Control-Allow-Origin: <frontend-origin>
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```

## API Documentation

FastAPI automatically generates OpenAPI/Swagger documentation at:

- Development: `http://localhost:8000/docs`
- Development: `http://localhost:8000/redoc`
