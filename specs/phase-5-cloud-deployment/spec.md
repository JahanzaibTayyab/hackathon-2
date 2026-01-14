# Phase V: Advanced Cloud Deployment - Specification

## WHAT - Requirements, User Journeys & Acceptance Criteria

**Phase**: Phase V - Advanced Cloud Deployment
**From Constitution**: constitution.md
**Status**: Specification Approved

---

## 1. User Journeys

### Journey 1: User Managing Advanced Tasks

**Actor**: End User
**Goal**: Manage tasks with advanced features (recurring, due dates, priorities, tags)
**Context**: User needs to organize complex task workflows

**Journey Steps**:

1. **Create Task with Due Date and Priority**
   - User clicks "Add Task"
   - Enters title: "Submit quarterly report"
   - Sets due date: "January 20, 2026"
   - Sets priority: "High"
   - Adds tags: "work", "finance"
   - Saves task

2. **Create Recurring Task**
   - User clicks "Add Task"
   - Enters title: "Weekly team standup"
   - Enables recurrence: "Weekly on Monday"
   - Sets start date
   - Saves task
   - System auto-creates next instance on completion

3. **Search and Filter Tasks**
   - User types "report" in search bar
   - Results filter to matching tasks
   - User clicks "Filter" dropdown
   - Selects priority: "High"
   - Selects tags: "work"
   - Results narrow to matching tasks

4. **Sort Tasks**
   - User clicks "Sort by" dropdown
   - Selects "Due Date (Ascending)"
   - Tasks reorder with earliest due dates first

5. **Receive Due Date Reminder**
   - System detects task due in 24 hours
   - Kafka reminder event published
   - User receives notification (in-app)

**Success Criteria**:
- ✅ Task created with all advanced fields
- ✅ Recurring task generates next instance
- ✅ Search returns relevant results <500ms
- ✅ Filters accurately narrow results
- ✅ Sort correctly orders tasks
- ✅ Reminder delivered within 30 seconds

---

### Journey 2: DevOps Engineer - Cloud Deployment

**Actor**: DevOps Engineer
**Goal**: Deploy application to cloud Kubernetes with full event-driven architecture
**Context**: Application ready for production cloud deployment

**Journey Steps**:

1. **Set Up Cloud Infrastructure**
   - Create Kubernetes cluster (AKS/GKE/OKE)
   - Configure container registry
   - Set up managed Kafka (Redpanda Cloud)
   - Configure DNS and networking

2. **Install Dapr on Cloud Cluster**
   - Add Dapr Helm repository
   - Install Dapr control plane
   - Configure Dapr components for cloud

3. **Configure CI/CD Pipeline**
   - Create GitHub Actions workflow
   - Configure secrets in GitHub
   - Set up deployment stages
   - Configure approval gates

4. **Deploy Application**
   - Push to main branch
   - CI/CD triggers automatically
   - Images built and pushed to registry
   - Helm chart deployed to cluster
   - Dapr sidecars injected

5. **Verify Deployment**
   - Check pod status
   - Verify Dapr components
   - Test Kafka event flow
   - Access application via external URL

**Success Criteria**:
- ✅ Cloud cluster operational
- ✅ CI/CD deploys without manual intervention
- ✅ All pods running with Dapr sidecars
- ✅ Kafka events flowing through Dapr
- ✅ Application accessible externally

---

### Journey 3: Developer - Local Dapr Development

**Actor**: Developer
**Goal**: Run and test application locally with Dapr and Kafka
**Context**: Need to develop and test event-driven features locally

**Journey Steps**:

1. **Set Up Local Environment**
   - Start Minikube with adequate resources
   - Install Dapr on Minikube
   - Deploy Kafka using Strimzi operator

2. **Configure Dapr Components**
   - Create pubsub.yaml for Kafka
   - Create statestore.yaml
   - Create secretstore.yaml
   - Apply components to cluster

3. **Run Application with Dapr**
   - Deploy frontend with Dapr sidecar
   - Deploy backend with Dapr sidecar
   - Verify inter-service communication

4. **Test Event Flow**
   - Create task (triggers task-events topic)
   - Verify event in Kafka
   - Test reminder scheduling
   - Verify state management

**Success Criteria**:
- ✅ Dapr running on Minikube
- ✅ Kafka operational via Strimzi
- ✅ Events published and consumed
- ✅ State management working
- ✅ Full feature set testable locally

---

