# Phase IV: Local Kubernetes Deployment - Specify

## WHAT - Requirements, User Journeys & Acceptance Criteria

**Phase**: Phase IV - Local Kubernetes Deployment
**From Constitution**: phase4-constitution.md
**Status**: Specification Approved

---

## 1. User Journeys

### Journey 1: DevOps Engineer - Initial Deployment

**Actor**: DevOps Engineer
**Goal**: Deploy the Todo application to local Minikube cluster for the first time
**Context**: Application code exists from Phase III, need to containerize and deploy

**Journey Steps**:

1. **Setup Environment**
   - Install Docker Desktop, Minikube, kubectl, Helm
   - Start Minikube cluster with adequate resources
   - Verify all tools are working

2. **Build Container Images**
   - Navigate to frontend directory
   - Build frontend Docker image using multi-stage Dockerfile
   - Navigate to backend directory
   - Build backend Docker image
   - Verify both images work locally with `docker run`

3. **Load Images into Minikube**
   - Load frontend image into Minikube's Docker daemon
   - Load backend image into Minikube's Docker daemon
   - Verify images are available in Minikube

4. **Deploy Using Helm**
   - Navigate to Helm chart directory
   - Create Kubernetes secrets with database credentials
   - Install Helm chart: `helm install todo-app ./helm-chart/todo-app -n todo-app --create-namespace`
   - Wait for pods to reach Running state

5. **Access Application**
   - Use `minikube service frontend-service -n todo-app` to open browser
   - Or port-forward: `kubectl port-forward svc/frontend-service 3000:3000 -n todo-app`
   - Log in to application
   - Verify all features work

**Success Criteria**:
- ✅ Application accessible from browser within 5 minutes
- ✅ Zero errors in pod logs
- ✅ All Phase III features functional

---

### Journey 2: Developer - Update and Redeploy

**Actor**: Developer
**Goal**: Make code changes and redeploy to Minikube
**Context**: Application already deployed, need to test code changes

**Journey Steps**:

1. **Make Code Changes**
   - Update frontend or backend code
   - Commit changes to Git

2. **Rebuild Images**
   - Rebuild affected Docker image
   - Load new image into Minikube
   - Tag image with new version (or use :latest)

3. **Upgrade Deployment**
   - Run: `helm upgrade todo-app ./helm-chart/todo-app -n todo-app`
   - Watch pods rolling update: `kubectl get pods -n todo-app -w`
   - Verify new version deployed

4. **Test Changes**
   - Access application via browser
   - Test specific changed feature
   - Check logs for errors

**Success Criteria**:
- ✅ Helm upgrade completes without downtime
- ✅ New pods start successfully
- ✅ Code changes reflected in running application

---

### Journey 3: DevOps Engineer - Troubleshoot Issues

**Actor**: DevOps Engineer
**Goal**: Diagnose and fix deployment issues
**Context**: Pods are not starting or application not working

**Journey Steps**:

1. **Check Pod Status**
   - Run: `kubectl get pods -n todo-app`
   - Identify pods in CrashLoopBackOff or Pending state

2. **Investigate Pod Events**
   - Run: `kubectl describe pod <pod-name> -n todo-app`
   - Review Events section for errors

3. **Check Pod Logs**
   - Run: `kubectl logs <pod-name> -n todo-app`
   - Look for ERROR or FATAL messages

4. **Verify Configuration**
   - Check secrets: `kubectl get secrets -n todo-app`
   - Check configmaps: `kubectl get configmaps -n todo-app`
   - Verify environment variables in pod

5. **Test Connectivity**
   - Port-forward to backend: `kubectl port-forward svc/backend-service 8000:8000 -n todo-app`
   - Test health endpoint: `curl http://localhost:8000/health`
   - Verify database connection from pod

6. **Fix Issues**
   - Update Helm values or templates
   - Helm upgrade with fixes
   - Verify pods now healthy

