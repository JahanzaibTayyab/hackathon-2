# Implementation Plan: Phase 2 - Todo Full-Stack Web Application

**Branch**: `phase-2-full-stack-web` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Hackathon II - Todo Spec-Driven Development requirements for Phase 2

## Summary

Phase 2 transforms the Phase 1 console application into a modern, multi-user full-stack web application with persistent storage. This phase implements all 5 Basic Level features (Add, Delete, Update, View, Mark Complete) as a web application with RESTful API endpoints, responsive frontend interface, and user authentication. The application uses a monorepo structure with Next.js frontend, FastAPI backend, SQLModel ORM, and Neon Serverless PostgreSQL database.

**Package Managers**: Frontend uses **pnpm** (always) and backend uses **UV** (always) for all dependency management.

## Technical Context

**Language/Version**:

- Frontend: TypeScript (latest), Node.js (latest LTS)
- Backend: Python 3.11+ (latest 3.11+)

**Primary Dependencies** (all packages use latest versions automatically):

- Frontend: Next.js (latest, App Router), React (latest), Tailwind CSS (latest), shadcn/ui (latest), Better Auth (latest)
- Backend: FastAPI (latest), SQLModel (latest), Pydantic (latest), PyJWT (latest), httpx (latest)
- Database: Neon Serverless PostgreSQL
- Development: Claude Code, Spec-Kit Plus

**Package Managers**:

- Frontend: pnpm (always use pnpm for all frontend dependencies)
- Backend: UV (always use UV for all backend dependencies)

**Storage**: Neon Serverless PostgreSQL (persistent, multi-user)

**Testing**:

- Frontend: Jest, React Testing Library, Playwright (E2E)
- Backend: pytest, httpx (for async testing), pytest-asyncio

**Target Platform**:

- Web browsers (Chrome, Firefox, Safari, Edge)
- Deployment: Vercel (frontend), Railway/Render/Fly.io (backend)

**Project Type**: Monorepo (full-stack web application)

**Performance Goals**:

- API response time: <200ms p95
- Frontend initial load: <2s
- Support 1000+ concurrent users
- Handle 10,000+ tasks per user

**Constraints**:

- Must use Spec-Driven Development (no manual coding)
- JWT-based authentication required
- Stateless backend architecture
- Responsive design (mobile-first)
- CORS configuration for frontend-backend communication

**Scale/Scope**:

- Multi-user application
- User isolation (each user sees only their tasks)
- Persistent data storage
- Production-ready deployment

## Constitution Check

_GATE: Must pass before implementation. Re-check after design phase._

- ✅ Test-First Development: All features must have tests written first (TDD)
- ✅ Spec-Driven Development: Must use Spec-Kit Plus workflow (Specify → Plan → Tasks → Implement)
- ✅ Code Quality: Clean, readable, well-documented code with type hints
- ✅ Incremental Delivery: MVP first (Basic Level features), then enhancements
- ⚠️ CLI Interface: Phase 2 moves to web interface (constitution allows evolution per phase)
- ✅ Simplicity First: Start with Basic Level features, avoid over-engineering

## Project Structure

### Documentation (this feature)

```text
specs/phase-2-full-stack-web/
├── plan.md              # This file
├── spec.md              # Feature requirements (to be created)
├── tasks.md             # Implementation tasks (to be created)
├── data-model.md        # Database schema and models
├── api-contracts.md     # REST API endpoint specifications
└── quickstart.md        # User guide and setup instructions
```

### Monorepo Structure (repository root)

