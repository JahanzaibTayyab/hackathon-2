# Todo Full-Stack Web Application

A modern, cloud-native, full-stack todo application built with Next.js, FastAPI, and PostgreSQL. Features AI-powered task management, event-driven architecture with Dapr + Kafka, and Kubernetes deployment.

## Features

- **Task Management**: Create, read, update, delete tasks with advanced filtering
- **AI Chatbot**: Natural language task management using OpenAI Agents SDK
- **Advanced Features**: Priority levels, tags, due dates, recurring tasks
- **Event-Driven**: Real-time events via Dapr pub/sub and Kafka
- **Cloud-Native**: Kubernetes deployment with Helm charts
- **CI/CD**: Automated deployments via GitHub Actions

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER                              │
│                                                                             │
│  ┌─────────────────┐         ┌─────────────────┐         ┌───────────────┐ │
│  │    Frontend     │         │    Backend      │         │    Kafka      │ │
│  │   (Next.js)     │◄───────►│   (FastAPI)     │◄───────►│  (Strimzi)    │ │
│  │                 │   REST  │                 │  Dapr   │               │ │
│  │  ┌───────────┐  │         │  ┌───────────┐  │ PubSub  │  ┌─────────┐  │ │
│  │  │Dapr Sidecar│ │         │  │Dapr Sidecar│ │         │  │ Topics  │  │ │
│  │  └───────────┘  │         │  └───────────┘  │         │  │-events  │  │ │
│  └────────┬────────┘         └────────┬────────┘         │  │-remind  │  │ │
│           │                           │                   │  │-updates │  │ │
│           │                           │                   │  └─────────┘  │ │
│           │                           ▼                   └───────────────┘ │
│           │                  ┌─────────────────┐                            │
│           │                  │   AI Agent      │                            │
│           │                  │ (OpenAI GPT-4)  │                            │
│           │                  │                 │                            │
│           │                  │ Tools:          │                            │
│           │                  │ - add_task      │                            │
│           │                  │ - list_tasks    │                            │
│           │                  │ - complete_task │                            │
│           │                  │ - delete_task   │                            │
│           │                  │ - update_task   │                            │
│           │                  └─────────────────┘                            │
│           │                                                                 │
└───────────┼─────────────────────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────┐
    │     Neon      │
    │  PostgreSQL   │
    │  (Serverless) │
    └───────────────┘
```

### Component Architecture

#### Frontend (Next.js 15)
```
frontend/
├── src/app/                    # App Router
│   ├── (auth)/                 # Auth pages (login, signup)
│   ├── dashboard/              # Main dashboard
│   │   └── chat/               # AI chatbot interface
│   └── api/auth/[...all]/      # Better Auth handler
├── src/components/
│   ├── tasks/                  # Task UI components
│   │   ├── task-list.tsx       # Task listing with filters
│   │   ├── task-item.tsx       # Individual task display
│   │   ├── task-form.tsx       # Create/edit task form
│   │   └── task-filters.tsx    # Filter controls
│   ├── chat/                   # AI Chat components
│   │   ├── chat-interface.tsx  # Main chat UI
│   │   ├── chat-message.tsx    # Message bubbles
│   │   └── chat-input.tsx      # Input with send button
│   └── ui/                     # shadcn/ui components
└── src/lib/
    ├── auth.ts                 # Better Auth server config
    ├── auth-client.ts          # Better Auth client
    ├── api.ts                  # Task API client
    └── hooks/                  # React Query hooks
        ├── use-tasks.ts        # Task CRUD hooks
        └── use-chat.ts         # Chat state hooks