**Success Criteria**:
- ✅ Root cause identified within 15 minutes
- ✅ Issue resolved with configuration change
- ✅ All pods reach Running and Ready state

---

### Journey 4: Student - AI-Assisted Operations

**Actor**: Student learning Kubernetes
**Goal**: Use AI tools to manage Kubernetes deployment
**Context**: Want to leverage kubectl-ai and Docker AI for learning

**Journey Steps**:

1. **Use Docker AI (Gordon)**
   - Ask: `docker ai "show me the size of all my images"`
   - Ask: `docker ai "how can I reduce the size of todo-frontend image?"`
   - Apply optimization suggestions

2. **Use kubectl-ai**
   - Deploy: `kubectl-ai "deploy the todo app to namespace todo-app"`
   - Scale: `kubectl-ai "scale the frontend to 3 replicas"`
   - Debug: `kubectl-ai "why is my backend pod not starting?"`

3. **Use kagent**
   - Analyze: `kagent "analyze the health of my cluster"`
   - Optimize: `kagent "suggest resource optimizations for todo-app namespace"`

**Success Criteria**:
- ✅ AI tools provide helpful suggestions
- ✅ Student understands both AI and traditional approaches
- ✅ Deployment succeeds with AI assistance

---

## 2. Functional Requirements

### FR-1: Container Images

**FR-1.1: Frontend Containerization**
- **Description**: Next.js frontend must be packaged as Docker image
- **Requirements**:
  - Use node:20-alpine as base image
  - Multi-stage build (dependencies → build → runtime)
  - Only include standalone output in final image
  - Expose port 3000
  - Run as non-root user
  - Image size <500MB
  - No build-time secrets in image
- **Validation**: `docker run -p 3000:3000 todo-frontend:latest` works locally

**FR-1.2: Backend Containerization**
- **Description**: FastAPI backend must be packaged as Docker image
- **Requirements**:
  - Use python:3.13-slim as base image
  - Install dependencies via uv
  - Expose port 8000
  - Run as non-root user
  - Image size <300MB
  - Include health check endpoint
- **Validation**: `docker run -p 8000:8000 todo-backend:latest` responds to /health

**FR-1.3: Build Optimization**
- **Description**: Images must be optimized for size and build speed
- **Requirements**:
  - Use .dockerignore files
  - Layer caching strategy
  - Multi-stage builds where applicable
  - No unnecessary packages
- **Validation**: Build completes in <5 minutes total

---

### FR-2: Kubernetes Deployment

**FR-2.1: Minikube Cluster**
- **Description**: Application must run on local Minikube cluster
- **Requirements**:
  - Minikube started with: `--cpus=4 --memory=8192 --driver=docker`
  - Kubernetes version 1.28+
  - Namespace: `todo-app`
- **Validation**: `minikube status` shows "Running"

**FR-2.2: Frontend Deployment**
- **Description**: Frontend deployed as Kubernetes Deployment
- **Requirements**:
  - Deployment name: `frontend-deployment`
  - Replicas: 2 (configurable)
  - Container port: 3000
  - Labels: `app=frontend, phase=4`
  - Liveness probe: HTTP GET / port 3000
  - Readiness probe: HTTP GET / port 3000
  - Resource requests: CPU 100m, Memory 128Mi
  - Resource limits: CPU 500m, Memory 512Mi
- **Validation**: `kubectl get deployments -n todo-app` shows 2/2 ready

**FR-2.3: Backend Deployment**
- **Description**: Backend deployed as Kubernetes Deployment
- **Requirements**:
  - Deployment name: `backend-deployment`
  - Replicas: 2 (configurable)
  - Container port: 8000
  - Labels: `app=backend, phase=4`
  - Liveness probe: HTTP GET /health port 8000
  - Readiness probe: HTTP GET /health port 8000
  - Resource requests: CPU 100m, Memory 256Mi
  - Resource limits: CPU 500m, Memory 1Gi
