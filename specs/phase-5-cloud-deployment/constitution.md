# Phase V: Advanced Cloud Deployment - Constitution

## Project Identity
**Phase**: Phase V - Advanced Cloud Deployment
**Objective**: Deploy enhanced Todo application with Kafka event-driven architecture and Dapr to cloud Kubernetes
**Due Date**: January 18, 2026
**Points**: 300

---

## WHY - Core Principles & Constraints

### 1. Event-Driven Architecture First
**Principle**: The application must transition from synchronous to event-driven patterns
- Kafka as the event backbone
- Decoupled services communicating through events
- Eventual consistency where appropriate
- Idempotent message processing
- Dead letter queues for failed events

### 2. Dapr Abstraction Layer
**Principle**: Use Dapr building blocks to abstract infrastructure complexity
- Pub/Sub: Kafka abstracted through Dapr
- State Management: Consistent state handling
- Service Invocation: Service-to-service communication
- Jobs API: Scheduled reminder notifications
- Secrets Management: Centralized secret handling
- Dapr enables cloud-agnostic deployments

### 3. Cloud-Native Best Practices
**Principle**: Follow 12-factor app principles for cloud deployment
- External configuration
- Backing services as attached resources
- Horizontal scalability
- Process disposability
- Environment parity (dev/staging/prod)
- Logs as event streams

### 4. Spec-Driven Development
**Principle**: No implementation without specification
- Constitution → Specify → Plan → Tasks → Implement
- No manual coding allowed
- Use Claude Code for all code generation
- Iterate on specs, not code

### 5. Infrastructure as Code
**Principle**: All infrastructure must be version-controlled
- Terraform/Pulumi for cloud resources
- Helm charts for Kubernetes deployments
- GitHub Actions for CI/CD
- GitOps workflow for deployments

---

## Technology Constraints

### Required Stack

| Component | Technology | Version | Non-Negotiable |
|-----------|-----------|---------|----------------|
| Event Streaming | Apache Kafka | Latest | Yes |
| Kafka Provider | Redpanda Cloud OR Strimzi | Latest | Yes |
| Application Runtime | Dapr | 1.13+ | Yes |
| Cloud Provider | Azure AKS OR GKE OR OKE | Latest | Yes |
| CI/CD | GitHub Actions | Latest | Yes |
| Container Registry | Cloud Provider Registry | - | Yes |
| Orchestration | Kubernetes | 1.28+ | Yes |
| Package Manager | Helm | 3.0+ | Yes |

### Kafka Topics (Required)

| Topic | Purpose | Producer | Consumer |
|-------|---------|----------|----------|
| task-events | Task CRUD operations | Backend | Analytics/Notifications |
| reminders | Due date reminders | Scheduler/Jobs | Notification Service |
| task-updates | Real-time task updates | Backend | Frontend (WebSocket) |

### Dapr Building Blocks (Required)

| Building Block | Use Case | Configuration |
|----------------|----------|---------------|
| Pub/Sub | Kafka message publishing/subscribing | pubsub.yaml |
| State | Distributed state management | statestore.yaml |
| Service Invocation | Service-to-service calls | N/A (automatic) |
| Jobs API | Scheduled reminder checks | jobs.yaml |
| Secrets | Centralized secret management | secrets.yaml |

### Advanced Features (Required)

| Feature | Description | Priority |
|---------|-------------|----------|
| Recurring Tasks | Daily, weekly, monthly recurrence | High |
| Due Dates | Task deadlines with reminders | High |
| Priorities | Low, Medium, High, Urgent | High |
| Tags | Custom labels for categorization | Medium |
| Search | Full-text search across tasks | Medium |
| Filter | Filter by status, priority, tags, dates | High |
| Sort | Multiple sort options | High |

### Prohibited
- ❌ Direct Kafka client usage (must use Dapr Pub/Sub)
- ❌ Hardcoded cloud provider configurations
- ❌ Manual deployments (must use CI/CD)
- ❌ Secrets in code or Git
- ❌ Single point of failure architectures
- ❌ Missing health checks or observability
- ❌ Polling-based message consumption

---

## Architecture Principles

### 1. Event Sourcing Pattern
- All state changes emit events
- Events are immutable facts
- State can be reconstructed from events
- Audit trail built-in

### 2. CQRS (Command Query Responsibility Segregation)
- Separate read and write paths where beneficial
- Optimized query models
- Eventually consistent reads

### 3. Microservices Communication
**Synchronous**: HTTP/gRPC via Dapr Service Invocation
- User authentication
- Immediate responses required

**Asynchronous**: Kafka via Dapr Pub/Sub
- Task creation notifications
- Reminder scheduling
- Analytics events

### 4. Resilience Patterns
- Circuit breakers for external services
- Retry with exponential backoff
- Bulkhead isolation
- Dead letter queues

### 5. Security Baseline
- Zero-trust networking
- Service-to-service authentication (mTLS via Dapr)
- Secrets in cloud secret managers
- Network policies in Kubernetes
- RBAC for all resources

---

## Development Workflow Principles

### 1. Local → Minikube → Cloud
```
Local Development (Dapr standalone)
    ↓
Minikube with Dapr + Kafka (Strimzi)
    ↓
Cloud Kubernetes (AKS/GKE/OKE) with Managed Kafka
```

### 2. CI/CD Pipeline Stages
```
Push to main → Build Images → Push to Registry
    ↓
Deploy to Staging → Integration Tests
    ↓
Manual Approval → Deploy to Production
```