```text
hackathon-todo/
├── .spec-kit/
│   └── config.yaml      # Spec-Kit configuration
├── specs/               # Spec-Kit managed specifications
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/
│   │   └── rest-endpoints.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       ├── components.md
│       └── pages.md
├── CLAUDE.md            # Root Claude Code instructions
├── frontend/            # Next.js application
│   ├── CLAUDE.md        # Frontend-specific guidelines
│   ├── package.json
│   ├── pnpm-lock.yaml   # pnpm lock file
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/         # App Router pages
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── login/
│   │   │   ├── signup/
│   │   │   └── dashboard/
│   │   ├── components/  # React components
│   │   │   ├── ui/      # shadcn/ui components (Button, Input, Card, etc.)
│   │   │   ├── tasks/   # Task-related components
│   │   │   └── auth/    # Auth-related components
│   │   ├── lib/         # Utilities and helpers
│   │   │   ├── api.ts   # API client
│   │   │   ├── auth.ts  # Auth utilities
│   │   │   └── utils.ts
│   │   └── types/       # TypeScript types
│   │       └── task.ts
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── e2e/
├── backend/             # FastAPI application
│   ├── CLAUDE.md        # Backend-specific guidelines
│   ├── pyproject.toml   # UV project configuration
│   ├── uv.lock          # UV lock file
│   ├── src/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── models/      # SQLModel models
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   └── user.py
│   │   ├── api/         # API routes
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tasks.py
│   │   │   │   └── auth.py
│   │   ├── core/        # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py  # JWT verification
│   │   │   └── dependencies.py
│   │   ├── services/     # Business logic
│   │   │   ├── __init__.py
│   │   │   └── task_service.py
│   │   └── schemas/     # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── task.py
│   │       └── user.py
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── conftest.py
├── docker-compose.yml   # Local development setup
├── README.md            # Project documentation
└── .env.example         # Environment variables template
```

**Structure Decision**: Monorepo structure selected to enable Spec-Kit Plus workflow and allow Claude Code to work with both frontend and backend in a single context. This aligns with the hackathon requirements for spec-driven development.

## Architecture Overview

### System Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   Next.js       │────────▶│   FastAPI       │────────▶│   Neon          │
│   Frontend      │  HTTP   │   Backend       │  SQL    │   PostgreSQL    │
│   (Vercel)      │  +JWT   │   (Railway)     │         │   (Serverless)  │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │
         │                           │
         └──────────────────────────┘
                   Better Auth
              (JWT Token Management)
