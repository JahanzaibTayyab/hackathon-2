# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack todo application with Next.js frontend and FastAPI backend, using Neon PostgreSQL for persistence. Features AI-powered task management chatbot using OpenAI Agents SDK. Uses Better Auth for authentication with JWT tokens shared between frontend and backend.

## Commands

### Frontend (from `/frontend`)
```bash
pnpm dev                 # Start dev server (http://localhost:3000)
pnpm build              # Production build
pnpm test               # Run Jest unit tests
pnpm test:watch         # Jest in watch mode
pnpm test:coverage      # Jest with coverage
pnpm test:e2e           # Run Playwright E2E tests
pnpm db:check           # Verify database connection
```

### Backend (from `/backend`)
```bash
uv run uvicorn src.main:app --reload --port 8000  # Start dev server
uv run pytest                                      # Run all tests
uv run pytest tests/unit                           # Unit tests only
uv run pytest tests/integration                    # Integration tests only
uv run pytest --cov                                # Tests with coverage
uv run python scripts/create_tables.py             # Create database tables
uv run ruff check src                              # Lint code
```

### Running a Single Test
```bash
# Frontend
pnpm test -- path/to/test.test.ts

# Backend
uv run pytest tests/unit/test_file.py::test_function -v
```

## Architecture

### Authentication Flow
1. Frontend uses Better Auth (`lib/auth.ts`, `lib/auth-client.ts`) with JWT plugin
2. JWT tokens signed with `BETTER_AUTH_SECRET` (shared between frontend/backend)
3. Backend verifies JWT via `core/security.py` - extracts `user_id` from token
4. All task API endpoints require valid JWT; user isolation enforced by `user_id`

### Frontend Structure
- **App Router**: Pages in `src/app/` (login, signup, dashboard, **chat** - Phase 3)
- **API Routes**: Better Auth handler in `src/app/api/auth/[...all]/route.ts`
- **Components**:
  - `src/components/tasks/` - task management UI (task-list, task-item, task-form, task-filters)
  - `src/components/chat/` - **Phase 3** AI chat UI (chat-interface, chat-message, chat-input)
  - `src/components/ui/` - shadcn components
- **API Clients**:
  - `src/lib/api.ts` - task API client with JWT
  - `src/lib/api/chat.ts` - **Phase 3** chat API client
- **Hooks**:
  - `src/lib/hooks/use-tasks.ts` - React Query hooks for tasks
  - `src/lib/hooks/use-chat.ts` - **Phase 3** chat state management
- **State**: React Query for server state, no additional state management

### Backend Structure
- **Entry**: `src/main.py` - FastAPI app with CORS, routers
- **Routes**:
  - `src/api/v1/tasks.py` - task CRUD endpoints
  - `src/api/v1/chat.py` - **Phase 3** chat endpoints
- **Models**:
  - `src/models/task.py` - SQLModel Task class
  - `src/models/conversation.py` - **Phase 3** Conversation model
  - `src/models/message.py` - **Phase 3** Message model
- **Schemas**:
  - `src/schemas/task.py` - task request/response models
  - `src/schemas/chat.py` - **Phase 3** chat request/response models
  - `src/schemas/conversation.py` - **Phase 3** conversation models
- **Services**:
  - `src/services/task_service.py` - task business logic
  - `src/services/chat_service.py` - **Phase 3** AI chat orchestration
  - `src/services/conversation_service.py` - **Phase 3** conversation management
- **AI Agent** (Phase 3):
  - `src/agent/agent.py` - agent definition with function tools
  - `src/agent/model_provider.py` - OpenAI model provider
- **Security**: `src/core/security.py` - JWT verification, user extraction
- **Config**: `src/core/config.py` - settings from environment

### Database
- Neon PostgreSQL (serverless)
- **Tasks table**: id, user_id, title, description, completed, created_at, updated_at
- **Conversations table** (Phase 3): id, user_id, created_at, updated_at
- **Messages table** (Phase 3): id, conversation_id, user_id, role, content, tool_calls, created_at
- Better Auth tables: user, session, account (auto-managed)

### AI Chatbot (Phase 3)
- **AI Model**: OpenAI GPT-4o-mini via OpenAI Agents SDK
- **Agent Framework**: OpenAI Agents SDK with custom model provider
- **Tools**: 5 MCP-compatible tools (add_task, list_tasks, complete_task, delete_task, update_task)
- **Conversation**: Stateless - all history persisted to PostgreSQL
- **Agent Structure**:
  - `src/agent/agent.py` - Agent definition with function tools
  - `src/agent/model_provider.py` - OpenAI model provider configuration
  - `src/services/chat_service.py` - Chat orchestration with conversation management
  - `src/mcp/server.py` - MCP server with 5 task tools (optional, not used with function_tool approach)

## API Endpoints

All endpoints require JWT in Authorization header.

### Task Endpoints (`/api/v1/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tasks | List tasks (supports ?status=pending\|completed&sort_by=created_at\|title&order=asc\|desc) |
| POST | /tasks | Create task |
| GET | /tasks/{id} | Get single task |
| PUT | /tasks/{id} | Update task |
| PATCH | /tasks/{id}/complete | Toggle completion |
| DELETE | /tasks/{id} | Delete task |

### Chat Endpoints (`/api/v1/chat`) - Phase 3
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat | Send message to AI assistant (returns conversation_id, response, tool_calls) |
| GET | /chat/conversations | List all conversations for user |
| GET | /chat/conversations/{id} | Get conversation with all messages |
| DELETE | /chat/conversations/{id} | Delete conversation and all messages |

API docs available at http://localhost:8000/docs (Swagger) or /redoc

## Key Files

- `frontend/.env.local` - Frontend environment config (DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL)
- `backend/.env` - Backend environment config (DATABASE_URL, BETTER_AUTH_SECRET, **OPENAI_API_KEY** - Phase 3)
- `frontend/auth-schema.ts` - Better Auth database schema
- `backend/scripts/create_tables.py` - Database migration script (tasks, conversations, messages)

## Environment Variables

### Required for Phase 3:
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys (in `backend/.env`)
  - Used by AI agent for natural language task management
  - Currently configured for GPT-4o-mini model