- **Validation**: `kubectl get deployments -n todo-app` shows 2/2 ready

**FR-2.4: Frontend Service**
- **Description**: Frontend exposed via Kubernetes Service
- **Requirements**:
  - Service name: `frontend-service`
  - Type: NodePort
  - Port: 3000
  - Selector: `app=frontend`
  - NodePort: 30000 or auto-assigned
- **Validation**: `minikube service frontend-service -n todo-app` opens browser

**FR-2.5: Backend Service**
- **Description**: Backend exposed via Kubernetes Service
- **Requirements**:
  - Service name: `backend-service`
  - Type: ClusterIP (internal only)
  - Port: 8000
  - Selector: `app=backend`
- **Validation**: Port-forward works, frontend can reach backend

---

### FR-3: Helm Chart

**FR-3.1: Chart Structure**
- **Description**: Application deployable via Helm chart
- **Requirements**:
  - Chart name: `todo-app`
  - Chart version: 0.1.0
  - App version: matches Phase IV
  - Chart.yaml with metadata
  - values.yaml with all configurable options
  - templates/ directory with all Kubernetes resources
  - _helpers.tpl with reusable template functions
  - NOTES.txt with post-install instructions
- **Validation**: `helm lint` passes with no errors

**FR-3.2: Configurability**
- **Description**: All deployment aspects configurable via values.yaml
- **Requirements**:
  - Image names and tags
  - Replica counts
  - Resource limits/requests
  - Service types and ports
  - Environment variables
  - Ingress enabled/disabled (future)
- **Validation**: Can deploy with custom values

**FR-3.3: Templating**
- **Description**: Templates must be valid and render correctly
- **Requirements**:
  - All resources use template functions from _helpers.tpl
  - Labels and selectors consistent
  - Resource names follow naming convention
  - Annotations include descriptions
- **Validation**: `helm template` renders without errors

**FR-3.4: Lifecycle Management**
- **Description**: Helm chart supports full lifecycle
- **Requirements**:
  - Install: `helm install`
  - Upgrade: `helm upgrade` (zero-downtime)
  - Rollback: `helm rollback`
  - Uninstall: `helm uninstall` (cleans up all resources)
- **Validation**: All lifecycle operations succeed

---

### FR-4: Configuration Management

**FR-4.1: ConfigMap**
- **Description**: Non-sensitive configuration via ConfigMap
- **Requirements**:
  - ConfigMap name: `app-config`
  - Contains: NEXT_PUBLIC_API_URL, NODE_ENV
  - Mounted as environment variables
- **Validation**: Pods have correct environment variables

**FR-4.2: Secrets**
- **Description**: Sensitive data via Kubernetes Secrets
- **Requirements**:
  - Secret name: `app-secrets`
  - Contains: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, BETTER_AUTH_URL
  - Type: Opaque
  - Not checked into Git
  - Created separately before Helm install
- **Validation**: `kubectl get secret app-secrets -n todo-app` exists

**FR-4.3: External Dependencies**
- **Description**: Application connects to external services
- **Requirements**:
  - Database: Neon PostgreSQL (external, not in cluster)
  - OpenAI API: External API
  - No local database required
- **Validation**: Backend logs show successful database connection

---

### FR-5: Observability

**FR-5.1: Health Checks**
- **Description**: All services expose health endpoints
- **Requirements**:
  - Frontend: GET / returns 200
  - Backend: GET /health returns 200 with status
  - Liveness probes configured
  - Readiness probes configured
- **Validation**: `kubectl get pods` shows all Ready

**FR-5.2: Logging**
- **Description**: Application logs to stdout/stderr
- **Requirements**:
  - Structured logging (JSON preferred)
  - Log levels: INFO, WARN, ERROR
  - No sensitive data in logs
  - Logs accessible via kubectl logs
- **Validation**: `kubectl logs` shows application logs