```

### Component Breakdown

#### 1. Frontend (Next.js 16+ App Router)

**Core Components:**

- **Layout System**: Root layout with authentication context
- **Authentication Pages**: Login, Signup, Logout (using shadcn/ui form components)
- **Dashboard Page**: Main task management interface (using shadcn/ui layout components)
- **Task Components**: TaskList, TaskItem, TaskForm, TaskFilters (built with shadcn/ui)
- **UI Components**: shadcn/ui base components (Button, Input, Card, Dialog, Select, etc.)
- **API Client**: Centralized HTTP client with JWT token management
- **Auth Context**: React context for user session management

**Key Features:**

- Server Components by default (React Server Components)
- Client Components only for interactivity
- TypeScript for type safety
- Tailwind CSS for styling
- shadcn/ui for accessible, customizable UI components
- Better Auth for authentication UI and token management

#### 2. Backend (FastAPI)

**Core Components:**

- **API Routes**: RESTful endpoints under `/api/v1/`
- **SQLModel Models**: Database models (Task, User)
- **Pydantic Schemas**: Request/response validation
- **JWT Middleware**: Token verification and user extraction
- **Database Layer**: SQLModel session management
- **Services**: Business logic separation

**Key Features:**

- Async/await for performance
- Automatic API documentation (Swagger/OpenAPI)
- Request validation via Pydantic
- CORS configuration for frontend
- Environment-based configuration

#### 3. Database (Neon PostgreSQL)

**Schema:**

- **users table**: Managed by Better Auth (id, email, name, created_at)
- **tasks table**:
  - id (primary key, auto-increment)
  - user_id (foreign key → users.id)
  - title (required, varchar 200)
  - description (optional, text)
  - completed (boolean, default false)
  - created_at (timestamp)
  - updated_at (timestamp)

**Indexes:**

- tasks.user_id (for user filtering)
- tasks.completed (for status filtering)
- tasks.created_at (for sorting)

#### 4. Authentication Flow (Better Auth + JWT)

**Flow:**

1. User signs up/logs in via Better Auth (frontend)
2. Better Auth creates session and issues JWT token
3. Frontend stores JWT token (httpOnly cookie or localStorage)
4. Frontend includes JWT in `Authorization: Bearer <token>` header for API calls
5. Backend verifies JWT signature using shared secret (`BETTER_AUTH_SECRET`)
6. Backend extracts user_id from JWT payload
7. Backend filters all operations by authenticated user_id

**Security:**

- JWT tokens expire (configurable, default 7 days)
- Shared secret stored in environment variables
- HTTPS required in production
- CORS configured for frontend domain only

## API Design

### Base URL

- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

### Authentication

All endpoints require JWT token in header:

```
Authorization: Bearer <jwt_token>
```

### Endpoints

#### Task Management

**GET /api/v1/tasks**

- List all tasks for authenticated user
- Query parameters:
  - `status`: "all" | "pending" | "completed" (default: "all")
  - `sort`: "created" | "title" | "updated" (default: "created")
  - `order`: "asc" | "desc" (default: "desc")
- Response: `200 OK` with array of task objects

**POST /api/v1/tasks**

- Create a new task
- Request body:
  ```json
  {
    "title": "string (required, 1-200 chars)",
    "description": "string (optional, max 1000 chars)"
  }
  ```
- Response: `201 Created` with created task object

**GET /api/v1/tasks/{task_id}**

- Get task details by ID
- Response: `200 OK` with task object or `404 Not Found`

**PUT /api/v1/tasks/{task_id}**

- Update task (title and/or description)
- Request body:
  ```json
  {
    "title": "string (optional)",
    "description": "string (optional)"
  }
  ```
- Response: `200 OK` with updated task object or `404 Not Found`

**PATCH /api/v1/tasks/{task_id}/complete**

- Toggle task completion status
- Request body: empty or `{"completed": true/false}`
- Response: `200 OK` with updated task object or `404 Not Found`

**DELETE /api/v1/tasks/{task_id}**

- Delete a task
- Response: `204 No Content` or `404 Not Found`

### Error Responses

All endpoints return consistent error format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success (no body)
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing/invalid JWT token
- `403 Forbidden`: User doesn't own resource
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Database Schema

### Users Table (Managed by Better Auth)

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

## Implementation Phases

### Phase 1: Project Setup & Infrastructure

**Goal**: Establish monorepo structure and development environment

**Tasks:**

1. Initialize monorepo structure
2. Set up Spec-Kit configuration (`.spec-kit/config.yaml`)
3. Create root and subdirectory CLAUDE.md files
4. Install pnpm (if not already installed) for frontend package management
5. Create Next.js project using pnpm (`pnpm create next-app@latest`) with TypeScript and Tailwind CSS
6. Install and initialize shadcn/ui (`pnpm dlx shadcn-ui@latest init`)
7. Install UV (if not already installed) for backend package management
8. Initialize backend project using UV (`uv init`) and add required packages (FastAPI, SQLModel, pytest, etc.) with latest versions
9. Set up environment variable management
10. Configure Docker Compose for local development
11. Set up database connection (Neon)
12. Create database migration scripts
13. Configure CORS and security settings

**Deliverables:**

- Working monorepo structure
- pnpm configured for frontend (package.json, pnpm-lock.yaml)
- UV configured for backend (pyproject.toml, uv.lock)
- Both frontend and backend can start locally
- Database connection established
- Spec-Kit structure in place

### Phase 2: Authentication Foundation

**Goal**: Implement user authentication with Better Auth and JWT

**Tasks:**

1. Install Better Auth using pnpm (`pnpm add better-auth@latest`)
2. Configure Better Auth with JWT plugin
3. Create login page (frontend)
4. Create signup page (frontend)
5. Implement JWT verification middleware (backend)
6. Create user extraction dependency (backend)
7. Test authentication flow end-to-end
8. Configure shared secret (`BETTER_AUTH_SECRET`)
9. Implement logout functionality
10. Add protected route wrapper (frontend)

**Deliverables:**

- Users can sign up and log in
- JWT tokens are issued and verified
- Protected routes work correctly
- Logout functionality works

### Phase 3: Database Models & Migrations

**Goal**: Define and create database schema

**Tasks:**

1. Create SQLModel Task model
2. Create database connection utility
3. Create database migration script
4. Run initial migration on Neon
5. Create Pydantic schemas for API
6. Test database operations (CRUD)
7. Add database indexes
8. Create database seed script (optional, for testing)

**Deliverables:**

- Database schema created
- Models defined and tested
- Migration scripts ready
- Database connection working

### Phase 4: Backend API Implementation

**Goal**: Implement all REST API endpoints

**Tasks:**

1. Create task service layer (business logic)
2. Implement GET /api/v1/tasks (list with filters)
3. Implement POST /api/v1/tasks (create)
4. Implement GET /api/v1/tasks/{id} (get one)
5. Implement PUT /api/v1/tasks/{id} (update)
6. Implement PATCH /api/v1/tasks/{id}/complete (toggle)
7. Implement DELETE /api/v1/tasks/{id} (delete)
8. Add request validation
9. Add error handling
10. Write API tests (pytest)
11. Test JWT authentication on all endpoints
12. Test user isolation (users can't access others' tasks)

**Deliverables:**

- All API endpoints implemented
- All endpoints tested
- User isolation verified
- API documentation generated (Swagger)

### Phase 5: Frontend API Client & State Management

**Goal**: Create frontend infrastructure for API communication

**Tasks:**

1. Create API client utility (`lib/api.ts`)
2. Implement JWT token management
3. Add request interceptors for auth headers
4. Add error handling and retry logic
5. Create TypeScript types for API responses
6. Install and set up React Query using pnpm (`pnpm add @tanstack/react-query@latest`)
7. Create custom hooks for task operations
8. Test API client with mock data

**Deliverables:**

- API client fully functional
- Token management working
- Data fetching hooks ready
- Error handling in place

### Phase 6: Frontend UI Components

**Goal**: Build user interface components using shadcn/ui

**Tasks:**

1. Install and configure shadcn/ui with Next.js and Tailwind CSS using pnpm (`pnpm dlx shadcn-ui@latest init`)
2. Add shadcn/ui base components (Button, Input, Card, Dialog, Select, etc.)
3. Create TaskItem component using shadcn/ui components
4. Create TaskList component using shadcn/ui components
5. Create TaskForm component (create/edit) using shadcn/ui Form components
6. Create TaskFilters component using shadcn/ui Select/Dropdown components
7. Create Dashboard layout with shadcn/ui layout components
8. Add loading states using shadcn/ui Skeleton components
9. Add error states using shadcn/ui Alert components
10. Implement responsive design (shadcn/ui components are responsive by default)
11. Customize shadcn/ui theme to match application design
12. Add accessibility features (shadcn/ui components are accessible by default)

**Deliverables:**

- shadcn/ui installed and configured
- All UI components created using shadcn/ui
- Responsive design implemented (shadcn/ui responsive by default)
- Accessibility features added (shadcn/ui accessible by default)
- Components tested (unit tests)
- Custom theme applied

### Phase 7: Frontend Pages & Integration

**Goal**: Connect frontend pages with backend API

**Tasks:**

1. Create dashboard page with task list
2. Integrate task creation form
3. Integrate task update functionality
4. Integrate task deletion
5. Integrate task completion toggle
6. Add task filtering UI
7. Add task sorting UI
8. Implement real-time updates (optimistic updates)
9. Add success/error notifications
10. Test complete user workflows

**Deliverables:**

- All pages functional
- Full CRUD operations working
- User can complete all workflows
- UI is polished and responsive

### Phase 8: Testing & Quality Assurance

**Goal**: Comprehensive testing coverage

**Tasks:**

1. Write backend unit tests (models, services)
2. Write backend integration tests (API endpoints)
3. Write frontend unit tests (components)
4. Write frontend integration tests (pages)
5. Write E2E tests (Playwright)
6. Test authentication flows
7. Test user isolation scenarios
8. Test error handling
9. Achieve 80%+ code coverage
10. Run security audit

**Deliverables:**

- 80%+ test coverage
- All tests passing
- E2E tests covering critical paths
- Security vulnerabilities addressed

### Phase 9: Deployment Preparation

**Goal**: Prepare for production deployment

**Tasks:**

1. Configure environment variables for production
2. Set up Vercel project (frontend)
3. Set up backend hosting (Railway/Render/Fly.io)
4. Configure production database (Neon)
5. Set up CI/CD pipeline (GitHub Actions) with pnpm for frontend and UV for backend
6. Add health check endpoints
7. Configure logging and monitoring
8. Set up error tracking (Sentry optional)
9. Create deployment documentation
10. Test production deployment

**Deliverables:**

- Application deployed to production
- CI/CD pipeline working
- Monitoring in place
- Documentation complete

### Phase 10: Polish & Documentation

**Goal**: Final touches and documentation

**Tasks:**

1. Update README with setup instructions
2. Create API documentation
3. Create user guide
4. Add code comments and docstrings
5. Optimize performance (bundle size, API response times)
6. Add loading skeletons
7. Improve error messages
8. Add helpful tooltips
9. Final UI/UX polish
10. Create demo video script

**Deliverables:**

- Complete documentation
- Polished user experience
- Performance optimized
- Ready for submission

## Testing Strategy

### Backend Testing

**Unit Tests:**

- Model validation
- Service layer logic
- JWT token verification
- Database operations (with test database)

**Integration Tests:**

- API endpoint testing (with test client)
- Authentication flow testing
- User isolation testing
- Error scenario testing

**Test Tools:**

- pytest for test framework
- pytest-asyncio for async tests
- httpx.AsyncClient for API testing
- SQLModel test database (SQLite in-memory for speed)

### Frontend Testing

**Unit Tests:**

- Component rendering
- User interactions
- Form validation
- Utility functions

**Integration Tests:**

- Page workflows
- API client integration
- Authentication flows

**E2E Tests:**

- Complete user journeys
- Cross-browser testing
- Mobile responsiveness

**Test Tools:**

- Jest + React Testing Library for unit/integration
- Playwright for E2E testing
- MSW (Mock Service Worker) for API mocking

### Test Coverage Goals

- Minimum 80% code coverage
- 100% coverage for critical paths (auth, task CRUD)
- All user workflows covered by E2E tests

## Security Considerations

### Authentication Security

- JWT tokens stored securely (httpOnly cookies preferred)
- Token expiration enforced
- Shared secret stored in environment variables (never in code)
- HTTPS required in production

### API Security

- All endpoints require authentication
- User isolation enforced at database level
- Input validation on all endpoints
- SQL injection prevention (SQLModel parameterized queries)
- CORS configured for frontend domain only
- Rate limiting (consider adding in production)

### Data Security

- User data isolated by user_id
- No sensitive data in API responses
- Database credentials in environment variables
- Regular security audits

## Performance Considerations

### Frontend Performance

- Code splitting (Next.js automatic)
- Image optimization
- Lazy loading for components
- Optimistic UI updates
- Client-side caching (React Query/SWR)

### Backend Performance

- Database query optimization (indexes)
- Connection pooling
- Async/await for I/O operations
- Response caching where appropriate
- Pagination for large result sets (future enhancement)

### Database Performance

- Proper indexing (user_id, completed, created_at)
- Connection pooling
- Query optimization
- Consider read replicas for scale (future)

## Error Handling

### Frontend Error Handling

- Network errors: Retry with exponential backoff
- Authentication errors: Redirect to login
- Validation errors: Display inline
- Server errors: Show user-friendly message
- Global error boundary for React errors

### Backend Error Handling

- Validation errors: Return 400 with details
- Authentication errors: Return 401
- Authorization errors: Return 403
- Not found errors: Return 404
- Server errors: Return 500 (log details, don't expose)
- Consistent error response format

## Dependencies

### Frontend Dependencies

**Required Packages** (all packages will be installed with latest versions automatically):

**Dependencies:**

- next
- react
- react-dom
- better-auth
- @tanstack/react-query
- tailwindcss
- typescript
- @radix-ui/react-slot
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-select
- @radix-ui/react-label
- class-variance-authority
- clsx
- tailwind-merge
- lucide-react

**Dev Dependencies:**

- @testing-library/react
- @testing-library/jest-dom
- jest
- playwright
- msw
- @types/node
- @types/react
- @types/react-dom
- autoprefixer
- postcss

**Package Manager**: pnpm

**Installation Commands**:

```bash
# Create Next.js project (automatically uses latest version)
pnpm create next-app@latest

