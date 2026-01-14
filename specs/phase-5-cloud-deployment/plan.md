# Phase V: Advanced Cloud Deployment - Plan

## HOW - Architecture, Strategy & Implementation Approach

**Phase**: Phase V - Advanced Cloud Deployment
**From Specification**: spec.md
**Status**: Plan Approved

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Cloud Kubernetes Cluster                           │
│                         (Azure AKS / GKE / Oracle OKE)                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           Ingress Controller                         │    │
│  │                    (External Load Balancer + TLS)                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                        │
│                                     ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Frontend Service                            │    │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │    │
│  │  │  Frontend   │    │  Frontend   │    │  Frontend   │              │    │
│  │  │    Pod      │    │    Pod      │    │    Pod      │              │    │
│  │  │  ┌───────┐  │    │  ┌───────┐  │    │  ┌───────┐  │              │    │
│  │  │  │ Dapr  │  │    │  │ Dapr  │  │    │  │ Dapr  │  │              │    │
│  │  │  │Sidecar│  │    │  │Sidecar│  │    │  │Sidecar│  │              │    │
│  │  │  └───────┘  │    │  └───────┘  │    │  └───────┘  │              │    │
│  │  └─────────────┘    └─────────────┘    └─────────────┘              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                        │
│                                     │ Dapr Service Invocation               │
│                                     ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Backend Service                             │    │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │    │
│  │  │  Backend    │    │  Backend    │    │  Backend    │              │    │
│  │  │    Pod      │    │    Pod      │    │    Pod      │              │    │
│  │  │  ┌───────┐  │    │  ┌───────┐  │    │  ┌───────┐  │              │    │
│  │  │  │ Dapr  │──┼────┼──│ Dapr  │──┼────┼──│ Dapr  │──┼──────┐       │    │
│  │  │  │Sidecar│  │    │  │Sidecar│  │    │  │Sidecar│  │      │       │    │
│  │  │  └───────┘  │    │  └───────┘  │    │  └───────┘  │      │       │    │
│  │  └─────────────┘    └─────────────┘    └─────────────┘      │       │    │
│  └─────────────────────────────────────────────────────────────┼───────┘    │
│                                                                 │            │
│  ┌──────────────────────────────────────────────────────────────┼───────┐   │
│  │                    Dapr Pub/Sub (Kafka)                       │       │   │
│  │                                                               ▼       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │  task-events    │  │    reminders    │  │  task-updates   │       │   │
│  │  │     Topic       │  │      Topic      │  │     Topic       │       │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Dapr Control Plane                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ operator │ │ sidecar  │ │ sentry   │ │placement │ │dashboard │   │   │
│  │  │          │ │ injector │ │ (mTLS)   │ │          │ │(optional)│   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                              │                              │
                              │                              │
              ┌───────────────┴───────────────┐              │
              ▼                               ▼              ▼
     ┌─────────────────┐             ┌─────────────────┐  ┌─────────────────┐
     │ Neon PostgreSQL │             │ Redpanda Cloud  │  │    OpenAI API   │
     │   (External)    │             │ (Managed Kafka) │  │   (External)    │
     └─────────────────┘             └─────────────────┘  └─────────────────┘
```

### 1.2 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Event Flow Diagram                                │
│                                                                              │
│  ┌───────────┐    HTTP     ┌───────────┐    Dapr      ┌───────────┐        │
│  │  Browser  │───────────▶ │ Frontend  │───────────▶  │  Backend  │        │
│  │           │◀─────────── │           │◀───────────  │           │        │
│  └───────────┘             └───────────┘              └─────┬─────┘        │
│                                                              │              │
│                                                              │ Task CRUD    │
│                                                              ▼              │
│                                                        ┌───────────┐        │
│                                                        │ PostgreSQL│        │
│                                                        └───────────┘        │
│                                                              │              │
│                                                              │ Publish      │
│                                                              ▼              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Kafka Topics (via Dapr)                      │   │
│  │                                                                      │   │
│  │   task-events ──────▶ Analytics/Logging Consumer                    │   │
│  │                                                                      │   │
│  │   reminders ────────▶ Notification Service                          │   │
│  │                                                                      │   │
│  │   task-updates ─────▶ WebSocket Server (real-time UI updates)       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Backend Service Updates

**New Modules**:

```
backend/
├── src/
│   ├── api/v1/
│   │   └── tasks.py           # Updated with advanced features
│   ├── models/
│   │   └── task.py            # Updated schema
│   ├── schemas/
│   │   └── task.py            # New fields
│   ├── services/
│   │   ├── task_service.py    # Updated business logic
│   │   ├── event_service.py   # NEW: Kafka event publishing
│   │   └── reminder_service.py # NEW: Reminder logic
│   ├── events/
│   │   ├── __init__.py
│   │   ├── producer.py        # Dapr pub/sub wrapper
│   │   ├── consumer.py        # Event handlers
│   │   └── schemas.py         # Event schemas
│   └── core/
│       └── dapr.py            # NEW: Dapr client setup
```

**Task Model Updates**:

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str
    title: str
    description: str | None = None
    completed: bool = False
    # NEW FIELDS
    due_date: datetime | None = None
    priority: str = "medium"  # low, medium, high, urgent
    tags: list[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    recurrence_pattern: dict | None = Field(default=None, sa_column=Column(JSON))
    next_occurrence: datetime | None = None
    reminder_sent: bool = False
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.2 Frontend Updates

**New Components**:

```
frontend/
├── src/
│   ├── components/
│   │   └── tasks/
│   │       ├── task-form.tsx         # Updated with new fields
│   │       ├── task-item.tsx         # Updated display
│   │       ├── task-filters.tsx      # NEW: Advanced filtering
│   │       ├── task-search.tsx       # NEW: Search component
│   │       ├── date-picker.tsx       # NEW: Due date picker
│   │       ├── priority-select.tsx   # NEW: Priority dropdown
│   │       ├── tag-input.tsx         # NEW: Tag management
│   │       └── recurrence-picker.tsx # NEW: Recurrence config
│   ├── lib/
│   │   └── hooks/
│   │       └── use-tasks.ts          # Updated queries
```

### 2.3 Dapr Components

**pubsub.yaml**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-secrets
        key: brokers
    - name: consumerGroup
      value: "todo-app-consumer"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
```