### 3. Event-Driven Testing
- Unit tests with mock Dapr
- Integration tests with local Kafka
- E2E tests with real services

---

## Quality Gates

### Before Moving to Implementation
- ✅ All specs reviewed and approved
- ✅ Kafka topic design validated
- ✅ Dapr configuration reviewed
- ✅ Cloud provider selection made
- ✅ CI/CD pipeline designed

### Before Considering Phase V Complete
- ✅ All advanced features implemented
- ✅ Kafka events flowing correctly
- ✅ Dapr building blocks working
- ✅ Local Minikube deployment successful
- ✅ Cloud deployment successful
- ✅ CI/CD pipeline operational
- ✅ Documentation complete
- ✅ Demo video recorded (<90 seconds)

### Before Submission
- ✅ GitHub repository updated
- ✅ All infrastructure as code committed
- ✅ CI/CD workflows in .github/workflows
- ✅ README includes cloud deployment instructions
- ✅ Demo video uploaded

---

## Resource Requirements

### Local Development
- **CPU**: Minimum 6 cores available
- **Memory**: Minimum 12GB available
- **Disk**: Minimum 30GB free space
- **Network**: Internet access required

### Minikube with Dapr + Kafka
```bash
minikube start --cpus=6 --memory=12288 --driver=docker
```

### Cloud Kubernetes Cluster
- **Node Count**: Minimum 3 nodes
- **Node Size**: 4 vCPU, 8GB RAM each
- **Total**: 12 vCPU, 24GB RAM

---

## Performance Expectations

| Metric | Target | Maximum Acceptable |
|--------|--------|-------------------|
| Kafka event latency | <100ms | 500ms |
| Task creation (E2E) | <1s | 2s |
| Search response time | <500ms | 1s |
| Reminder delivery | <5s of due time | 30s |
| CI/CD pipeline | <10 min | 15 min |
| Pod startup time | <30 sec | 1 min |

---

## Error Handling Strategy

### Event Processing Errors
- Automatic retry with backoff
- Dead letter queue after max retries
- Alerting on DLQ messages
- Manual intervention process

### Service Failures
- Circuit breaker activation
- Graceful degradation
- Health check failures trigger restarts
- Automatic failover where possible

### Cloud Resource Failures
- Multi-AZ deployments
- Auto-scaling policies
- Health-based routing
- Disaster recovery procedures

---

## Documentation Standards

### Every Kafka Topic Must Have
- Schema definition (JSON Schema or Avro)
- Producer documentation
- Consumer documentation
- Retention policy
- Partitioning strategy

### Every Dapr Component Must Have
- Component YAML with comments
- Usage documentation
- Testing instructions

### Every CI/CD Stage Must Have
- Clear description
- Success/failure criteria
- Rollback procedure
- Manual intervention points

---

## Alignment with Hackathon Requirements

### Must Use
- ✅ Spec-Driven Development
- ✅ Claude Code for implementation
- ✅ Kafka event streaming
- ✅ Dapr building blocks
- ✅ Cloud Kubernetes (AKS/GKE/OKE)
- ✅ GitHub Actions CI/CD

### Should Use
- ⭐ Redpanda Cloud for managed Kafka
- ⭐ Strimzi for self-hosted Kafka
- ⭐ Cloud provider managed services where available
- ⭐ Infrastructure as Code (Terraform/Pulumi)

### Demo Requirements
- ✅ 90-second video maximum
- ✅ Show: Cloud deployment, Kafka events, Dapr integration, one advanced feature
- ✅ Tool: NotebookLM or screen recording

---

## Success Definition

Phase V is successful when:
1. All advanced features implemented (recurring tasks, due dates, priorities, tags, search, filter, sort)
2. Kafka event-driven architecture working
3. Dapr building blocks integrated
4. Local Minikube deployment with Dapr successful
5. Cloud Kubernetes deployment operational
6. CI/CD pipeline deploying automatically
7. Documentation enables replication
8. Demo video showcases all major features

---

## Non-Goals (Out of Scope for Phase V)

- ❌ Machine learning features
- ❌ Mobile applications
- ❌ Multi-tenant SaaS features
- ❌ Real-time collaboration
- ❌ Offline support
- ❌ GraphQL API
- ❌ Advanced analytics dashboard

---

## Phase V Sub-Phases

### Part A: Advanced Features & Kafka Integration
- Add recurring tasks, due dates, priorities, tags
- Implement search, filter, sort functionality
- Set up Kafka topics and event publishing
- Integrate Dapr Pub/Sub

### Part B: Local Deployment with Dapr on Minikube
- Install Dapr on Minikube
- Deploy Kafka (Strimzi or local)
- Configure Dapr components
- Test full event flow locally

### Part C: Cloud Deployment
- Set up cloud Kubernetes cluster (AKS/GKE/OKE)
- Deploy managed Kafka (Redpanda or cloud-native)
- Configure CI/CD pipeline
- Deploy application with full observability

---

## Constitutional Hierarchy

If conflicts arise:
1. **Hackathon requirements** (from PDF) override all
2. **This Constitution** defines Phase V principles
3. **Specification** defines what to build
4. **Plan** defines how to build
5. **Tasks** define step-by-step implementation

---

**Last Updated**: 2026-01-14
**Phase**: V of V
**Status**: Constitution Approved - Ready for Specification Phase