# Install all dependencies (automatically uses latest versions from package.json)
pnpm install

# Add new dependency (automatically installs latest version)
pnpm add <package-name>

# Add dev dependency (automatically installs latest version)
pnpm add -D <package-name>

# Run scripts
pnpm dev
pnpm build
pnpm test
```

**Note**: shadcn/ui is installed via CLI (`pnpm dlx shadcn-ui@latest init`) which adds components to the project. The above dependencies are the core packages that shadcn/ui components typically use (Radix UI primitives, class-variance-authority, clsx, tailwind-merge, lucide-react for icons).

### Backend Dependencies

**Package Manager**: UV

**Required Packages** (all packages will be installed with latest versions automatically):

**Dependencies:**

- fastapi
- uvicorn[standard]
- sqlmodel
- pydantic
- pydantic-settings
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart
- httpx
- psycopg2-binary

**Dev Dependencies:**

- pytest
- pytest-asyncio
- pytest-cov
- black
- ruff

**Project Configuration** (`pyproject.toml`):

```toml
[project]
name = "todo-backend"
version = "0.1.0"
description = "Todo Backend API"
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlmodel",
    "pydantic",
    "pydantic-settings",
    "python-jose[cryptography]",
    "passlib[bcrypt]",
    "python-multipart",
    "httpx",
    "psycopg2-binary",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "black",
    "ruff",
]
```

**Note**: UV will automatically resolve and install the latest compatible versions of all packages when running `uv sync` or `uv add`.

**Installation Commands**:

```bash
# Initialize UV project (if not already initialized)
uv init

