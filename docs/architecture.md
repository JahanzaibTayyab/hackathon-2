# Todo Application Architecture

## Overview

The Todo application is a full-stack, cloud-native task management system built with modern technologies and event-driven architecture.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              User Browser                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster (AKS/Minikube)                        │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                              Dapr Control Plane                            │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │  │
│  │  │   Operator   │ │   Sidecar    │ │  Placement   │ │     Sentry       │  │  │
│  │  │              │ │   Injector   │ │    Server    │ │    (mTLS)        │  │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │         Frontend Pod            │  │          Backend Pod                │   │
│  │  ┌─────────────────────────┐    │  │  ┌─────────────────────────┐        │   │
│  │  │     Next.js App         │    │  │  │     FastAPI App         │        │   │
│  │  │     (Port 3000)         │    │  │  │     (Port 8000)         │        │   │
│  │  └─────────────────────────┘    │  │  └───────────┬─────────────┘        │   │
│  │  ┌─────────────────────────┐    │  │  ┌───────────▼─────────────┐        │   │
│  │  │     Dapr Sidecar        │◄───┼──┼──►    Dapr Sidecar         │        │   │
│  │  │     (Port 3500)         │    │  │  │    (Port 3500)          │        │   │
│  │  └─────────────────────────┘    │  │  └───────────┬─────────────┘        │   │
│  └─────────────────────────────────┘  └──────────────┼──────────────────────┘   │
│                                                      │                          │
│  ┌───────────────────────────────────────────────────▼──────────────────────┐   │
│  │                         Kafka Cluster (Strimzi)                           │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐    │   │
│  │  │                        Kafka Broker                               │    │   │
│  │  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐        │    │   │
│  │  │  │  task-events   │ │   reminders    │ │  task-updates  │        │    │   │
│  │  │  │  (3 partitions)│ │  (1 partition) │ │  (3 partitions)│        │    │   │
│  │  │  └────────────────┘ └────────────────┘ └────────────────┘        │    │   │
│  │  └──────────────────────────────────────────────────────────────────┘    │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐    │   │
│  │  │                        Zookeeper                                  │    │   │
│  │  └──────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           External Services                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │   Neon PostgreSQL    │  │     OpenAI API       │  │   Redpanda Cloud     │   │
│  │   (Database)         │  │   (AI Chatbot)       │  │   (Cloud Kafka)      │   │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Components

### Frontend (Next.js 15)

- **Technology**: Next.js with App Router, React 19, TypeScript
- **Authentication**: Better Auth with JWT tokens
- **UI Components**: shadcn/ui, Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Features**:
  - Task CRUD operations
  - Advanced filtering and search
  - Priority and tag management
  - Recurring task support
  - AI-powered chat interface

### Backend (FastAPI)

- **Technology**: FastAPI, Python 3.11+, SQLModel
- **Authentication**: JWT verification (shared secret with frontend)
- **Database**: Neon PostgreSQL (serverless)
- **AI Integration**: OpenAI Agents SDK for chat functionality
- **Features**:
  - RESTful API with automatic OpenAPI documentation
  - Task management with advanced filtering
  - Event publishing via Dapr
  - AI chatbot for natural language task management

### Event System (Dapr + Kafka)

- **Message Broker**: Apache Kafka (Strimzi on K8s / Redpanda Cloud)
- **Event Router**: Dapr pub/sub component
- **Event Types**:
  - Task lifecycle events (created, updated, deleted, completed)
  - Reminder events (due soon, overdue)
  - Real-time sync events

### Infrastructure

- **Container Orchestration**: Kubernetes (Minikube for local, AKS for cloud)
- **Service Mesh**: Dapr with mTLS
- **CI/CD**: GitHub Actions
- **Container Registry**: Azure Container Registry

## Data Flow

### Task Creation Flow

```
1. User creates task in UI
2. Frontend sends POST to /api/v1/tasks
3. Backend validates and stores in PostgreSQL
4. Backend publishes task.created event via Dapr
5. Dapr routes event to Kafka (task-events topic)
6. Event consumer logs/processes event
7. Response returned to frontend
```

### AI Chat Flow

```
1. User sends message in chat
2. Frontend sends POST to /api/v1/chat
3. Backend invokes OpenAI agent
4. Agent determines intent (add, list, complete, delete task)
5. Agent executes tool function
6. Database updated
7. Event published
8. Response returned with action confirmation
```

## Security

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │────►│ Frontend │────►│ Backend  │
└──────────┘     └──────────┘     └──────────┘
      │               │                │
      │  1. Login     │                │
      │──────────────►│                │
      │               │  2. Create     │
      │               │     Session    │
      │               │───────────────►│
      │  3. JWT Token │                │
      │◄──────────────│                │
      │               │                │
      │  4. API Call  │                │
      │  + JWT Header │                │
      │───────────────┼───────────────►│
      │               │                │ 5. Verify JWT
      │               │                │    Extract user_id
      │               │                │
      │  6. Response  │                │
      │◄──────────────┼────────────────│
```

### Security Measures

- JWT tokens with HMAC-SHA256 signing
- mTLS between services via Dapr
- CORS policy enforcement
- User isolation (all tasks scoped to user_id)
- Secret management via Kubernetes secrets

## Deployment Environments

| Environment | Infrastructure | Kafka | Purpose |
|-------------|----------------|-------|---------|
| Local | Minikube | Strimzi | Development |
| Staging | AKS | Redpanda Cloud | Testing |
| Production | AKS | Redpanda Cloud | Live |

## Scalability

- **Horizontal Pod Autoscaling**: 2-5 replicas based on CPU/memory
- **Kafka Partitioning**: task-events (3), task-updates (3)
- **Database**: Neon serverless auto-scales
- **Stateless Services**: Frontend and Backend are stateless

## Monitoring

- **Metrics**: Prometheus scraping via pod annotations
- **Logging**: Structured logging to stdout, aggregated by Azure Monitor
- **Tracing**: Dapr provides distributed tracing
- **Dashboards**: Dapr Dashboard for service mesh visibility
