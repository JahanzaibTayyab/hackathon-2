# Tasks: Phase 2 - Todo Full-Stack Web Application

**Input**: Design documents from `/specs/phase-2-full-stack-web/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, api-contracts.md

**Tests**: Tests are REQUIRED - following TDD approach (Red-Green-Refactor)

**Organization**: Tasks are grouped by implementation phases to enable systematic development.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo structure**: `frontend/` and `backend/` at repository root
- Frontend paths: `frontend/src/app/`, `frontend/src/components/`, `frontend/src/lib/`
- Backend paths: `backend/src/`, `backend/tests/`

## Phase 1: Project Setup & Infrastructure

**Purpose**: Establish monorepo structure and development environment

- [ ] T001 Create monorepo structure (root directory with frontend/ and backend/ subdirectories)
- [ ] T002 Set up Spec-Kit configuration (`.spec-kit/config.yaml`)
- [ ] T003 Create root CLAUDE.md file
- [ ] T004 [P] Create frontend/CLAUDE.md file
- [ ] T005 [P] Create backend/CLAUDE.md file
- [ ] T006 Install pnpm (if not already installed) for frontend package management
- [ ] T007 Create Next.js project using pnpm (`pnpm create next-app@latest`) in frontend/ directory with TypeScript and Tailwind CSS
- [ ] T008 Install and initialize shadcn/ui (`pnpm dlx shadcn-ui@latest init`) in frontend/
- [ ] T009 Install UV (if not already installed) for backend package management
- [ ] T010 Initialize backend project using UV (`uv init`) in backend/ directory
- [ ] T011 [P] Add FastAPI dependency using UV (`uv add fastapi`)
- [ ] T012 [P] Add SQLModel dependency using UV (`uv add sqlmodel`)
- [ ] T013 [P] Add Pydantic dependency using UV (`uv add pydantic`)
- [ ] T014 [P] Add PyJWT dependency using UV (`uv add python-jose[cryptography]`)
- [ ] T015 [P] Add httpx dependency using UV (`uv add httpx`)
- [ ] T016 [P] Add psycopg2-binary dependency using UV (`uv add psycopg2-binary`)
- [ ] T017 [P] Add pytest as dev dependency using UV (`uv add --dev pytest`)
- [ ] T018 [P] Add pytest-asyncio as dev dependency using UV (`uv add --dev pytest-asyncio`)
- [ ] T019 Set up environment variable management (.env files for frontend and backend)
- [ ] T020 Configure Docker Compose for local development (docker-compose.yml)
- [ ] T021 Set up database connection to Neon PostgreSQL (backend configuration)
- [ ] T022 Create database migration script structure (backend/migrations/)
- [ ] T023 Configure CORS settings in backend (allow frontend origin)
- [ ] T024 Configure security settings (HTTPS, headers) in backend

**Checkpoint**: Monorepo structure ready, both frontend and backend can start locally, database connection established

---

## Phase 2: Authentication Foundation

**Purpose**: Implement user authentication with Better Auth and JWT

**⚠️ CRITICAL**: Authentication must be complete before any user story implementation can begin

### Tests for Authentication (REQUIRED - TDD)

- [ ] T025 [P] [US1] Unit test for JWT token verification in backend/tests/unit/test_auth.py
- [ ] T026 [P] [US1] Integration test for login flow in backend/tests/integration/test_auth.py
- [ ] T027 [P] [US1] Frontend unit test for login page in frontend/src/app/login/**tests**/
- [ ] T028 [P] [US1] Frontend unit test for signup page in frontend/src/app/signup/**tests**/

### Implementation for Authentication

- [ ] T029 [US1] Install Better Auth using pnpm (`pnpm add better-auth@latest`) in frontend/
- [ ] T030 [US1] Configure Better Auth with JWT plugin in frontend/src/lib/auth.ts
- [ ] T031 [US1] Create login page component in frontend/src/app/login/page.tsx using shadcn/ui form components
- [ ] T032 [US1] Create signup page component in frontend/src/app/signup/page.tsx using shadcn/ui form components
- [ ] T033 [US1] Implement JWT verification middleware in backend/src/middleware/auth.py
- [ ] T034 [US1] Create user extraction dependency in backend/src/dependencies/auth.py
- [ ] T035 [US1] Configure shared secret (`BETTER_AUTH_SECRET`) in environment variables
- [ ] T036 [US1] Implement logout functionality in frontend (clear session, redirect)
- [ ] T037 [US1] Add protected route wrapper in frontend/src/components/auth/ProtectedRoute.tsx
- [ ] T038 [US1] Test authentication flow end-to-end (signup → login → access protected route)

**Checkpoint**: Users can sign up, log in, JWT tokens are issued and verified, protected routes work correctly

---

## Phase 3: Database Models & Migrations

**Purpose**: Define and create database schema

**⚠️ CRITICAL**: Database schema must be complete before API implementation

### Tests for Database Models (REQUIRED - TDD)

- [ ] T039 [P] Unit test for Task SQLModel in backend/tests/unit/test_models.py
- [ ] T040 [P] Unit test for database connection in backend/tests/unit/test_db.py
- [ ] T041 [P] Integration test for Task CRUD operations in backend/tests/integration/test_task_crud.py

### Implementation for Database Models

- [ ] T042 Create SQLModel Task model in backend/src/models/task.py
- [ ] T043 Create database connection utility in backend/src/db/connection.py
- [ ] T044 Create database migration script in backend/migrations/001_create_tasks_table.py
- [ ] T045 Run initial migration on Neon database
- [ ] T046 Create Pydantic schemas for API (TaskCreate, TaskUpdate, TaskResponse, TaskComplete) in backend/src/schemas/task.py
- [ ] T047 Add database indexes (user_id, completed, created_at) in migration script
- [ ] T048 Test database operations (create, read, update, delete) manually
- [ ] T049 Create database seed script (optional, for testing) in backend/scripts/seed.py

**Checkpoint**: Database schema created, models defined and tested, migration scripts ready

---

## Phase 4: Backend API Implementation

**Purpose**: Implement all REST API endpoints

### Tests for API Endpoints (REQUIRED - TDD)

- [ ] T050 [P] [US2] Integration test for GET /api/v1/tasks in backend/tests/integration/test_api_list.py
- [ ] T051 [P] [US2] Integration test for POST /api/v1/tasks in backend/tests/integration/test_api_create.py
- [ ] T052 [P] [US2] Integration test for GET /api/v1/tasks/{id} in backend/tests/integration/test_api_get.py
- [ ] T053 [P] [US4] Integration test for PUT /api/v1/tasks/{id} in backend/tests/integration/test_api_update.py
- [ ] T054 [P] [US3] Integration test for PATCH /api/v1/tasks/{id}/complete in backend/tests/integration/test_api_complete.py
- [ ] T055 [P] [US5] Integration test for DELETE /api/v1/tasks/{id} in backend/tests/integration/test_api_delete.py
- [ ] T056 [P] Integration test for user isolation (users can't access others' tasks) in backend/tests/integration/test_user_isolation.py
- [ ] T057 [P] Integration test for JWT authentication on all endpoints in backend/tests/integration/test_auth_required.py

### Implementation for API Endpoints

- [ ] T058 Create task service layer (business logic) in backend/src/services/task_service.py
- [ ] T059 [US2] Implement GET /api/v1/tasks endpoint (list with filters) in backend/src/api/v1/routes/tasks.py
- [ ] T060 [US2] Implement POST /api/v1/tasks endpoint (create) in backend/src/api/v1/routes/tasks.py
- [ ] T061 [US2] Implement GET /api/v1/tasks/{id} endpoint (get one) in backend/src/api/v1/routes/tasks.py
- [ ] T062 [US4] Implement PUT /api/v1/tasks/{id} endpoint (update) in backend/src/api/v1/routes/tasks.py
- [ ] T063 [US3] Implement PATCH /api/v1/tasks/{id}/complete endpoint (toggle) in backend/src/api/v1/routes/tasks.py
- [ ] T064 [US5] Implement DELETE /api/v1/tasks/{id} endpoint (delete) in backend/src/api/v1/routes/tasks.py
- [ ] T065 Add request validation using Pydantic schemas in all endpoints
- [ ] T066 Add error handling (400, 401, 404, 500) in backend/src/api/v1/routes/tasks.py
- [ ] T067 Ensure user isolation (filter by user_id from JWT) in all endpoints
- [ ] T068 Test all endpoints with Swagger UI (http://localhost:8000/docs)

**Checkpoint**: All API endpoints implemented, tested, user isolation verified, API documentation generated

---

## Phase 5: Frontend API Client & State Management

**Purpose**: Create frontend infrastructure for API communication

### Tests for API Client (REQUIRED - TDD)

- [ ] T069 [P] Unit test for API client utility in frontend/src/lib/**tests**/api.test.ts
- [ ] T070 [P] Unit test for JWT token management in frontend/src/lib/**tests**/auth.test.ts
- [ ] T071 [P] Unit test for React Query hooks in frontend/src/hooks/**tests**/useTasks.test.ts

### Implementation for API Client

- [ ] T072 Create API client utility in frontend/src/lib/api.ts
- [ ] T073 Implement JWT token management (get from Better Auth, add to headers) in frontend/src/lib/api.ts
- [ ] T074 Add request interceptors for auth headers in frontend/src/lib/api.ts
- [ ] T075 Add error handling and retry logic in frontend/src/lib/api.ts
- [ ] T076 Create TypeScript types for API responses in frontend/src/types/api.ts
- [ ] T077 Install React Query using pnpm (`pnpm add @tanstack/react-query@latest`) in frontend/
- [ ] T078 Set up React Query provider in frontend/src/app/layout.tsx
- [ ] T079 Create custom hook for listing tasks (useTasks) in frontend/src/hooks/useTasks.ts
- [ ] T080 Create custom hook for creating task (useCreateTask) in frontend/src/hooks/useCreateTask.ts
- [ ] T081 Create custom hook for updating task (useUpdateTask) in frontend/src/hooks/useUpdateTask.ts
- [ ] T082 Create custom hook for completing task (useCompleteTask) in frontend/src/hooks/useCompleteTask.ts
- [ ] T083 Create custom hook for deleting task (useDeleteTask) in frontend/src/hooks/useDeleteTask.ts
- [ ] T084 Test API client with mock data (MSW optional)

**Checkpoint**: API client fully functional, token management working, data fetching hooks ready

---

## Phase 6: Frontend UI Components

**Purpose**: Build user interface components using shadcn/ui

### Tests for UI Components (REQUIRED - TDD)

- [ ] T085 [P] [US2] Unit test for TaskItem component in frontend/src/components/tasks/**tests**/TaskItem.test.tsx
- [ ] T086 [P] [US2] Unit test for TaskList component in frontend/src/components/tasks/**tests**/TaskList.test.tsx
- [ ] T087 [P] [US2] Unit test for TaskForm component in frontend/src/components/tasks/**tests**/TaskForm.test.tsx
- [ ] T088 [P] Unit test for TaskFilters component in frontend/src/components/tasks/**tests**/TaskFilters.test.tsx

### Implementation for UI Components

- [ ] T089 Install and configure shadcn/ui with Next.js and Tailwind CSS using pnpm (`pnpm dlx shadcn-ui@latest init`) in frontend/
- [ ] T090 Add shadcn/ui Button component (`pnpm dlx shadcn-ui@latest add button`)
- [ ] T091 Add shadcn/ui Input component (`pnpm dlx shadcn-ui@latest add input`)
- [ ] T092 Add shadcn/ui Card component (`pnpm dlx shadcn-ui@latest add card`)
- [ ] T093 Add shadcn/ui Dialog component (`pnpm dlx shadcn-ui@latest add dialog`)
- [ ] T094 Add shadcn/ui Select component (`pnpm dlx shadcn-ui@latest add select`)
- [ ] T095 Add shadcn/ui Form components (`pnpm dlx shadcn-ui@latest add form`)
- [ ] T096 Add shadcn/ui Skeleton component (`pnpm dlx shadcn-ui@latest add skeleton`)
- [ ] T097 Add shadcn/ui Alert component (`pnpm dlx shadcn-ui@latest add alert`)
- [ ] T098 [US2] Create TaskItem component using shadcn/ui components in frontend/src/components/tasks/TaskItem.tsx
- [ ] T099 [US2] Create TaskList component using shadcn/ui components in frontend/src/components/tasks/TaskList.tsx
- [ ] T100 [US2] Create TaskForm component (create/edit) using shadcn/ui Form components in frontend/src/components/tasks/TaskForm.tsx
- [ ] T101 Create TaskFilters component using shadcn/ui Select/Dropdown components in frontend/src/components/tasks/TaskFilters.tsx
- [ ] T102 Create Dashboard layout with shadcn/ui layout components in frontend/src/components/layout/DashboardLayout.tsx
- [ ] T103 Add loading states using shadcn/ui Skeleton components in TaskList
- [ ] T104 Add error states using shadcn/ui Alert components in TaskList
- [ ] T105 Implement responsive design (shadcn/ui components are responsive by default)
- [ ] T106 Customize shadcn/ui theme to match application design in frontend/src/app/globals.css
- [ ] T107 Add accessibility features (shadcn/ui components are accessible by default, verify ARIA labels)

**Checkpoint**: All UI components created using shadcn/ui, responsive design implemented, accessibility features added

---

## Phase 7: Frontend Pages & Integration

**Purpose**: Connect frontend pages with backend API

### Tests for Frontend Pages (REQUIRED - TDD)

- [ ] T108 [P] [US2] Integration test for dashboard page in frontend/src/app/dashboard/**tests**/page.test.tsx
- [ ] T109 [P] [US2] E2E test for create task workflow in frontend/tests/e2e/create-task.spec.ts
- [ ] T110 [P] [US4] E2E test for update task workflow in frontend/tests/e2e/update-task.spec.ts
- [ ] T111 [P] [US3] E2E test for complete task workflow in frontend/tests/e2e/complete-task.spec.ts
- [ ] T112 [P] [US5] E2E test for delete task workflow in frontend/tests/e2e/delete-task.spec.ts

### Implementation for Frontend Pages

- [ ] T113 [US2] Create dashboard page with task list in frontend/src/app/dashboard/page.tsx
- [ ] T114 [US2] Integrate task creation form with API in frontend/src/app/dashboard/page.tsx
- [ ] T115 [US4] Integrate task update functionality with API in frontend/src/components/tasks/TaskForm.tsx
- [ ] T116 [US5] Integrate task deletion with API in frontend/src/components/tasks/TaskItem.tsx
- [ ] T117 [US3] Integrate task completion toggle with API in frontend/src/components/tasks/TaskItem.tsx
- [ ] T118 Add task filtering UI (status filter) in frontend/src/app/dashboard/page.tsx
- [ ] T119 Add task sorting UI (sort by created, title, updated) in frontend/src/app/dashboard/page.tsx
- [ ] T120 Implement real-time updates (optimistic updates) using React Query in hooks
- [ ] T121 Add success/error notifications using shadcn/ui Toast component in frontend/src/components/ui/toast.tsx
- [ ] T122 Test complete user workflows (signup → login → create → update → complete → delete)

**Checkpoint**: All pages functional, full CRUD operations working, user can complete all workflows

---

## Phase 8: Testing & Quality Assurance

**Purpose**: Comprehensive testing coverage

### Backend Testing

- [ ] T123 Write backend unit tests for models in backend/tests/unit/test_models.py
- [ ] T124 Write backend unit tests for services in backend/tests/unit/test_services.py
- [ ] T125 Write backend integration tests for all API endpoints in backend/tests/integration/
- [ ] T126 Test authentication flows (JWT verification) in backend/tests/integration/test_auth.py
- [ ] T127 Test user isolation scenarios (users can't access others' tasks) in backend/tests/integration/test_user_isolation.py
- [ ] T128 Test error handling (400, 401, 404, 500) in backend/tests/integration/test_errors.py

### Frontend Testing

- [ ] T129 Write frontend unit tests for all components in frontend/src/components/\*\*/**tests**/
- [ ] T130 Write frontend integration tests for pages in frontend/src/app/\*\*/**tests**/
- [ ] T131 Write E2E tests for critical paths using Playwright in frontend/tests/e2e/
- [ ] T132 Test authentication flows (login, signup, logout) in frontend/tests/e2e/auth.spec.ts
- [ ] T133 Test complete user workflows in frontend/tests/e2e/workflows.spec.ts

### Quality Assurance

- [ ] T134 Achieve 80%+ code coverage for backend (run pytest with coverage)
- [ ] T135 Achieve 80%+ code coverage for frontend (run Jest with coverage)
- [ ] T136 Run security audit (check for vulnerabilities in dependencies)
- [ ] T137 Test responsive design on mobile and desktop browsers
- [ ] T138 Test accessibility (keyboard navigation, screen readers)
- [ ] T139 Performance testing (API response times, frontend load times)

**Checkpoint**: 80%+ test coverage achieved, all tests passing, E2E tests covering critical paths

---

## Phase 9: Deployment Preparation

**Purpose**: Prepare for production deployment

- [ ] T140 Configure environment variables for production (frontend and backend)
- [ ] T141 Set up Vercel project for frontend deployment
- [ ] T142 Set up backend hosting (Railway/Render/Fly.io)
- [ ] T143 Configure production database (Neon)
- [ ] T144 Set up CI/CD pipeline (GitHub Actions) with pnpm for frontend and UV for backend
- [ ] T145 Add health check endpoints in backend/src/api/v1/routes/health.py
- [ ] T146 Configure logging and monitoring
- [ ] T147 Set up error tracking (Sentry optional)
- [ ] T148 Create deployment documentation in docs/deployment.md
- [ ] T149 Test production deployment (deploy to staging first)
- [ ] T150 Verify production deployment (test all features in production)

**Checkpoint**: Application deployed to production, CI/CD pipeline working, monitoring in place

---

## Summary

**Total Tasks**: 150 tasks across 9 phases

**Critical Path**:

1. Phase 1: Project Setup (blocks everything)
2. Phase 2: Authentication (blocks all user stories)
3. Phase 3: Database Models (blocks API implementation)
4. Phase 4: Backend API (blocks frontend integration)
5. Phase 5: Frontend API Client (blocks UI integration)
6. Phase 6: Frontend UI Components (blocks pages)
7. Phase 7: Frontend Pages (completes user stories)
8. Phase 8: Testing (quality assurance)
9. Phase 9: Deployment (production readiness)

**Test Coverage Goal**: 80%+ for both frontend and backend

**Success Criteria**: All user stories (US1-US5) fully implemented, tested, and deployed