**FR-5.3: Resource Monitoring**
- **Description**: Resource usage visible
- **Requirements**:
  - Metrics server enabled in Minikube
  - `kubectl top pods` works
  - `kubectl top nodes` works
- **Validation**: Resource metrics displayed

---

### FR-6: AI Operations

**FR-6.1: Docker AI Integration (Optional)**
- **Description**: Demonstrate Docker AI (Gordon) usage
- **Requirements**:
  - Docker Desktop 4.53+
  - Gordon enabled in settings
  - Document Gordon commands used
- **Validation**: Gordon provides helpful responses

**FR-6.2: kubectl-ai Usage (Optional)**
- **Description**: Demonstrate kubectl-ai for operations
- **Requirements**:
  - kubectl-ai installed
  - Show scaling via kubectl-ai
  - Show debugging via kubectl-ai
  - Document commands used
- **Validation**: kubectl-ai successfully executes Kubernetes operations

**FR-6.3: Standard CLI Fallback**
- **Description**: All operations documented with standard CLI
- **Requirements**:
  - Every AI command has kubectl/helm equivalent
  - Documentation shows both approaches
  - Works without AI tools
- **Validation**: Deployment succeeds using only standard tools

---

## 3. Non-Functional Requirements

### NFR-1: Performance

| Metric | Requirement | Critical Threshold |
|--------|-------------|-------------------|
| Docker build time (total) | <3 min | 5 min |
| Helm install time | <1 min | 2 min |
| Pod startup time | <30 sec | 1 min |
| Frontend response time (/) | <500ms | 1 sec |
| Backend response time (/health) | <100ms | 500ms |
| Image size (frontend) | <300MB | 500MB |
| Image size (backend) | <200MB | 300MB |

### NFR-2: Reliability
- All pods must restart automatically on failure
- Helm upgrade must support zero-downtime deployment
- Data persists across pod restarts (in external DB)
- Application recovers from database connection loss

### NFR-3: Maintainability
- Helm chart version controlled
- All configuration in values.yaml
- No hardcoded values in templates
- Clear naming conventions
- Comprehensive documentation

### NFR-4: Security
- Containers run as non-root user (UID 1001+)
- No secrets in container images
- Secrets managed via Kubernetes Secrets
- Network policies (future phase)
- Container image scanning (future phase)

### NFR-5: Usability
- One-command deployment: `helm install`
- Clear error messages
- Comprehensive README
- Troubleshooting guide
- Demo video showing deployment

---

## 4. Acceptance Criteria

### AC-1: Containerization Complete
- ✅ Frontend Dockerfile exists and builds successfully
- ✅ Backend Dockerfile exists and builds successfully
- ✅ Both images run locally with `docker run`
- ✅ Images are loaded into Minikube
- ✅ Frontend image size <500MB
- ✅ Backend image size <300MB
- ✅ .dockerignore files present and effective
- ✅ Multi-stage builds used where applicable

### AC-2: Kubernetes Deployment Successful
- ✅ Minikube cluster running
- ✅ Namespace `todo-app` created
- ✅ Helm chart installs without errors
- ✅ All pods reach "Running" state within 2 minutes
- ✅ All pods show "Ready" status
- ✅ No errors in pod logs
- ✅ Resource limits configured and respected

### AC-3: Application Accessible
- ✅ Frontend accessible via browser (NodePort or port-forward)
- ✅ Backend health endpoint responds: `curl http://backend:8000/health`
- ✅ Frontend can communicate with backend
- ✅ Application loads without console errors

### AC-4: Functionality Preserved
- ✅ User can log in with existing credentials
- ✅ User can create new tasks
- ✅ User can view task list
- ✅ User can update task details
- ✅ User can mark tasks as complete
- ✅ User can delete tasks
- ✅ AI chatbot responds to natural language
- ✅ All Phase III features work identically

