# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack todo application with Next.js frontend and FastAPI backend, using Neon PostgreSQL for persistence. Features AI-powered task management chatbot using OpenAI Agents SDK, event-driven architecture with Dapr + Kafka, and Kubernetes deployment with CI/CD. Uses Better Auth for authentication with JWT tokens shared between frontend and backend.

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

### Kubernetes/Dapr (from project root)
```bash
./scripts/setup-dapr-kafka.sh              # Setup Dapr + Kafka on Minikube
./scripts/setup-dapr-kafka.sh --deploy-app # Setup and deploy app
dapr status -k                             # Check Dapr status
kubectl get pods                           # Check pod status
helm upgrade --install todo-release helm-chart/todo-app --set dapr.enabled=true
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
- **App Router**: Pages in `src/app/` (login, signup, dashboard, chat)
- **API Routes**: Better Auth handler in `src/app/api/auth/[...all]/route.ts`
- **Components**:
  - `src/components/tasks/` - task management UI (task-list, task-item, task-form, task-filters)
  - `src/components/chat/` - AI chat UI (chat-interface, chat-message, chat-input)
  - `src/components/ui/` - shadcn components
- **API Clients**:
  - `src/lib/api.ts` - task API client with JWT
  - `src/lib/api/chat.ts` - chat API client
- **Hooks**:
  - `src/lib/hooks/use-tasks.ts` - React Query hooks for tasks
  - `src/lib/hooks/use-chat.ts` - chat state management
- **State**: React Query for server state, no additional state management

### Backend Structure
- **Entry**: `src/main.py` - FastAPI app with CORS, routers, Dapr lifecycle
- **Routes**:
  - `src/api/v1/tasks.py` - task CRUD endpoints with event publishing
  - `src/api/v1/chat.py` - chat endpoints
  - `src/api/v1/events.py` - Dapr event consumer endpoints (Phase 5)
- **Models**:
  - `src/models/task.py` - SQLModel Task class (with priority, tags, due_date, recurrence)
  - `src/models/conversation.py` - Conversation model
  - `src/models/message.py` - Message model
- **Schemas**:
  - `src/schemas/task.py` - task request/response models
  - `src/schemas/chat.py` - chat request/response models
  - `src/schemas/conversation.py` - conversation models
- **Services**:
  - `src/services/task_service.py` - task business logic
  - `src/services/chat_service.py` - AI chat orchestration
  - `src/services/conversation_service.py` - conversation management
- **Events (Phase 5)**:
  - `src/events/schemas.py` - CloudEvents-compatible event schemas
  - `src/events/producer.py` - Event publisher for Kafka via Dapr
- **AI Agent**:
  - `src/agent/agent.py` - agent definition with function tools
  - `src/agent/model_provider.py` - OpenAI model provider
- **Core**:
  - `src/core/security.py` - JWT verification, user extraction
  - `src/core/config.py` - settings from environment
  - `src/core/dapr.py` - Dapr client wrapper (Phase 5)

### Database
- Neon PostgreSQL (serverless)
- **Tasks table**: id, user_id, title, description, completed, due_date, priority, tags, recurrence_pattern, created_at, updated_at
- **Conversations table**: id, user_id, created_at, updated_at
- **Messages table**: id, conversation_id, user_id, role, content, tool_calls, created_at
- Better Auth tables: user, session, account (auto-managed)

### Event System (Phase 5)
- **Message Broker**: Apache Kafka via Dapr pub/sub
- **Topics**:
  - `task-events` - Task lifecycle events (created, updated, completed, deleted)
  - `reminders` - Due date reminders (due_soon, overdue)
  - `task-updates` - Real-time sync events
- **Event Format**: CloudEvents specification
- **Producer**: `src/events/producer.py` publishes via Dapr HTTP API
- **Consumer**: `src/api/v1/events.py` receives events from Dapr

### Kubernetes Deployment (Phase 4-5)
- **Helm Chart**: `helm-chart/todo-app/` with staging/production values
- **Dapr Components**: `helm-chart/dapr-components/` (pubsub, subscriptions)
- **Kafka**: `helm-chart/kafka/` (Strimzi cluster, topics)
- **CI/CD**: `.github/workflows/deploy.yml` (GitHub Actions to Azure AKS)

## API Endpoints

All endpoints require JWT in Authorization header.

### Task Endpoints (`/api/v1/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tasks | List tasks (supports filtering, sorting, search) |
| POST | /tasks | Create task (publishes task.created event) |
| GET | /tasks/{id} | Get single task |
| PUT | /tasks/{id} | Update task (publishes task.updated event) |
| PATCH | /tasks/{id}/complete | Toggle completion (publishes task.completed/uncompleted) |
| DELETE | /tasks/{id} | Delete task (publishes task.deleted event) |
| GET | /tasks/tags | Get all unique tags for user |

### Chat Endpoints (`/api/v1/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat | Send message to AI assistant |
| GET | /chat/conversations | List all conversations for user |
| GET | /chat/conversations/{id} | Get conversation with all messages |
| DELETE | /chat/conversations/{id} | Delete conversation and all messages |

### Event Endpoints (`/api/v1/events`) - Dapr Consumer
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /events/tasks | Handle task-events topic |
| POST | /events/reminders | Handle reminders topic |
| POST | /events/task-updates | Handle task-updates topic |
| GET | /events/dapr/subscribe | Dapr subscription discovery |

API docs available at http://localhost:8000/docs (Swagger) or /redoc

## Key Files

- `frontend/.env.local` - Frontend environment config
- `backend/.env` - Backend environment config (includes OPENAI_API_KEY, DAPR_ENABLED)
- `frontend/auth-schema.ts` - Better Auth database schema
- `backend/scripts/create_tables.py` - Database migration script
- `helm-chart/todo-app/values.yaml` - Helm chart default values
- `helm-chart/todo-app/values-staging.yaml` - Staging environment overrides
- `helm-chart/todo-app/values-production.yaml` - Production environment overrides
- `.github/workflows/deploy.yml` - CI/CD pipeline

## Environment Variables

### Backend
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT signing secret (must match frontend)
- `OPENAI_API_KEY` - OpenAI API key for AI chatbot
- `CORS_ORIGINS` - Allowed CORS origins
- `DAPR_ENABLED` - Enable Dapr event publishing (default: false)

### Frontend
- `DATABASE_URL` - Neon PostgreSQL connection string (server-side)
- `BETTER_AUTH_SECRET` - JWT signing secret (must match backend)
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Documentation

- `docs/architecture.md` - System architecture with diagrams
- `docs/kafka-topics.md` - Kafka topics and event schemas
- `docs/dapr-setup.md` - Dapr installation and configuration
- `docs/cicd.md` - CI/CD pipeline documentation