# Install all dependencies (automatically installs latest versions)
uv sync

# Add new dependency (automatically installs latest version)
uv add <package-name>

# Add dev dependency (automatically installs latest version)
uv add --dev <package-name>

# Run application
uv run uvicorn main:app --reload

# Run tests
uv run pytest
```

## Development Workflow

### Package Management

**Frontend (pnpm)**:

- Always use `pnpm` for all frontend dependency management
- Never use `npm` or `yarn`
- All packages are automatically installed with latest versions (no version pinning)
- Commands:
  - `pnpm create next-app@latest` - Create Next.js project with latest version
  - `pnpm install` - Install all dependencies (uses latest versions from package.json)
  - `pnpm add <package>` - Add production dependency (automatically installs latest version)
  - `pnpm add -D <package>` - Add dev dependency (automatically installs latest version)
  - `pnpm remove <package>` - Remove dependency
  - `pnpm dev` - Start development server
  - `pnpm build` - Build for production
  - `pnpm test` - Run tests

**Backend (UV)**:

- Always use `uv` for all backend dependency management
- Never use `pip` or `poetry`
- All packages are automatically installed with latest compatible versions (no version pinning in pyproject.toml)
- Commands:
  - `uv init` - Initialize UV project
  - `uv sync` - Install all dependencies (automatically resolves latest versions)
  - `uv add <package>` - Add production dependency (automatically installs latest version)
  - `uv add --dev <package>` - Add dev dependency (automatically installs latest version)
  - `uv remove <package>` - Remove dependency
  - `uv run <command>` - Run command in UV environment
  - `uv run uvicorn main:app --reload` - Start development server
  - `uv run pytest` - Run tests

### Local Development Setup

1. **Clone repository**
2. **Frontend setup**:
   ```bash
   cd frontend
   # Install all dependencies (automatically uses latest versions)
   pnpm install
   pnpm dev
   ```
3. **Backend setup**:
   ```bash
   cd backend
   # Install all dependencies (automatically resolves latest versions)
   uv sync
   uv run uvicorn main:app --reload
   ```

### Adding New Dependencies

**Frontend**:

```bash
cd frontend
# Add production dependency (automatically installs latest version)
pnpm add <package-name>
# or for dev dependencies (automatically installs latest version)
pnpm add -D <package-name>
```

**Backend**:

```bash
cd backend
# Add production dependency (automatically installs latest version)
uv add <package-name>
# or for dev dependencies (automatically installs latest version)
uv add --dev <package-name>
```

## Risks and Mitigation

| Risk                                   | Impact | Probability | Mitigation                                                             |
| -------------------------------------- | ------ | ----------- | ---------------------------------------------------------------------- |
| JWT integration complexity             | High   | Medium      | Start with simple JWT verification, test thoroughly, document flow     |
| Database connection issues             | High   | Low         | Use connection pooling, implement retry logic, test with Neon early    |
| CORS configuration problems            | Medium | Medium      | Configure CORS early, test in development, document allowed origins    |
| Frontend-backend API mismatch          | Medium | Medium      | Use TypeScript types shared between frontend/backend, contract testing |
| Authentication state management        | Medium | Low         | Use Better Auth's built-in state management, test thoroughly           |
| Deployment configuration errors        | High   | Medium      | Test deployment early, document all environment variables, use CI/CD   |
| Performance issues with large datasets | Low    | Low         | Add pagination if needed, optimize queries, use indexes                |
| Spec-Kit workflow learning curve       | Medium | Medium      | Follow templates closely, reference Phase 1 examples, iterate on specs |

## Success Criteria

### Functional Requirements

- ✅ All 5 Basic Level features implemented and working
- ✅ User authentication (signup, login, logout) functional
- ✅ User isolation enforced (users can't access others' tasks)
- ✅ All CRUD operations work correctly
- ✅ Responsive design works on mobile and desktop
- ✅ Application deployed and accessible

### Quality Requirements

- ✅ 80%+ test coverage achieved
- ✅ All tests passing
- ✅ No critical security vulnerabilities
- ✅ API response times <200ms p95
- ✅ Frontend initial load <2s
- ✅ Code follows constitution standards

### Documentation Requirements

- ✅ README with setup instructions
- ✅ API documentation (Swagger/OpenAPI)
- ✅ Spec-Kit artifacts complete (spec, plan, tasks)
- ✅ CLAUDE.md files in place
- ✅ Deployment guide

### Development Process Requirements

- ✅ Spec-Driven Development followed (no manual coding)
- ✅ All code generated via Claude Code
- ✅ Spec iterations documented
- ✅ TDD approach followed

## Next Steps

1. **Create Detailed Specification** (`spec.md`)

   - User stories for each feature
   - Acceptance criteria
   - UI/UX mockups or descriptions
   - API contract details

2. **Create Data Model Document** (`data-model.md`)

   - Detailed database schema
   - Model relationships
   - Validation rules

3. **Create API Contracts** (`api-contracts.md`)

   - Detailed endpoint specifications
   - Request/response examples
   - Error response formats

4. **Break Down into Tasks** (`tasks.md`)

   - Detailed task list following Spec-Kit format
   - Task dependencies
   - Test requirements for each task

5. **Begin Implementation**
   - Follow TDD approach
   - Use Claude Code for all implementation
   - Iterate on specs as needed
   - Test continuously

## Complexity Tracking

> **No constitution violations identified. This plan follows all principles:**
>
> - Test-First Development: All phases include testing
> - Spec-Driven Development: Full Spec-Kit workflow
> - Simplicity First: Basic Level features only, no over-engineering
> - Code Quality: Type hints, documentation, clean code
> - Incremental Delivery: Phased approach with MVP first

## Notes

- The API endpoint pattern uses `/api/v1/tasks` instead of `/api/{user_id}/tasks` because user_id is extracted from JWT token, avoiding redundancy and improving security.
- Better Auth handles user management, so we only need to create the tasks table with user_id foreign key.
- The monorepo structure enables Spec-Kit Plus to manage specs for both frontend and backend in a unified way.
- All implementation must be done via Claude Code - no manual coding allowed per hackathon requirements.