### AC-5: Helm Chart Quality
- ✅ `helm lint` passes with no warnings
- ✅ `helm template` renders valid YAML
- ✅ values.yaml contains all configurable options
- ✅ Chart installs successfully
- ✅ Chart upgrades successfully (zero downtime)
- ✅ Chart uninstalls cleanly (removes all resources)
- ✅ NOTES.txt provides helpful post-install instructions

### AC-6: Configuration Management
- ✅ Secrets created separately (not in Helm chart)
- ✅ ConfigMap contains non-sensitive config
- ✅ Environment variables correctly injected into pods
- ✅ Database connection works from pods
- ✅ OpenAI API accessible from pods
- ✅ No secrets visible in `helm template` output

### AC-7: Observability Working
- ✅ Liveness probes configured and passing
- ✅ Readiness probes configured and passing
- ✅ `kubectl logs` shows application logs
- ✅ `kubectl top pods` shows resource usage
- ✅ No ERROR level logs during normal operation

### AC-8: Documentation Complete
- ✅ README.md includes prerequisites
- ✅ README.md includes step-by-step deployment
- ✅ README.md includes access instructions
- ✅ README.md includes troubleshooting section
- ✅ TROUBLESHOOTING.md covers common issues
- ✅ Helm chart README documents all values
- ✅ Comments in Dockerfiles explain each stage

### AC-9: Demo Video Created
- ✅ Video recorded and uploaded
- ✅ Duration under 90 seconds
- ✅ Shows Minikube cluster running
- ✅ Shows Helm deployment command
- ✅ Shows application running in browser
- ✅ Demonstrates one feature (e.g., chatbot creating task)
- ✅ Clear audio or captions

### AC-10: AI Operations Demonstrated (Optional)
- ✅ Docker AI (Gordon) usage documented
- ✅ kubectl-ai usage demonstrated
- ✅ kagent usage demonstrated
- ✅ Standard CLI alternatives documented
- ✅ Both approaches shown in README

---

## 5. Edge Cases & Error Scenarios

### EC-1: Insufficient Resources
**Scenario**: Minikube started with insufficient memory
**Expected Behavior**: Pods evicted or fail to schedule
**Resolution**: Restart Minikube with `--memory=8192`

### EC-2: Image Not Found
**Scenario**: Helm install fails with ImagePullBackOff
**Expected Behavior**: Pods stuck in Pending
**Resolution**: Load images into Minikube with `minikube image load`

### EC-3: Database Connection Failure
**Scenario**: DATABASE_URL incorrect or database unreachable
**Expected Behavior**: Backend pods crash with connection error
**Resolution**: Verify secret, check network connectivity

### EC-4: Port Already in Use
**Scenario**: Port 3000 or 8000 already used on host
**Expected Behavior**: Port-forward fails
**Resolution**: Use different port or stop conflicting service

### EC-5: Helm Chart Syntax Error
**Scenario**: Invalid template syntax in Helm chart
**Expected Behavior**: `helm install` fails with parse error
**Resolution**: Run `helm lint` and `helm template` to find errors

### EC-6: Missing Secrets
**Scenario**: Helm install before creating secrets
**Expected Behavior**: Pods fail to start, missing environment variables
**Resolution**: Create secrets first, then helm install

### EC-7: Health Check Failing
**Scenario**: Health probe endpoint returns 500
**Expected Behavior**: Pods never reach Ready state
**Resolution**: Check application logs, fix health endpoint

---

## 6. Data Requirements

### DR-1: No Local Persistence Required
- Application uses external Neon PostgreSQL
- No PersistentVolumes needed in Minikube
- All state in external database

### DR-2: Secrets Management
- Secrets created manually before deployment
- Secrets contain:
  - DATABASE_URL (from Neon dashboard)
  - OPENAI_API_KEY (from OpenAI platform)
  - BETTER_AUTH_SECRET (shared between frontend/backend)
  - BETTER_AUTH_URL (frontend URL)