**statestore.yaml**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
```

**subscription.yaml**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
spec:
  pubsubname: taskpubsub
  topic: task-events
  route: /events/tasks
  scopes:
    - backend
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminders-sub
spec:
  pubsubname: taskpubsub
  topic: reminders
  route: /events/reminders
  scopes:
    - backend
```

---

## 3. Implementation Strategy

### 3.1 Phase V Sub-Phases

```
┌────────────────────────────────────────────────────────────────────────┐
│                         Phase V Implementation                          │
│                                                                         │
│   Part A: Advanced Features & Kafka          Part B: Local Dapr        │
│   ┌─────────────────────────────────┐       ┌─────────────────────┐   │
│   │ 1. Database schema migration     │       │ 1. Dapr on Minikube │   │
│   │ 2. Backend API updates           │       │ 2. Strimzi Kafka    │   │
│   │ 3. Frontend UI components        │──────▶│ 3. Dapr components  │   │
│   │ 4. Search & filter logic         │       │ 4. Integration test │   │
│   │ 5. Recurring task logic          │       │ 5. Local validation │   │
│   │ 6. Event publishing setup        │       └──────────┬──────────┘   │
│   └─────────────────────────────────┘                   │              │
│                                                          ▼              │
│                              Part C: Cloud Deployment                   │
│                              ┌─────────────────────────────────┐       │
│                              │ 1. Cloud cluster setup           │       │
│                              │ 2. Container registry            │       │
│                              │ 3. Managed Kafka (Redpanda)      │       │
│                              │ 4. Dapr on cloud                 │       │
│                              │ 5. CI/CD pipeline                │       │
│                              │ 6. Production deployment         │       │
│                              │ 7. Monitoring & observability    │       │
│                              └─────────────────────────────────┘       │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Part A: Advanced Features Implementation Order

1. **Database Migration** (First)
   - Add new columns to tasks table
   - No breaking changes to existing data
   - Create migration script

2. **Backend API Updates**
   - Update Pydantic schemas
   - Update SQLModel
   - Update CRUD operations
   - Add filtering, sorting, search logic

3. **Frontend Components**
   - Priority selector
   - Due date picker
   - Tag input
   - Recurrence picker
   - Filter panel
   - Search bar
   - Sort dropdown

4. **Recurring Task Logic**
   - Recurrence pattern parsing
   - Next occurrence calculation
   - Auto-creation on completion

5. **Reminder System**
   - Due date check logic
   - Reminder event generation
   - In-app notification display

6. **Event Publishing**
   - Dapr client setup
   - Event schemas
   - Publish on task CRUD
   - Consumer endpoints

### 3.3 Part B: Local Dapr Deployment

1. **Minikube Setup**
   ```bash
   minikube start --cpus=6 --memory=12288 --driver=docker
   ```

2. **Dapr Installation**
   ```bash
   dapr init -k
   kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system
   ```

3. **Kafka via Strimzi**
   ```bash
   kubectl create namespace kafka
   kubectl apply -f strimzi-operator.yaml -n kafka
   kubectl apply -f kafka-cluster.yaml -n kafka
   ```

4. **Dapr Components**
   ```bash
   kubectl apply -f dapr-components/pubsub.yaml
   kubectl apply -f dapr-components/statestore.yaml
   kubectl apply -f dapr-components/subscription.yaml
   ```

5. **Application Deployment**
   - Update Helm chart for Dapr annotations
   - Deploy with Dapr sidecars
   - Verify event flow

### 3.4 Part C: Cloud Deployment

**Cloud Provider Decision**: Azure AKS (recommended for Dapr support)

1. **Infrastructure Setup**
   ```bash
   # Create resource group
   az group create --name todo-app-rg --location eastus

   # Create AKS cluster
   az aks create --resource-group todo-app-rg \
     --name todo-app-aks \
     --node-count 3 \
     --enable-managed-identity \
     --generate-ssh-keys
   ```

2. **Container Registry**
   ```bash
   az acr create --resource-group todo-app-rg \
     --name todoappacr \
     --sku Standard
   ```

3. **Managed Kafka (Redpanda Cloud)**
   - Create Redpanda Cloud account
   - Create cluster
   - Create topics: task-events, reminders, task-updates
   - Get connection credentials

4. **Dapr on AKS**
   ```bash
   az k8s-extension create --cluster-type managedClusters \
     --cluster-name todo-app-aks \
     --resource-group todo-app-rg \
     --name dapr \
     --extension-type Microsoft.Dapr
   ```

5. **CI/CD Pipeline**
   - GitHub Actions workflow
   - Build → Test → Docker Build → Push → Deploy

---

## 4. CI/CD Pipeline Design

### 4.1 Workflow Structure

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Frontend
        run: |
          cd frontend
          pnpm install
          pnpm build
          pnpm test
      - name: Build Backend
        run: |
          cd backend
          uv sync
          uv run pytest

  docker:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Build and Push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/todo-frontend:${{ github.sha }}

      - name: Build and Push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/todo-backend:${{ github.sha }}

  deploy-staging:
    needs: docker
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Staging
        run: |
          helm upgrade --install todo-app ./helm-chart/todo-app \
            --namespace staging \
            --set image.tag=${{ github.sha }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          helm upgrade --install todo-app ./helm-chart/todo-app \
            --namespace production \
            --set image.tag=${{ github.sha }}
```

