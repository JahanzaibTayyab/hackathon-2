# Phase IV: Local Kubernetes Deployment - Constitution

## Project Identity
**Phase**: Phase IV - Local Kubernetes Deployment
**Objective**: Deploy Phase III Todo Chatbot on local Kubernetes cluster
**Due Date**: January 4, 2026
**Points**: 250

---

## WHY - Core Principles & Constraints

### 1. Cloud-Native First
**Principle**: All deployments must follow cloud-native best practices
- Containerized applications
- Declarative configuration
- Immutable infrastructure
- Horizontal scalability
- Health checks and observability

### 2. Infrastructure as Code
**Principle**: All infrastructure must be version-controlled and reproducible
- No manual kubectl commands for deployment
- Helm charts as single source of truth
- All configuration in Git
- Idempotent deployments

### 3. Spec-Driven Development
**Principle**: No implementation without specification
- Constitution → Specify → Plan → Tasks → Implement
- No manual coding allowed
- Use Claude Code for all code generation
- Iterate on specs, not code

### 4. AI-Assisted Operations (AIOps)
**Principle**: Leverage AI tools where available
- Primary: kubectl-ai, kagent, Docker AI (Gordon)
- Fallback: Standard CLI commands
- Document both approaches
- AI tools augment, not replace, understanding

### 5. Local-First Development
**Principle**: Everything must work on local Minikube before cloud
- Minikube as development environment
- Identical configuration for local/cloud
- No cloud-specific dependencies (except external DB)
- Resource constraints realistic for local machine

---

## Technology Constraints

### Required Stack
| Component | Technology | Version | Non-Negotiable |
|-----------|-----------|---------|----------------|
| Containerization | Docker | Latest | Yes |
| Container Runtime | Docker Desktop | 4.53+ | Yes (for Gordon) |
| Orchestration | Kubernetes (Minikube) | 1.28+ | Yes |
| Package Manager | Helm | 3.0+ | Yes |
| Base Images | Alpine/Slim variants | Latest stable | Yes |
| Application | Phase III Todo App | As-is | Yes |

### Optional Tools
- Docker AI (Gordon) - Recommended but not required
- kubectl-ai - Recommended for learning
- kagent - Optional advanced tool

### Prohibited
- ❌ Manual Kubernetes YAML without Helm
- ❌ Hardcoded secrets in templates
- ❌ Large base images (>1GB)
- ❌ Root containers (must run as non-root user)
- ❌ Missing health checks
- ❌ Missing resource limits

---

## Architecture Principles

### 1. Separation of Concerns
- Frontend and Backend as separate deployments
- One concern per container
- Services expose only necessary ports
- Secrets separated from ConfigMaps

### 2. Stateless Applications
- No local state in containers
- All persistence in external Neon DB
- Containers can be killed and recreated
- Horizontal scaling without coordination

### 3. Configuration Management
**Hierarchy**:
1. Secrets (DATABASE_URL, API keys) → Kubernetes Secret
2. Environment-specific config → values.yaml
3. Public config → ConfigMap
4. Application defaults → Container image

### 4. Security Baseline
- Non-root containers
- Read-only root filesystem where possible
- Secrets mounted as volumes, not environment variables
- Network policies (future phase)
- Image scanning (future phase)

### 5. Observability
- Health endpoints for all services
- Structured logging to stdout/stderr
- Kubernetes liveness/readiness probes
- Resource metrics via kubectl top

---

## Development Workflow Principles

### 1. Build → Test → Deploy → Verify
```
Dockerfile → docker build → docker run (local test)
    ↓
Load into Minikube
    ↓
Helm template → helm lint → helm install
    ↓
kubectl get pods → kubectl logs → curl/browser test
```

### 2. Fail Fast
- Validate Helm chart before install
- Set aggressive health check timeouts
- Use `--wait` flag on helm install
- Check logs immediately after deployment

### 3. Incremental Deployment
- Deploy frontend first, verify
- Deploy backend, verify
- Test integration
- Don't move forward until current step works

---

## Quality Gates

### Before Moving to Implementation
- ✅ All specs reviewed and approved
- ✅ Plan has no architectural conflicts
- ✅ Tasks are atomic and testable
- ✅ Success criteria defined for each task

### Before Considering Phase IV Complete
- ✅ All acceptance criteria met
- ✅ Application accessible from host machine
- ✅ All Phase III features functional
- ✅ Documentation complete
- ✅ Demo video recorded (<90 seconds)
- ✅ Clean Minikube deployment (no errors in logs)