### Journey 4: System - Event-Driven Reminders

**Actor**: System (Automated)
**Goal**: Send reminders for tasks with approaching due dates
**Context**: Automated background process for reminder notifications

**Journey Steps**:

1. **Scheduler Triggers Check**
   - Dapr Jobs API triggers daily check
   - Backend queries tasks with due dates within 24 hours

2. **Generate Reminder Events**
   - For each task due soon:
     - Create reminder message
     - Publish to 'reminders' topic via Dapr

3. **Process Reminder Events**
   - Notification service consumes 'reminders' topic
   - Creates in-app notification for user
   - Optionally sends email/push notification

4. **Update Task Status**
   - Mark reminder as sent
   - Publish event to 'task-updates' topic

**Success Criteria**:
- ✅ Scheduler runs reliably
- ✅ Reminders generated for due tasks
- ✅ Events processed asynchronously
- ✅ No duplicate reminders
- ✅ Latency <30 seconds

---

## 2. Functional Requirements

### FR-1: Advanced Task Features

**FR-1.1: Due Dates**
- **Description**: Tasks can have optional due dates
- **Requirements**:
  - Due date field (datetime)
  - Date picker in UI
  - Display relative time (e.g., "Due in 2 days")
  - Overdue visual indicator
  - Filter by due date range
  - Sort by due date
- **Database**: `due_date TIMESTAMP NULL`
- **Validation**: Due date cannot be in the past on creation

**FR-1.2: Recurring Tasks**
- **Description**: Tasks can recur on a schedule
- **Requirements**:
  - Recurrence patterns: daily, weekly, monthly, yearly
  - Custom intervals (e.g., every 3 days)
  - Weekly: select days of week
  - Monthly: select day of month
  - End date or occurrence count (optional)
  - On completion, create next instance
  - Visual indicator for recurring tasks
- **Database**: `recurrence_pattern JSON`, `next_occurrence TIMESTAMP`
- **Schema**:
  ```json
  {
    "type": "weekly",
    "interval": 1,
    "daysOfWeek": [1, 3, 5],
    "endDate": "2026-12-31"
  }
  ```

**FR-1.3: Priorities**
- **Description**: Tasks have priority levels
- **Requirements**:
  - Levels: Low, Medium, High, Urgent
  - Visual indicators (color/icon)
  - Default: Medium
  - Filter by priority
  - Sort by priority
- **Database**: `priority VARCHAR(10) DEFAULT 'medium'`

**FR-1.4: Tags**
- **Description**: Tasks can have multiple tags
- **Requirements**:
  - Comma-separated or multi-select
  - Auto-suggest existing tags
  - Create new tags inline
  - Tag colors (optional)
  - Filter by tags (include/exclude)
  - Tag management UI
- **Database**: `tags VARCHAR(500)` or separate tags table
- **API**: Tags as array in request/response

**FR-1.5: Search**
- **Description**: Full-text search across tasks
- **Requirements**:
  - Search in title and description
  - Real-time results (debounced)
  - Highlight matching terms
  - Case-insensitive
  - Partial word matching
- **Implementation**: PostgreSQL full-text search or ILIKE

**FR-1.6: Advanced Filtering**
- **Description**: Filter tasks by multiple criteria
- **Requirements**:
  - Status: pending, completed, all
  - Priority: Low, Medium, High, Urgent
  - Tags: include/exclude
  - Due date range: today, week, month, custom
  - Combine multiple filters (AND logic)
  - Save filter presets (optional)
- **API Query Params**:
  ```
  GET /tasks?status=pending&priority=high&tags=work,urgent&due_before=2026-01-20
  ```

**FR-1.7: Sorting**
- **Description**: Sort tasks by various fields
- **Requirements**:
  - Sort fields: created_at, due_date, priority, title
  - Order: ascending, descending
  - Secondary sort (optional)
  - Persist sort preference per user (optional)
- **API Query Params**: `?sort_by=due_date&order=asc`

---

### FR-2: Kafka Event System

**FR-2.1: Task Events Topic**
- **Description**: Events for all task state changes
- **Topic**: `task-events`
- **Events**:
  - `task.created`
  - `task.updated`
  - `task.completed`
  - `task.deleted`
- **Schema**:
  ```json
  {
    "eventType": "task.created",
    "taskId": "uuid",
    "userId": "uuid",
    "timestamp": "ISO-8601",
    "data": { "title": "...", "priority": "..." }
  }
  ```