```

#### Backend (FastAPI)
```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry
│   ├── api/v1/
│   │   ├── tasks.py            # Task CRUD endpoints
│   │   ├── chat.py             # AI chat endpoints
│   │   └── events.py           # Dapr event handlers
│   ├── models/
│   │   ├── task.py             # Task SQLModel
│   │   ├── conversation.py     # Conversation model
│   │   └── message.py          # Message model
│   ├── schemas/
│   │   ├── task.py             # Task Pydantic schemas
│   │   └── chat.py             # Chat schemas
│   ├── services/
│   │   ├── task_service.py     # Task business logic
│   │   └── chat_service.py     # AI chat orchestration
│   ├── agent/
│   │   ├── agent.py            # OpenAI agent with tools
│   │   └── model_provider.py   # Model configuration
│   ├── events/
│   │   ├── schemas.py          # CloudEvents schemas
│   │   └── producer.py         # Dapr event publisher
│   └── core/
│       ├── config.py           # Settings management
│       ├── database.py         # Database connection
│       ├── security.py         # JWT verification
│       └── dapr.py             # Dapr client wrapper
└── tests/
    ├── unit/                   # Unit tests
    └── integration/            # Integration tests
```

### Data Flow

#### 1. Authentication Flow
```
User → Frontend → Better Auth → JWT Token
                       ↓
                  PostgreSQL (sessions)
                       ↓
JWT Token → Backend → Verify with BETTER_AUTH_SECRET → User ID
```

#### 2. Task CRUD Flow
```
User Action → Frontend (React Query) → Backend API → PostgreSQL
                                            ↓
                                    Dapr Event Producer
                                            ↓
                                    Kafka (task-events topic)
                                            ↓
                                    Dapr Subscription
                                            ↓
                                    Event Consumer Endpoint
```

#### 3. AI Chat Flow
```
User Message → Chat API → Chat Service
                              ↓
                    Load Conversation History
                              ↓
                    OpenAI Agent (GPT-4o-mini)
                              ↓
                    Execute Tools (add/list/complete/delete/update)
                              ↓
                    Save Messages to PostgreSQL
                              ↓
                    Return Response to User
```

### Event-Driven Architecture

#### Kafka Topics
| Topic | Purpose | Events |
|-------|---------|--------|
| `task-events` | Task lifecycle events | created, updated, deleted, completed |
| `reminders` | Due date notifications | reminder_due, reminder_snoozed |
| `task-updates` | Cross-service sync | sync_requested, sync_completed |

#### Event Schema (CloudEvents)
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/v1/tasks",
  "id": "uuid",
  "time": "2026-01-15T00:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-uuid",
    "title": "Task title",
    "action": "created"
  }
}
```

#### Dapr Pub/Sub Flow
```
Backend Service                    Dapr Sidecar                     Kafka
      │                                 │                              │
      │ POST /publish                   │                              │
      │ (taskpubsub/task-events)        │                              │
      ├────────────────────────────────►│                              │
      │                                 │      Produce Message         │
      │                                 ├─────────────────────────────►│
      │                                 │                              │
      │                                 │      Consume Message         │
      │                                 │◄─────────────────────────────┤
      │ POST /api/v1/events/tasks       │                              │
      │◄────────────────────────────────┤                              │
      │                                 │                              │
```

---

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
   cp .env.example .env  # Configure environment variables
   uv sync
   uv run python scripts/create_tables.py
   uv run uvicorn src.main:app --reload --port 8000
   ```

3. **Frontend**
   ```bash
   cd frontend
   cp .env.example .env.local  # Configure environment variables
   pnpm install
   pnpm dev
   ```

Access the app at http://localhost:3000

---

## Kubernetes Deployment (Dapr + Kafka)

### Prerequisites

```bash
# Install Minikube
brew install minikube

# Install kubectl
brew install kubectl

# Install Helm
brew install helm

# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
# Or: brew install dapr/tap/dapr-cli
```

### Automated Deployment

Run the setup script to deploy everything:

```bash
./scripts/setup-dapr-kafka.sh --deploy-app
```

### Manual Deployment Steps

#### Step 1: Start Minikube
```bash
minikube start --cpus=4 --memory=7168 --driver=docker
minikube addons enable metrics-server
```

#### Step 2: Install Dapr
```bash
dapr init -k --wait
dapr status -k
```

#### Step 3: Install Strimzi Kafka Operator
```bash
kubectl create namespace kafka
kubectl create -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka
kubectl wait deployment/strimzi-cluster-operator \
    --for=condition=available \
    --timeout=300s \
    -n kafka