### 4.2 Secret Management

**GitHub Secrets Required**:
- `AZURE_CREDENTIALS` - Service principal for AKS
- `ACR_LOGIN_SERVER` - Container registry URL
- `ACR_USERNAME` / `ACR_PASSWORD` - Registry credentials
- `KUBECONFIG` - Kubernetes config
- `KAFKA_BROKERS` - Redpanda connection string
- `KAFKA_USERNAME` / `KAFKA_PASSWORD` - SASL credentials

---

## 5. Helm Chart Updates

### 5.1 Dapr Annotations

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend"
        dapr.io/app-port: "3000"
        dapr.io/enable-mtls: "true"
```

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-mtls: "true"
```

### 5.2 New Values

```yaml
# values.yaml additions
dapr:
  enabled: true
  pubsubName: taskpubsub

kafka:
  brokers: ""  # Set via secret
  topics:
    events: task-events
    reminders: reminders
    updates: task-updates

features:
  recurring: true
  reminders: true
  search: true
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Backend**:
- Task model with new fields
- Recurrence pattern calculation
- Event schema validation
- Filter/search logic

**Frontend**:
- New components (date picker, priority, tags)
- Filter state management
- Search debounce

### 6.2 Integration Tests

- Dapr pub/sub round-trip
- Event publishing verification
- Reminder generation
- API with filters/search

### 6.3 E2E Tests

- Full task lifecycle with new fields
- Recurring task creation and completion
- Search and filter functionality
- Cloud deployment smoke tests

---

## 7. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Kafka connectivity issues | Medium | High | Retry logic, DLQ, local fallback |
| Dapr learning curve | Medium | Medium | Use official docs, examples |
| Cloud costs | Low | Medium | Use free tiers, set budgets |
| CI/CD pipeline complexity | Medium | Medium | Start simple, iterate |
| Database migration issues | Low | High | Test migration locally first |

---

## 8. Rollback Strategy

### Application Rollback
```bash
helm rollback todo-app <revision> -n production
```

### Database Rollback
- Keep previous schema compatible
- Feature flags for new features
- Data migration reversible

### Event System Rollback
- Disable Dapr pub/sub
- Fall back to direct API calls
- Feature flag for event publishing

---

## 9. Documentation Plan

| Document | Content | Location |
|----------|---------|----------|
| Architecture | Updated diagrams | docs/architecture.md |
| Kafka Topics | Schema, retention | docs/kafka-topics.md |
| Dapr Components | Configuration | docs/dapr-setup.md |
| CI/CD | Pipeline details | docs/cicd.md |
| Deployment | Cloud setup | docs/cloud-deployment.md |
| Local Dev | Dapr + Kafka local | docs/local-development.md |
| API | Updated endpoints | docs/api.md |

---

## 10. Success Criteria

### Part A Complete When:
- ✅ All advanced features working
- ✅ Database migration successful
- ✅ Frontend UI complete
- ✅ Event publishing working

### Part B Complete When:
- ✅ Dapr running on Minikube
- ✅ Kafka (Strimzi) operational
- ✅ Events flowing through system
- ✅ Full functionality locally

### Part C Complete When:
- ✅ Cloud cluster running
- ✅ CI/CD deploying successfully
- ✅ Application accessible externally
- ✅ All features working in cloud

---

## 11. Approval

**Plan Status**: ✅ Approved
**Ready for Tasks**: Yes
**Next Step**: Create tasks.md
**Approver**: Development Team
**Date**: 2026-01-14

---

**References**:
- Constitution: constitution.md
- Specification: spec.md
- Hackathon PDF: Pages 24-36
- Next: tasks.md (Implementation Tasks)