- **Partitioning**: By `userId` for ordering
- **Retention**: 7 days

**FR-2.2: Reminders Topic**
- **Description**: Due date reminder notifications
- **Topic**: `reminders`
- **Events**:
  - `reminder.due_soon` (24h before)
  - `reminder.overdue`
- **Schema**:
  ```json
  {
    "eventType": "reminder.due_soon",
    "taskId": "uuid",
    "userId": "uuid",
    "dueDate": "ISO-8601",
    "title": "..."
  }
  ```
- **Retention**: 24 hours

**FR-2.3: Task Updates Topic**
- **Description**: Real-time task updates for UI refresh
- **Topic**: `task-updates`
- **Purpose**: Frontend subscriptions for live updates
- **Events**: Same as task-events, filtered for UI
- **Retention**: 1 hour

---

### FR-3: Dapr Integration

**FR-3.1: Pub/Sub Component**
- **Description**: Kafka abstraction via Dapr
- **Component**: pubsub.yaml
- **Configuration**:
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
        value: "kafka-broker:9092"
      - name: consumerGroup
        value: "todo-app"
  ```
- **Usage**: Publish/subscribe via Dapr HTTP/SDK

**FR-3.2: State Store Component**
- **Description**: Distributed state management
- **Component**: statestore.yaml
- **Use Cases**:
  - User session state
  - Caching hot data
  - Distributed locks
- **Configuration**: PostgreSQL or Redis backend

**FR-3.3: Service Invocation**
- **Description**: Service-to-service communication
- **Usage**: Frontend → Backend via Dapr
- **Benefits**:
  - mTLS automatic
  - Retries built-in
  - Service discovery
- **Invocation**: `http://localhost:3500/v1.0/invoke/backend/method/tasks`

**FR-3.4: Jobs API**
- **Description**: Scheduled task execution
- **Use Cases**:
  - Daily reminder checks
  - Recurring task generation
  - Cleanup jobs
- **Configuration**: Cron-based schedules
- **Implementation**: Dapr Jobs API (if available) or external scheduler

**FR-3.5: Secrets Management**
- **Description**: Centralized secret storage
- **Component**: secretstore.yaml
- **Secrets**:
  - DATABASE_URL
  - OPENAI_API_KEY
  - BETTER_AUTH_SECRET
- **Integration**: Kubernetes secrets or cloud secret manager

---

### FR-4: Cloud Deployment

**FR-4.1: Kubernetes Cluster**
- **Description**: Managed Kubernetes on cloud provider
- **Options**:
  - Azure AKS
  - Google Cloud GKE
  - Oracle Cloud OKE
- **Requirements**:
  - 3+ nodes
  - Auto-scaling enabled
  - Load balancer
  - Ingress controller

**FR-4.2: Container Registry**
- **Description**: Private container registry
- **Options**:
  - Azure ACR
  - Google GCR/Artifact Registry
  - Oracle OCIR
- **Requirements**:
  - Vulnerability scanning
  - Image retention policy
  - Access from Kubernetes

**FR-4.3: Managed Kafka**
- **Description**: Kafka cluster for event streaming
- **Recommended**: Redpanda Cloud (managed)
- **Alternative**: Strimzi operator (self-managed)
- **Requirements**:
  - 3 brokers minimum
  - Topic auto-creation disabled
  - SASL authentication
  - TLS encryption

**FR-4.4: CI/CD Pipeline**
- **Description**: Automated build and deployment
- **Platform**: GitHub Actions
- **Stages**:
  1. Build: Compile, test, lint
  2. Docker: Build and push images
  3. Deploy Staging: Helm upgrade
  4. Test: Integration tests
  5. Deploy Production: Manual approval, Helm upgrade
- **Triggers**: Push to main, PRs

**FR-4.5: Observability**
- **Description**: Monitoring, logging, tracing
- **Components**:
  - Metrics: Prometheus + Grafana
  - Logs: Cloud provider logging
  - Traces: Dapr distributed tracing
- **Alerts**: Pod restarts, error rates, latency

---

## 3. Non-Functional Requirements

### NFR-1: Performance

| Metric | Requirement | Critical Threshold |
|--------|-------------|-------------------|
| API response time (95th) | <200ms | 500ms |
| Search latency | <500ms | 1s |
| Kafka event publish | <50ms | 200ms |
| Kafka event E2E | <500ms | 2s |
| Page load time | <2s | 3s |
| CI/CD pipeline | <10 min | 15 min |