```

#### Step 4: Deploy Kafka Cluster (KRaft Mode)
```bash
kubectl apply -f helm-chart/kafka/kafka-cluster.yaml
kubectl wait kafka/todo-kafka \
    --for=condition=Ready \
    --timeout=600s \
    -n kafka
```

#### Step 5: Create Kafka Topics
```bash
kubectl apply -f helm-chart/kafka/topics.yaml
kubectl get kafkatopics -n kafka
```

#### Step 6: Deploy Dapr Components
```bash
# Configuration (disable mTLS for local dev)
kubectl apply -f helm-chart/dapr-components/appconfig.yaml

# Pub/Sub component (Kafka)
kubectl apply -f helm-chart/dapr-components/pubsub.yaml

# Subscriptions (route events to endpoints)
kubectl apply -f helm-chart/dapr-components/subscription.yaml
```

#### Step 7: Build Docker Images
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

#### Step 8: Create Secrets
```bash
kubectl create secret generic todo-secrets \
  --from-literal=database-url='postgresql://user:pass@host/db?sslmode=require' \
  --from-literal=auth-secret='your-better-auth-secret' \
  --from-literal=openai-api-key='sk-your-openai-key'
```

#### Step 9: Deploy Application with Helm
```bash
helm upgrade --install todo-release ./helm-chart/todo-app \
    --set dapr.enabled=true \
    --set kafka.enabled=true \
    --wait \
    --timeout 300s
```

#### Step 10: Access the Application

**On macOS (Docker driver):**
```bash
# Terminal 1: Start tunnel
minikube tunnel

# Terminal 2: Access app
open http://localhost:30080
```

**On Linux:**
```bash
open http://$(minikube ip):30080
```

### Verify Deployment

```bash
# Check all pods
kubectl get pods -A

# Check application pods (should show 2/2 for Dapr sidecar)
kubectl get pods -l app.kubernetes.io/name=todo-app

# Check Dapr status
dapr status -k

# Check Kafka topics
kubectl get kafkatopics -n kafka

# View Dapr dashboard
dapr dashboard -k
```

### Monitor Kafka Events

```bash
# Watch task events
kubectl exec -it todo-kafka-dual-role-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

### Useful Commands

```bash
# View frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -f

# View backend logs
kubectl logs -l app.kubernetes.io/component=backend -f

# View Dapr sidecar logs
kubectl logs -l app.kubernetes.io/component=backend -c daprd -f

# Restart deployments
kubectl rollout restart deployment todo-release-todo-app-backend
kubectl rollout restart deployment todo-release-todo-app-frontend

# Uninstall
helm uninstall todo-release
```

---

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
- **AI**: OpenAI Agents SDK (GPT-4o-mini)
- **Events**: Dapr pub/sub

### Infrastructure
- **Database**: Neon PostgreSQL (serverless)
- **Message Broker**: Apache Kafka (Strimzi with KRaft)
- **Service Mesh**: Dapr 1.16
- **Orchestration**: Kubernetes (Minikube/AKS)
- **CI/CD**: GitHub Actions

---

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

### Event Endpoints (`/api/v1/events`) - Dapr Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /events/tasks | Handle task events |
| POST | /events/reminders | Handle reminder events |
| POST | /events/task-updates | Handle sync events |

---

## Development

### Frontend
```bash
cd frontend
pnpm dev              # Development server
pnpm build            # Production build
pnpm test             # Jest unit tests
pnpm test:e2e         # Playwright E2E tests
pnpm test:coverage    # Coverage report
```

### Backend
```bash
cd backend
uv run uvicorn src.main:app --reload  # Dev server
uv run pytest                          # All tests
uv run pytest --cov                    # With coverage
uv run ruff check src                  # Lint
```

---

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

---

## Project Phases

1. ✅ **Phase 1**: In-Memory Console App
2. ✅ **Phase 2**: Full-Stack Web (Next.js + FastAPI)
3. ✅ **Phase 3**: AI Chatbot (OpenAI Agents SDK)
4. ✅ **Phase 4**: Kubernetes Deployment (Helm)
5. ✅ **Phase 5**: Cloud Deployment (Dapr + Kafka + CI/CD)

---

## License

MIT
