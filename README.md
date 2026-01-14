# Todo Full-Stack Web Application

A modern, cloud-native, full-stack todo application built with Next.js, FastAPI, and PostgreSQL. Features AI-powered task management, event-driven architecture with Dapr + Kafka, and Kubernetes deployment.

## Features

- **Task Management**: Create, read, update, delete tasks with advanced filtering
- **AI Chatbot**: Natural language task management using OpenAI Agents SDK
- **Advanced Features**: Priority levels, tags, due dates, recurring tasks
- **Event-Driven**: Real-time events via Dapr pub/sub and Kafka
- **Cloud-Native**: Kubernetes deployment with Helm charts
- **CI/CD**: Automated deployments via GitHub Actions

## Quick Start

### Prerequisites

- Node.js 20+ (LTS)
- Python 3.11+
- pnpm (`npm install -g pnpm`)
- UV (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Neon PostgreSQL account

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd hackathon-2
   ```

2. **Backend**
   ```bash
   cd backend
   uv sync
   uv run python scripts/create_tables.py
   uv run uvicorn src.main:app --reload --port 8000
   ```

3. **Frontend**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

Access the app at http://localhost:3000

### Kubernetes Deployment (Minikube)

```bash
# Install prerequisites: minikube, kubectl, helm, dapr CLI

# Run setup script
./scripts/setup-dapr-kafka.sh --deploy-app
```

## Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI**: shadcn/ui, Tailwind CSS
- **Auth**: Better Auth with JWT
- **State**: React Query (TanStack Query)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLModel
- **AI**: OpenAI Agents SDK
- **Events**: Dapr pub/sub

### Infrastructure
- **Database**: Neon PostgreSQL (serverless)
- **Message Broker**: Apache Kafka (Strimzi/Redpanda)
- **Service Mesh**: Dapr
- **Orchestration**: Kubernetes (Minikube/AKS)
- **CI/CD**: GitHub Actions

## Project Structure

```
hackathon-2/
├── frontend/              # Next.js application
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components (tasks, chat, ui)
│   │   └── lib/          # Utilities, hooks, API clients
│   └── .env.local        # Environment variables
├── backend/               # FastAPI application
│   ├── src/
│   │   ├── api/v1/       # API routes (tasks, chat, events)
│   │   ├── models/       # SQLModel database models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic
│   │   ├── agent/        # AI agent (OpenAI)
│   │   ├── events/       # Event schemas and producer
│   │   └── core/         # Config, database, security, Dapr
│   └── .env              # Environment variables
├── helm-chart/            # Kubernetes Helm charts
│   ├── todo-app/         # Application chart
│   ├── kafka/            # Strimzi Kafka configs
│   └── dapr-components/  # Dapr pub/sub configs
├── scripts/               # Setup and deployment scripts
├── docs/                  # Documentation
│   ├── architecture.md   # System architecture
│   ├── kafka-topics.md   # Event schemas
│   ├── dapr-setup.md     # Dapr installation guide
│   └── cicd.md           # CI/CD pipeline docs
└── .github/workflows/     # GitHub Actions CI/CD
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Task Endpoints (`/api/v1/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tasks | List tasks with filtering/sorting |
| POST | /tasks | Create task |
| GET | /tasks/{id} | Get task |
| PUT | /tasks/{id} | Update task |
| PATCH | /tasks/{id}/complete | Toggle completion |
| DELETE | /tasks/{id} | Delete task |
| GET | /tags | Get all user tags |

### Chat Endpoints (`/api/v1/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat | Send message to AI |
| GET | /chat/conversations | List conversations |
| GET | /chat/conversations/{id} | Get conversation |
| DELETE | /chat/conversations/{id} | Delete conversation |

### Event Endpoints (`/api/v1/events`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /events/tasks | Handle task events (Dapr) |
| POST | /events/reminders | Handle reminder events (Dapr) |
| POST | /events/task-updates | Handle sync events (Dapr) |

## Development

### Frontend
```bash
cd frontend
pnpm dev              # Development server
pnpm build            # Production build
pnpm test             # Jest unit tests
pnpm test:e2e         # Playwright E2E tests
```

### Backend
```bash
cd backend
uv run uvicorn src.main:app --reload  # Dev server
uv run pytest                          # All tests
uv run pytest --cov                    # With coverage
uv run ruff check src                  # Lint
```

## Environment Variables

### Backend (`.env`)
```
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000
DAPR_ENABLED=false
```

### Frontend (`.env.local`)
```
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Local (Minikube + Dapr + Kafka)
```bash
./scripts/setup-dapr-kafka.sh --deploy-app
```

### Cloud (Azure AKS)
See [CI/CD Documentation](docs/cicd.md) for GitHub Actions deployment.

## Documentation

- [Architecture](docs/architecture.md) - System design and diagrams
- [Kafka Topics](docs/kafka-topics.md) - Event schemas and topics
- [Dapr Setup](docs/dapr-setup.md) - Dapr installation guide
- [CI/CD](docs/cicd.md) - Pipeline and deployment docs

## Project Phases

1. ✅ Phase 1: In-Memory Console App
2. ✅ Phase 2: Full-Stack Web (Next.js + FastAPI)
3. ✅ Phase 3: AI Chatbot (OpenAI Agents SDK)
4. ✅ Phase 4: Kubernetes Deployment
5. ✅ Phase 5: Cloud Deployment (Dapr + Kafka + CI/CD)

## License

MIT