### NFR-2: Reliability
- 99.9% uptime target
- Zero data loss for events
- Automatic recovery from pod failures
- Multi-AZ deployment
- Database backups (managed by Neon)

### NFR-3: Scalability
- Horizontal pod autoscaling (2-10 replicas)
- Kafka partition scaling
- Database connection pooling
- CDN for static assets (optional)

### NFR-4: Security
- All traffic encrypted (TLS)
- Service mesh mTLS via Dapr
- Secrets in cloud secret manager
- RBAC for Kubernetes
- Network policies
- Container security scanning

### NFR-5: Maintainability
- Infrastructure as Code
- GitOps deployment
- Comprehensive documentation
- Runbooks for common operations
- Feature flags for rollouts

---

## 4. Acceptance Criteria

### AC-1: Advanced Features Complete

- ✅ Due dates: Create, edit, display, filter, sort
- ✅ Recurring tasks: All patterns work, next instance created
- ✅ Priorities: CRUD, filter, sort, visual indicators
- ✅ Tags: CRUD, filter, auto-suggest
- ✅ Search: Real-time, accurate, <500ms
- ✅ Filters: All criteria work, combinable
- ✅ Sorting: All fields, both directions

### AC-2: Kafka Events Working

- ✅ task-events topic created and configured
- ✅ reminders topic created and configured
- ✅ task-updates topic created and configured
- ✅ Events published on task CRUD
- ✅ Events consumed and processed
- ✅ Dead letter queue configured
- ✅ Event latency <500ms

### AC-3: Dapr Integration Complete

- ✅ Pub/Sub component configured and working
- ✅ State store component working
- ✅ Service invocation working (mTLS)
- ✅ Secrets management working
- ✅ Jobs API configured (if applicable)
- ✅ Dapr sidecars running with all pods
- ✅ Dapr dashboard accessible (optional)

### AC-4: Local Minikube Deployment

- ✅ Minikube cluster with adequate resources
- ✅ Dapr installed and running
- ✅ Kafka deployed (Strimzi)
- ✅ Application deployed with Dapr sidecars
- ✅ All features working locally
- ✅ Events flowing through Kafka
- ✅ Documented setup process

### AC-5: Cloud Deployment Successful

- ✅ Kubernetes cluster operational
- ✅ Container registry configured
- ✅ Managed Kafka running
- ✅ Dapr installed on cloud cluster
- ✅ Application deployed and accessible
- ✅ External DNS/URL working
- ✅ TLS certificate installed

### AC-6: CI/CD Pipeline Operational

- ✅ GitHub Actions workflow created
- ✅ Build stage passing
- ✅ Docker build and push working
- ✅ Staging deployment automated
- ✅ Production deployment with approval
- ✅ Rollback procedure documented
- ✅ Pipeline completes <15 minutes

### AC-7: Observability Configured

- ✅ Application logs accessible
- ✅ Metrics collection working
- ✅ Distributed tracing enabled
- ✅ Alerts configured for critical issues
- ✅ Dashboard for monitoring (optional)

### AC-8: Documentation Complete

- ✅ Architecture diagram updated
- ✅ Kafka topic documentation
- ✅ Dapr component documentation
- ✅ CI/CD pipeline documentation
- ✅ Cloud deployment guide
- ✅ Local development guide
- ✅ Troubleshooting guide
- ✅ API documentation updated

### AC-9: Demo Video Created

- ✅ Video <90 seconds
- ✅ Shows cloud deployment
- ✅ Shows Kafka events in action
- ✅ Shows advanced feature (recurring/due dates)
- ✅ Shows Dapr integration
- ✅ Clear narration or captions

---

## 5. Edge Cases & Error Scenarios

### EC-1: Kafka Broker Unavailable
**Scenario**: Kafka cluster temporarily unreachable
**Expected**: Events queued locally, retry with backoff
**Resolution**: Events delivered when broker recovers

### EC-2: Duplicate Events
**Scenario**: Event published twice due to retry
**Expected**: Consumer handles idempotently
**Resolution**: Dedupe by event ID

### EC-3: Recurring Task Drift
**Scenario**: Task completed late, next instance date calculation
**Expected**: Next instance based on original schedule, not completion time
**Resolution**: Store original schedule, calculate from last scheduled date