### DR-3: Configuration Data
- ConfigMap contains public configuration
- values.yaml contains deployment configuration
- No sensitive data in values.yaml

---

## 7. Integration Requirements

### IR-1: Frontend → Backend
- Frontend makes API calls to `http://backend-service:8000`
- Configured via NEXT_PUBLIC_API_URL environment variable
- Backend must be accessible from frontend pods

### IR-2: Backend → Database
- Backend connects to Neon PostgreSQL
- Connection string from DATABASE_URL secret
- Connection pooling configured
- Auto-reconnect on connection loss

### IR-3: Backend → OpenAI API
- Backend makes calls to OpenAI API
- API key from OPENAI_API_KEY secret
- Network egress required from cluster

### IR-4: User → Frontend
- User accesses via browser on host machine
- NodePort exposes frontend service
- Or port-forward: `kubectl port-forward svc/frontend-service 3000:3000`

---

## 8. Constraints & Assumptions

### Constraints
1. Must use Minikube (no other Kubernetes distributions)
2. Must use Helm for deployment (no raw YAML)
3. Must use Docker for containerization
4. Images must be loaded into Minikube (no registry)
5. Database must be external Neon (no local DB)

### Assumptions
1. Host machine meets minimum requirements (4 CPU, 8GB RAM)
2. Docker Desktop installed and running
3. Internet access available for image pulls
4. Neon database already provisioned (from Phase III)
5. OpenAI API key available (from Phase III)
6. Phase III application code working and tested

---

## 9. Dependencies

### External Dependencies
| Dependency | Version | Source | Required |
|-----------|---------|--------|----------|
| Docker Desktop | 4.53+ | docker.com | Yes |
| Minikube | 1.32+ | kubernetes.io | Yes |
| kubectl | 1.28+ | kubernetes.io | Yes |
| Helm | 3.0+ | helm.sh | Yes |
| kubectl-ai | Latest | kubectl-ai.com | Optional |
| kagent | Latest | GitHub | Optional |

### Internal Dependencies
| Dependency | Source | Notes |
|-----------|--------|-------|
| Phase III Application | Previous phase | Must be working |
| Neon Database | Phase II | Connection string required |
| OpenAI API Key | Phase III | For chatbot |
| Better Auth Config | Phase II | For authentication |

---

## 10. Success Metrics

### Deployment Metrics
- Time to first deployment: <30 minutes (for experienced user)
- Helm install success rate: 100% (with correct setup)
- Pod startup success rate: 100%
- Zero errors in logs after deployment

### Performance Metrics
- Frontend response time: <500ms
- Backend API response time: <200ms
- Pod restart time: <30 seconds
- Resource utilization: <50% of limits

### Quality Metrics
- All acceptance criteria met: 100%
- Documentation completeness: 100%
- Demo video quality: Clear and under 90 seconds
- Reproducibility: Anyone can deploy following README

---

## 11. Out of Scope

The following are explicitly NOT part of Phase IV:

- ❌ Cloud deployment (Phase V)
- ❌ Kafka integration (Phase V)
- ❌ Dapr integration (Phase V)
- ❌ CI/CD pipeline (Phase V)
- ❌ Container registry (use Minikube image load)
- ❌ Ingress controller (use NodePort/port-forward)
- ❌ TLS certificates (not needed for local)
- ❌ Advanced monitoring (Prometheus, Grafana)
- ❌ Service mesh (Istio, Linkerd)
- ❌ GitOps (ArgoCD, Flux)

---

## 12. Approval

**Specification Status**: ✅ Approved
**Ready for Planning**: Yes
**Next Step**: Create phase4-plan.md
**Approver**: Development Team
**Date**: 2026-01-13

---

**References**:
- Constitution: phase4-constitution.md
- Hackathon PDF: Pages 22-23
- Phase III: Completed and working
- Next: phase4-plan.md (Architecture & Implementation Strategy)
