# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack todo application with Next.js frontend and FastAPI backend, using Neon PostgreSQL for persistence. Uses Better Auth for authentication with JWT tokens shared between frontend and backend.

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
- **App Router**: Pages in `src/app/` (login, signup, dashboard)
- **API Routes**: Better Auth handler in `src/app/api/auth/[...all]/route.ts`
- **Components**: `src/components/tasks/` (task-list, task-item, task-form, task-filters), `src/components/ui/` (shadcn)
- **API Client**: `src/lib/api.ts` - typed fetch wrapper with JWT from cookies
- **Hooks**: `src/lib/hooks/use-tasks.ts` - React Query hooks for CRUD
- **State**: React Query for server state, no additional state management

### Backend Structure
- **Entry**: `src/main.py` - FastAPI app with CORS, routers
- **Routes**: `src/api/v1/tasks.py` - all task CRUD endpoints
- **Models**: `src/models/task.py` - SQLModel Task class
- **Schemas**: `src/schemas/task.py` - Pydantic request/response models
- **Services**: `src/services/task_service.py` - business logic, DB operations
- **Security**: `src/core/security.py` - JWT verification, user extraction
- **Config**: `src/core/config.py` - settings from environment

### Database
- Neon PostgreSQL (serverless)
- Tasks table: id, user_id, title, description, completed, created_at, updated_at
- Better Auth tables: user, session, account (auto-managed)

## API Endpoints

All endpoints at `http://localhost:8000/api/v1/tasks` require JWT in Authorization header:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tasks | List tasks (supports ?status=pending\|completed&sort_by=created_at\|title&order=asc\|desc) |
| POST | /tasks | Create task |
| GET | /tasks/{id} | Get single task |
| PUT | /tasks/{id} | Update task |
| PATCH | /tasks/{id}/complete | Toggle completion |
| DELETE | /tasks/{id} | Delete task |

API docs available at http://localhost:8000/docs (Swagger) or /redoc

## Key Files

- `frontend/.env.local` / `backend/.env` - Environment config (DATABASE_URL, BETTER_AUTH_SECRET)
- `frontend/auth-schema.ts` - Better Auth database schema
- `backend/scripts/create_tables.py` - Task table migration script