### EC-4: Reminder Already Sent
**Scenario**: Reminder job runs twice for same task
**Expected**: Only one reminder sent
**Resolution**: Track reminder status in database

### EC-5: CI/CD Pipeline Failure
**Scenario**: Deployment fails mid-rollout
**Expected**: Automatic rollback to previous version
**Resolution**: Helm rollback, notify team

### EC-6: Cloud Provider Outage
**Scenario**: Cloud region experiencing issues
**Expected**: Application continues in other AZs
**Resolution**: Multi-AZ deployment, failover procedures

---

## 6. Data Requirements

### DR-1: Database Schema Changes

**Tasks Table Updates**:
```sql
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags TEXT[];
ALTER TABLE tasks ADD COLUMN recurrence_pattern JSONB;
ALTER TABLE tasks ADD COLUMN next_occurrence TIMESTAMP;
ALTER TABLE tasks ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;
```

### DR-2: New Tables

**Reminders Log** (optional):
```sql
CREATE TABLE reminder_log (
  id UUID PRIMARY KEY,
  task_id UUID REFERENCES tasks(id),
  user_id VARCHAR(255),
  sent_at TIMESTAMP,
  type VARCHAR(50)
);
```

### DR-3: Event Schemas

All events must follow CloudEvents specification:
```json
{
  "specversion": "1.0",
  "type": "com.todoapp.task.created",
  "source": "/backend/tasks",
  "id": "uuid",
  "time": "2026-01-14T12:00:00Z",
  "datacontenttype": "application/json",
  "data": { ... }
}
```

---

## 7. Integration Requirements

### IR-1: Dapr ↔ Kafka
- Dapr Pub/Sub publishes to Kafka topics
- Consumers subscribe via Dapr subscription
- Dapr handles serialization, retries

### IR-2: Backend ↔ Dapr
- Backend uses Dapr SDK or HTTP API
- Publish: POST to Dapr sidecar
- Subscribe: Dapr calls backend endpoint

### IR-3: CI/CD ↔ Cloud
- GitHub Actions authenticates to cloud
- Pushes images to registry
- Deploys via Helm to cluster

### IR-4: Secrets ↔ Dapr
- Dapr reads from Kubernetes secrets
- Or cloud secret manager (Azure KeyVault, etc.)
- Application accesses via Dapr API

---

## 8. Constraints & Assumptions

### Constraints
1. Must use Dapr for all Kafka interaction
2. Must deploy to cloud Kubernetes (not local only)
3. Must use GitHub Actions for CI/CD
4. Must maintain backward compatibility with Phase III/IV
5. Kafka topics must be pre-created (no auto-create)

### Assumptions
1. Cloud provider account with credits available
2. Phase IV deployment working as baseline
3. OpenAI API key with sufficient quota
4. Neon database accessible from cloud
5. GitHub repository with Actions enabled

---

## 9. Dependencies

### External Dependencies

| Dependency | Source | Required |
|-----------|--------|----------|
| Dapr | dapr.io | Yes |
| Kafka (Redpanda) | redpanda.com | Yes |
| Cloud Provider | Azure/GCP/Oracle | Yes |
| GitHub Actions | github.com | Yes |
| Strimzi (local) | strimzi.io | For local only |

### Internal Dependencies

| Dependency | Source | Notes |
|-----------|--------|-------|
| Phase IV | Previous phase | Helm charts, Docker images |
| Database schema | Migration | New columns for features |
| API endpoints | Backend | New/updated endpoints |

---

## 10. Success Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Features | Advanced features complete | 100% |
| Events | Kafka event success rate | >99.9% |
| Performance | API p95 latency | <200ms |
| Reliability | Uptime | >99.9% |
| CI/CD | Pipeline success rate | >95% |
| Demo | Video duration | <90s |

---

## 11. Out of Scope

- ❌ Email notifications (in-app only)
- ❌ Push notifications (mobile)
- ❌ Collaborative features
- ❌ Offline support
- ❌ Advanced analytics
- ❌ Multi-tenant architecture
- ❌ GraphQL API

---

## 12. Approval

**Specification Status**: ✅ Approved
**Ready for Planning**: Yes
**Next Step**: Create plan.md
**Approver**: Development Team
**Date**: 2026-01-14

---

**References**:
- Constitution: constitution.md
- Hackathon PDF: Pages 24-36
- Phase IV: Completed
- Next: plan.md (Architecture & Implementation Strategy)