### Before Submission
- ✅ GitHub repository updated
- ✅ Helm chart committed with proper structure
- ✅ README includes deployment instructions
- ✅ TROUBLESHOOTING guide created
- ✅ All specs in /specs folder
- ✅ Demo video uploaded

---

## Resource Constraints

### Local Machine Requirements
- **CPU**: Minimum 4 cores available
- **Memory**: Minimum 8GB available for Minikube
- **Disk**: Minimum 20GB free space
- **Network**: Internet access for image pulls and Neon DB

### Minikube Configuration
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Per-Pod Resource Limits
**Frontend**:
- CPU Request: 100m, Limit: 500m
- Memory Request: 128Mi, Limit: 512Mi

**Backend**:
- CPU Request: 100m, Limit: 500m
- Memory Request: 256Mi, Limit: 1Gi

---

## Performance Expectations

| Metric | Target | Maximum Acceptable |
|--------|--------|-------------------|
| Docker build time (both) | 3 min | 5 min |
| Helm install time | 1 min | 2 min |
| Pod startup time | 30 sec | 1 min |
| Frontend response time | <500ms | <1s |
| Backend API response time | <200ms | <500ms |
| Image size (frontend) | 300MB | 500MB |
| Image size (backend) | 200MB | 300MB |

---

## Error Handling Strategy

### Build Errors
- Check Dockerfile syntax
- Verify all COPY paths exist
- Check base image availability
- Review build logs line by line

### Deployment Errors
- Validate Helm chart first: `helm lint`
- Check image availability in Minikube: `minikube image ls`
- Verify secrets exist: `kubectl get secrets`
- Review pod events: `kubectl describe pod`

### Runtime Errors
- Check pod logs: `kubectl logs`
- Verify environment variables
- Test database connectivity
- Check service endpoints

---

## Documentation Standards

### Every Kubernetes Resource Must Have
- Labels: app, component, phase
- Annotations: description, owner
- Resource limits
- Health checks (where applicable)

### Every Helm Template Must Have
- Comment header explaining purpose
- Values.yaml reference in comments
- Example usage in comments

### README Must Include
- Prerequisites with versions
- Step-by-step deployment instructions
- Verification commands
- Troubleshooting section
- Link to demo video

---

## Version Control

### Commit Standards
- Atomic commits per task
- Descriptive messages: "feat: add frontend Dockerfile (T-B01)"
- Reference task IDs in commits
- No secrets in commits

### Branch Strategy
- Main branch: stable code only
- Feature branch: `phase4-kubernetes-deployment`
- Merge to main only when all acceptance criteria met

---

## Alignment with Hackathon Requirements

### Must Use
- ✅ Spec-Driven Development (Specify → Plan → Tasks → Implement)
- ✅ Claude Code for implementation
- ✅ SpecKit Plus for workflow
- ✅ Docker containerization
- ✅ Minikube local deployment
- ✅ Helm charts

### Should Use
- ⭐ Docker AI (Gordon) if available
- ⭐ kubectl-ai for learning
- ⭐ kagent for advanced insights

### Demo Requirements
- ✅ 90-second video maximum
- ✅ Show: Minikube cluster, Helm deployment, running app, one feature
- ✅ Tool: NotebookLM or screen recording

---

## Success Definition

Phase IV is successful when:
1. Frontend and backend containerized with optimized images
2. Helm chart deploys application to Minikube without errors
3. Application accessible from host browser
4. All Phase III features work identically
5. Documentation enables anyone to replicate deployment
6. Demo video showcases working deployment
7. Ready to proceed to Phase V (Cloud Deployment)

---

## Non-Goals (Out of Scope for Phase IV)

- ❌ Cloud deployment (that's Phase V)
- ❌ Kafka integration (that's Phase V)
- ❌ Dapr integration (that's Phase V)
- ❌ CI/CD pipeline (that's Phase V)
- ❌ Production-grade monitoring
- ❌ Multi-region deployment
- ❌ Auto-scaling policies
- ❌ Advanced security hardening

---

## Constitutional Hierarchy

If conflicts arise:
1. **Hackathon requirements** (from PDF) override all
2. **This Constitution** defines Phase IV principles
3. **Specify** defines what to build
4. **Plan** defines how to build
5. **Tasks** define step-by-step implementation

---

**Last Updated**: 2026-01-13
**Phase**: IV of V
**Status**: Constitution Approved - Ready for Specify Phase
