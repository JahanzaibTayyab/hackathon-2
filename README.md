# Todo Full-Stack Web Application - Phase 2

A modern, multi-user full-stack todo application built with Next.js, FastAPI, and PostgreSQL.

## 🚀 Quick Start

### Prerequisites

- Node.js (latest LTS)
- Python 3.11+
- pnpm (`npm install -g pnpm`)
- UV (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Neon PostgreSQL account

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd hackathon-2
   ```

2. **Environment Variables**

   - Backend: `.env` file is already configured
   - Frontend: `.env.local` file is already configured
   - Both use the same `BETTER_AUTH_SECRET` for JWT verification

3. **Create Database Tables**

   **Backend (Tasks Table):**

   ```bash
   cd backend
   uv run python scripts/create_tables.py
   ```

   **Frontend (Better Auth Tables):**

   ```bash
   cd frontend
   pnpm db:check  # Verify connection
   # Tables will be created automatically on first use
   ```

4. **Start the Servers**

   **Backend:**

   ```bash
   cd backend
   uv run uvicorn src.main:app --reload --port 8000
   ```

   Backend will run on http://localhost:8000

   **Frontend:**

   ```bash
   cd frontend
   pnpm dev
   ```

   Frontend will run on http://localhost:3000

## Features

- ✅ User authentication (signup, login, logout) with Better Auth
- ✅ Create, read, update, and delete tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Filter tasks by status (all, pending, completed)
- ✅ Sort tasks by created date, title, or updated date
- ✅ User isolation (each user sees only their tasks)
- ✅ Responsive design (mobile and desktop)
- ✅ Modern UI with shadcn/ui components

## Tech Stack

### Frontend

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Authentication**: Better Auth with JWT
- **State Management**: React Query
- **Package Manager**: pnpm

### Backend

- **Framework**: FastAPI (latest)
- **Language**: Python 3.11+
- **ORM**: SQLModel
- **Authentication**: JWT verification
- **Package Manager**: UV

### Database

- **Database**: Neon Serverless PostgreSQL
- **Auth Tables**: Managed by Better Auth (user, session, account, etc.)
- **Task Tables**: Managed by backend (tasks)

## Project Structure

```
hackathon-2/
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/      # App Router pages
│   │   ├── components/  # React components
│   │   ├── lib/      # Utilities and hooks
│   │   └── types/    # TypeScript types
│   ├── auth-schema.ts  # Better Auth database schema
│   └── .env.local    # Environment variables
├── backend/           # FastAPI application
│   ├── src/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── core/     # Core functionality
│   │   └── services/ # Business logic
│   └── .env          # Environment variables
├── specs/            # Specification documents
└── README.md
```

## API Documentation

Once the backend is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Frontend Development

```bash
cd frontend
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm test         # Run tests
pnpm db:check     # Check database connection
```

### Backend Development

```bash
cd backend
uv run uvicorn src.main:app --reload  # Start development server
uv run pytest                         # Run tests
uv run python scripts/create_tables.py  # Create tables
```

## Security

- ✅ Database credentials stored in `.env` files (not committed)
- ✅ JWT tokens signed with shared secret
- ✅ User isolation enforced at database level
- ✅ CORS configured for frontend domain only
- ✅ Input validation on all endpoints

## Environment Variables

### Backend (`.env`)

- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT signing secret (must match frontend)
- `JWT_ALGORITHM` - HS256
- `CORS_ORIGINS` - http://localhost:3000

### Frontend (`.env.local`)

- `DATABASE_URL` - Neon PostgreSQL connection (server-side only)
- `BETTER_AUTH_SECRET` - JWT signing secret (must match backend)
- `NEXT_PUBLIC_BASE_URL` - http://localhost:3000
- `NEXT_PUBLIC_API_URL` - http://localhost:8000

## Testing

### Frontend Tests

```bash
cd frontend
pnpm test              # Unit tests
pnpm test:e2e          # E2E tests (Playwright)
```

### Backend Tests

```bash
cd backend
uv run pytest                    # All tests
uv run pytest tests/unit         # Unit tests only
uv run pytest tests/integration  # Integration tests only
uv run pytest --cov              # With coverage
```

## Deployment

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy

### Backend (Railway/Render/Fly.io)

1. Create a new project
2. Connect your GitHub repository
3. Set environment variables
4. Deploy

## Project Timeline

This project was built following Spec-Driven Development using Claude Code:

1. ✅ Phase 1: Project Setup & Infrastructure
2. ✅ Phase 2: Authentication Foundation
3. ✅ Phase 3: Database Models & Migrations
4. ✅ Phase 4: Backend API Implementation
5. ✅ Phase 5: Frontend API Client & State Management
6. ✅ Phase 6: Frontend UI Components
7. ✅ Phase 7: Frontend Pages & Integration
8. ⏳ Phase 8: Testing & Quality Assurance

## License

MIT

## Contributing

This project was created as part of a hackathon following spec-driven development principles.
