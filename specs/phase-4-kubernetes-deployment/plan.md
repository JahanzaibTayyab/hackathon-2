# Phase IV: Local Kubernetes Deployment - Plan

## HOW - Architecture, Components & Implementation Strategy

**Phase**: Phase IV - Local Kubernetes Deployment
**From**: constitution.md, spec.md
**Status**: Plan Approved - Ready for Tasks

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          HOST MACHINE                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    MINIKUBE CLUSTER                          │  │
│  │               (Kubernetes 1.28+)                             │  │
│  │                                                              │  │
│  │  ┌───────────────────────┐      ┌───────────────────────┐   │  │
│  │  │   Frontend Namespace  │      │   Backend Namespace   │   │  │
│  │  │   ┌─────────────┐     │      │   ┌─────────────┐     │   │  │
│  │  │   │   Pod 1     │     │      │   │   Pod 1     │     │   │  │
│  │  │   │  Next.js    │     │      │   │  FastAPI    │     │   │  │
│  │  │   │  :3000      │     │      │   │  :8000      │     │   │  │
│  │  │   └─────────────┘     │      │   └─────────────┘     │   │  │
│  │  │   ┌─────────────┐     │      │   ┌─────────────┐     │   │  │
│  │  │   │   Pod 2     │     │      │   │   Pod 2     │     │   │  │
│  │  │   │  Next.js    │     │      │   │  FastAPI    │     │   │  │
│  │  │   │  :3000      │     │      │   │  :8000      │     │   │  │
│  │  │   └─────────────┘     │      │   └─────────────┘     │   │  │
│  │  │          ▲             │      │          ▲            │   │  │
│  │  │          │             │      │          │            │   │  │
│  │  │   ┌──────┴───────┐    │      │   ┌──────┴──────┐     │   │  │
│  │  │   │   Service    │    │      │   │   Service   │     │   │  │
│  │  │   │  (NodePort)  │    │      │   │ (ClusterIP) │     │   │  │
│  │  │   │  Port: 30000 │    │      │   │  Port: 8000 │     │   │  │
│  │  │   └──────────────┘    │      │   └─────────────┘     │   │  │
│  │  └───────────┬─────────────      ───────────┬────────────┘   │  │
│  │              │                               │                │  │
│  │              │    ┌─────────────────────┐   │                │  │
│  │              └───▶│   ConfigMap &       │◀──┘                │  │
│  │                   │   Secrets           │                    │  │
│  │                   │  - DATABASE_URL     │                    │  │
│  │                   │  - OPENAI_API_KEY   │                    │  │
│  │                   │  - BETTER_AUTH_*    │                    │  │
│  │                   └─────────────────────┘                    │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ▲                                     │
│                              │                                     │
│                     Browser: localhost:30000                       │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │  Neon PostgreSQL     │
                  │  (External Cloud)    │
                  │  Port: 5432          │
                  └──────────────────────┘
                              ▲
                              │
                  ┌──────────────────────┐
                  │  OpenAI API          │
                  │  (External Cloud)    │
                  │  HTTPS: 443          │
                  └──────────────────────┘
```

---

### 1.2 Component Interaction Flow

```
User Browser
    │
    │ HTTP (localhost:30000 or port-forward 3000)
    ▼
Frontend Service (NodePort)
    │
    │ Load Balance
    ▼
Frontend Pods (2 replicas)
    │
    │ HTTP (http://backend-service:8000/api/*)
    ▼
Backend Service (ClusterIP)
    │
    │ Load Balance
    ▼
Backend Pods (2 replicas)
    │
    ├─── HTTPS ──▶ Neon PostgreSQL (External)
    │
    └─── HTTPS ──▶ OpenAI API (External)
```

---

## 2. Component Breakdown

### 2.1 Docker Images

#### Component: Frontend Image
**Technology**: Docker with multi-stage build
**Base Image**: node:20-alpine
**Purpose**: Containerize Next.js application

**Build Stages**:
1. **Stage 1: Dependencies**
   - Install all node_modules
   - Uses package.json and package-lock.json
   - Leverages layer caching

2. **Stage 2: Builder**
   - Copy source code
   - Run `next build`
   - Generate standalone output

3. **Stage 3: Runner**
   - Copy only standalone output
   - Copy public assets
   - Set NODE_ENV=production
   - Run as non-root user (node:node)

**Exposed Ports**: 3000
**Entry Point**: `node server.js`
**Size Target**: <500MB

---

#### Component: Backend Image
**Technology**: Docker single-stage build
**Base Image**: python:3.13-slim
**Purpose**: Containerize FastAPI application

**Build Steps**:
1. Install uv package manager
2. Copy uv.lock and pyproject.toml
3. Install dependencies
4. Copy source code
5. Create non-root user
6. Set working directory

**Exposed Ports**: 8000
**Entry Point**: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
**Size Target**: <300MB

---

### 2.2 Kubernetes Resources

#### Component: Namespace
**Resource Type**: Namespace
**Name**: `todo-app`
**Purpose**: Isolate application resources

**Labels**:
```yaml
name: todo-app
phase: "4"
project: hackathon-2
```

---

#### Component: Frontend Deployment
**Resource Type**: Deployment
**Name**: `frontend-deployment`
**Namespace**: todo-app

**Specification**:
```yaml
replicas: 2
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1

selector:
  matchLabels:
    app: frontend
    phase: "4"

template:
  metadata:
    labels:
      app: frontend
      phase: "4"
      component: ui

  spec:
    containers:
    - name: frontend
      image: todo-frontend:latest
      imagePullPolicy: Never  # Use local image
      ports:
      - containerPort: 3000
        name: http
        protocol: TCP

      env:
      - name: NODE_ENV
        value: "production"
      - name: NEXT_PUBLIC_API_URL
        valueFrom:
          configMapKeyRef:
            name: app-config
            key: BACKEND_URL
      - name: BETTER_AUTH_URL
        valueFrom:
          secretKeyRef:
            name: app-secrets
            key: BETTER_AUTH_URL

      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 500m
          memory: 512Mi

      livenessProbe:
        httpGet:
          path: /
          port: 3000
        initialDelaySeconds: 30
        periodSeconds: 10
        timeoutSeconds: 5
        failureThreshold: 3

      readinessProbe:
        httpGet:
          path: /
          port: 3000
        initialDelaySeconds: 10
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 3

      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: false
```

---

#### Component: Backend Deployment
**Resource Type**: Deployment
**Name**: `backend-deployment`
**Namespace**: todo-app

**Specification**:
```yaml
replicas: 2
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1

selector:
  matchLabels:
    app: backend
    phase: "4"

template:
  metadata:
    labels:
      app: backend
      phase: "4"
      component: api

  spec:
    containers:
    - name: backend
      image: todo-backend:latest
      imagePullPolicy: Never  # Use local image
      ports:
      - containerPort: 8000
        name: http
        protocol: TCP

      env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: app-secrets
            key: DATABASE_URL
      - name: OPENAI_API_KEY
        valueFrom:
          secretKeyRef:
            name: app-secrets
            key: OPENAI_API_KEY
      - name: BETTER_AUTH_SECRET
        valueFrom:
          secretKeyRef:
            name: app-secrets
            key: BETTER_AUTH_SECRET

      resources:
        requests:
          cpu: 100m
          memory: 256Mi
        limits:
          cpu: 500m
          memory: 1Gi

      livenessProbe:
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 30
        periodSeconds: 10
        timeoutSeconds: 5
        failureThreshold: 3

      readinessProbe:
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 10
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 3

      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: false
```

---

#### Component: Frontend Service
**Resource Type**: Service
**Name**: `frontend-service`
**Type**: NodePort

**Specification**:
```yaml
type: NodePort
selector:
  app: frontend
ports:
- name: http
  port: 3000
  targetPort: 3000
  nodePort: 30000  # Or let Kubernetes assign
  protocol: TCP
```

**Access Method**:
- `minikube service frontend-service -n todo-app`
- Or: `kubectl port-forward svc/frontend-service 3000:3000 -n todo-app`

---

#### Component: Backend Service
**Resource Type**: Service
**Name**: `backend-service`
**Type**: ClusterIP (internal only)

**Specification**:
```yaml
type: ClusterIP
selector:
  app: backend
ports:
- name: http
  port: 8000
  targetPort: 8000
  protocol: TCP
```

**Access Method**: Only accessible from within cluster or via port-forward

---

#### Component: ConfigMap
**Resource Type**: ConfigMap
**Name**: `app-config`
**Purpose**: Non-sensitive configuration

**Data**:
```yaml
data:
  BACKEND_URL: "http://backend-service:8000"
  NODE_ENV: "production"
  LOG_LEVEL: "info"
```

---

#### Component: Secret
**Resource Type**: Secret
**Name**: `app-secrets`
**Type**: Opaque
**Purpose**: Sensitive credentials

**Data** (base64 encoded):
```yaml
stringData:
  DATABASE_URL: "<neon-postgresql-connection-string>"
  OPENAI_API_KEY: "<openai-api-key>"
  BETTER_AUTH_SECRET: "<shared-auth-secret>"
  BETTER_AUTH_URL: "http://localhost:30000"
```

**Creation Method**: Manually created before Helm install
```bash
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL=$DATABASE_URL \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  --from-literal=BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET \
  --from-literal=BETTER_AUTH_URL=$BETTER_AUTH_URL \
  -n todo-app
```

---

### 2.3 Helm Chart Structure

#### Chart Directory Layout
```
helm-chart/
└── todo-app/
    ├── Chart.yaml           # Chart metadata
    ├── values.yaml          # Default configuration
    ├── .helmignore         # Files to ignore
    ├── templates/
    │   ├── NOTES.txt                # Post-install instructions
    │   ├── _helpers.tpl             # Template helpers
    │   ├── frontend-deployment.yaml # Frontend deployment
    │   ├── frontend-service.yaml    # Frontend service
    │   ├── backend-deployment.yaml  # Backend deployment
    │   ├── backend-service.yaml     # Backend service
    │   ├── configmap.yaml           # ConfigMap
    │   └── namespace.yaml           # Namespace (optional)
    └── README.md            # Chart documentation
```

---

#### Chart.yaml
```yaml
apiVersion: v2
name: todo-app
description: Phase IV - Kubernetes deployment of Todo application with AI chatbot
type: application
version: 0.1.0
appVersion: "phase-4"
keywords:
  - todo
  - kubernetes
  - nextjs
  - fastapi
  - ai-chatbot
maintainers:
  - name: Hackathon Team
    email: team@hackathon.local
```

---

#### values.yaml Structure
```yaml
# Global settings
global:
  namespace: todo-app

# Frontend configuration
frontend:
  enabled: true
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never

  replicaCount: 2

  service:
    type: NodePort
    port: 3000
    nodePort: 30000

  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  env:
    nodeEnv: production
    backendUrl: "http://backend-service:8000"

  probes:
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      initialDelaySeconds: 10
      periodSeconds: 5

# Backend configuration
backend:
  enabled: true
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never

  replicaCount: 2

  service:
    type: ClusterIP
    port: 8000

  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 1Gi

  probes:
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      initialDelaySeconds: 10
      periodSeconds: 5

# ConfigMap data
config:
  backendUrl: "http://backend-service:8000"
  nodeEnv: "production"
  logLevel: "info"

# Secrets (reference only, created separately)
secrets:
  name: app-secrets
  # Actual values created manually:
  # - DATABASE_URL
  # - OPENAI_API_KEY
  # - BETTER_AUTH_SECRET
  # - BETTER_AUTH_URL
```

---

#### _helpers.tpl (Template Helpers)
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
phase: "4"
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## 3. Deployment Sequence

### Phase 1: Environment Preparation
1. **Install Prerequisites**
   ```bash
   # macOS
   brew install docker
   brew install minikube
   brew install kubectl
   brew install helm
   ```

2. **Start Minikube**
   ```bash
   minikube start --cpus=4 --memory=8192 --driver=docker
   ```

3. **Verify Cluster**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

---

### Phase 2: Image Building
1. **Build Frontend Image**
   ```bash
   cd frontend
   docker build -t todo-frontend:latest .
   cd ..
   ```

2. **Build Backend Image**
   ```bash
   cd backend
   docker build -t todo-backend:latest .
   cd ..
   ```

3. **Test Images Locally**
   ```bash
   # Test frontend
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
     todo-frontend:latest

   # Test backend
   docker run -p 8000:8000 \
     -e DATABASE_URL=$DATABASE_URL \
     -e OPENAI_API_KEY=$OPENAI_API_KEY \
     todo-backend:latest
   ```

4. **Load Images into Minikube**
   ```bash
   minikube image load todo-frontend:latest
   minikube image load todo-backend:latest
   ```

---

### Phase 3: Helm Chart Creation
1. **Initialize Chart**
   ```bash
   helm create todo-app
   # Customize templates
   ```

2. **Validate Chart**
   ```bash
   helm lint helm-chart/todo-app
   helm template todo-app helm-chart/todo-app --debug
   ```

---

### Phase 4: Deployment
1. **Create Namespace**
   ```bash
   kubectl create namespace todo-app
   ```

2. **Create Secrets**
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=DATABASE_URL=$DATABASE_URL \
     --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
     --from-literal=BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET \
     --from-literal=BETTER_AUTH_URL=http://localhost:30000 \
     -n todo-app
   ```

3. **Install Helm Chart**
   ```bash
   helm install todo-app helm-chart/todo-app \
     --namespace todo-app \
     --wait --timeout 5m
   ```

4. **Verify Deployment**
   ```bash
   kubectl get pods -n todo-app
   kubectl get services -n todo-app
   helm list -n todo-app
   ```

---

### Phase 5: Access Application
**Method 1: Minikube Service**
```bash
minikube service frontend-service -n todo-app
```

**Method 2: Port Forward**
```bash
kubectl port-forward svc/frontend-service 3000:3000 -n todo-app
# Open browser: http://localhost:3000
```

---

### Phase 6: Verification
1. **Check Pod Health**
   ```bash
   kubectl get pods -n todo-app
   kubectl describe pod <pod-name> -n todo-app
   kubectl logs -l app=frontend -n todo-app --tail=50
   kubectl logs -l app=backend -n todo-app --tail=50
   ```

2. **Test Application**
   - Login with credentials
   - Create a task
   - Use chatbot: "Show me all my tasks"
   - Verify all Phase III features work

3. **Check Resource Usage**
   ```bash
   kubectl top pods -n todo-app
   kubectl top nodes
   ```

---

## 4. Configuration Strategy

### 4.1 Environment Variables

**Frontend Environment Variables**:
| Variable | Source | Purpose |
|----------|--------|---------|
| NODE_ENV | ConfigMap | Set to "production" |
| NEXT_PUBLIC_API_URL | ConfigMap | Backend service URL |
| BETTER_AUTH_URL | Secret | Frontend URL for auth |

**Backend Environment Variables**:
| Variable | Source | Purpose |
|----------|--------|---------|
| DATABASE_URL | Secret | Neon PostgreSQL connection |
| OPENAI_API_KEY | Secret | OpenAI API access |
| BETTER_AUTH_SECRET | Secret | JWT signing secret |

---

### 4.2 Configuration Hierarchy

```
1. Hardcoded Defaults (in application code)
   ↓
2. Dockerfile ENV (container image)
   ↓
3. ConfigMap (non-sensitive config)
   ↓
4. Secrets (sensitive config)
   ↓
5. values.yaml (Helm deployment config)
   ↓
6. --set flags (Helm install/upgrade overrides)
```

**Precedence**: Lower levels override higher levels

---

## 5. Networking Architecture

### 5.1 Internal Networking

**Service Discovery**:
- Frontend pods resolve backend via DNS: `backend-service.todo-app.svc.cluster.local`
- Kubernetes CoreDNS provides service discovery
- No IP addresses hardcoded

**Load Balancing**:
- Service acts as internal load balancer
- Distributes traffic across pod replicas
- Uses iptables rules (default kube-proxy mode)

---

### 5.2 External Access

**Option 1: NodePort Service**
```
User → Minikube Node IP:30000 → frontend-service → Frontend Pods
```

**Option 2: Port Forwarding**
```
User → localhost:3000 → kubectl port-forward → frontend-service → Frontend Pods
```

**Option 3: Minikube Tunnel (Alternative)**
```bash
minikube tunnel
# Makes LoadBalancer services accessible on localhost
```

---

### 5.3 Egress Traffic

**Backend → External Services**:
- Neon PostgreSQL: Port 5432 (HTTPS connection)
- OpenAI API: Port 443 (HTTPS)
- DNS resolution via CoreDNS

**Network Policies**: Not implemented in Phase IV (future enhancement)

---

## 6. Storage Architecture

### 6.1 Ephemeral Storage
- Container filesystem is ephemeral
- No PersistentVolumes required
- Application logs to stdout/stderr
- No local file storage needed

### 6.2 Persistent Storage
- All persistent data in external Neon PostgreSQL
- Database connection pooling handled by backend
- Connection survives pod restarts

---

## 7. Security Architecture

### 7.1 Container Security

**Non-Root User**:
```dockerfile
# Frontend Dockerfile
USER node:node

# Backend Dockerfile
RUN useradd -m -u 1001 appuser
USER appuser
```

**Security Context**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false  # Next.js needs write access for cache
```

---

### 7.2 Secrets Management

**Kubernetes Secrets**:
- Type: Opaque
- Encoded: Base64 (not encrypted by default)
- Mounted as environment variables
- Not in Helm templates (created separately)

**Best Practices Implemented**:
- ✅ Secrets not in Git
- ✅ Secrets created before deployment
- ✅ Environment variables for sensitive data
- ❌ Encryption at rest (not implemented - future)
- ❌ RBAC for secrets access (not implemented - future)

---

### 7.3 Network Security

**Current State (Phase IV)**:
- All pods can communicate freely
- No Network Policies
- All egress traffic allowed

**Future Enhancements (Phase V)**:
- Network Policies to restrict pod-to-pod communication
- Egress filtering
- mTLS with service mesh

---

## 8. Observability Architecture

### 8.1 Health Checks

**Liveness Probe**:
- Purpose: Detect crashed containers
- Action: Restart container if fails
- Frontend: HTTP GET / port 3000
- Backend: HTTP GET /health port 8000

**Readiness Probe**:
- Purpose: Detect when container is ready for traffic
- Action: Remove from service endpoints if fails
- Same endpoints as liveness

**Startup Probe**: Not implemented (liveness/readiness sufficient)

---

### 8.2 Logging

**Log Collection**:
- Applications log to stdout/stderr
- Kubernetes captures logs automatically
- Access via: `kubectl logs <pod-name> -n todo-app`

**Log Format**:
- Backend: JSON structured logs
- Frontend: Plain text logs from Next.js

**Log Aggregation**: Not implemented in Phase IV (future: Elasticsearch, Loki)

---

### 8.3 Metrics

**Resource Metrics**:
- Metrics Server enabled in Minikube
- View with: `kubectl top pods`
- CPU and Memory usage visible

**Application Metrics**: Not implemented in Phase IV (future: Prometheus)

---

## 9. Upgrade Strategy

### 9.1 Helm Upgrade Process
```bash
# Make changes to code or values.yaml
helm upgrade todo-app helm-chart/todo-app -n todo-app --wait
```

**What Happens**:
1. Helm calculates diff between current and desired state
2. Applies changes to affected resources
3. Triggers rolling update for Deployments
4. Waits for new pods to become Ready
5. Terminates old pods

---

### 9.2 Rolling Update Strategy

**Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1  # Max 1 pod down during update
    maxSurge: 1        # Max 1 extra pod during update
```

**Update Flow**:
```
Initial State: Pod-1 (Running), Pod-2 (Running)
    ↓
Create Pod-3 (new version)
    ↓
Wait for Pod-3 to be Ready
    ↓
Terminate Pod-1
    ↓
Create Pod-4 (new version)
    ↓
Wait for Pod-4 to be Ready
    ↓
Terminate Pod-2
    ↓
Final State: Pod-3 (Running), Pod-4 (Running)
```

**Zero-Downtime**: At least 1 pod always available

---

### 9.3 Rollback Strategy

**Automatic Rollback**: If upgrade fails
```yaml
# In deployment spec (future enhancement)
progressDeadlineSeconds: 600
```

**Manual Rollback**:
```bash
# View revision history
helm history todo-app -n todo-app

# Rollback to previous version
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 3 -n todo-app
```

---

## 10. Scalability Architecture

### 10.1 Horizontal Scaling

**Manual Scaling**:
```bash
# Scale frontend
kubectl scale deployment frontend-deployment --replicas=3 -n todo-app

# Or via Helm
helm upgrade todo-app helm-chart/todo-app \
  --set frontend.replicaCount=3 \
  -n todo-app
```

**Automatic Scaling (HPA)**: Not implemented in Phase IV
```yaml
# Future enhancement
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### 10.2 Resource Limits

**Why Resource Limits Matter**:
- Prevent resource starvation
- Enable Kubernetes scheduling
- Cost prediction
- Autoscaling basis

**Tuning Strategy**:
1. Deploy with conservative limits
2. Monitor with `kubectl top pods`
3. Adjust requests/limits based on actual usage
4. Test under load

---

## 11. Disaster Recovery

### 11.1 Pod Failure

**Scenario**: Pod crashes
**Kubernetes Response**:
1. Liveness probe fails
2. Kubernetes restarts container
3. If restart fails repeatedly → CrashLoopBackOff
4. Service routes traffic to healthy pods

**Recovery Time**: <30 seconds

---

### 11.2 Node Failure

**Scenario**: Minikube node crashes (unlikely in local dev)
**Kubernetes Response**:
1. Pods marked as Unknown
2. After 5 minutes, pods rescheduled (if multiple nodes)
3. In Minikube (single node): Manual restart required

**For Phase IV**: Not applicable (single node)

---

### 11.3 Database Connection Loss

**Scenario**: Neon database unreachable
**Application Response**:
1. Backend connection pool fails
2. API requests return 500
3. Readiness probe fails
4. Pod removed from service
5. When DB recovers, connection pool reconnects
6. Readiness probe passes
7. Pod added back to service

**Recovery Time**: Automatic, ~10 seconds after DB recovers

---

## 12. Development Workflow

### 12.1 Local Development Cycle

```
Code Change
    ↓
Run Tests Locally
    ↓
Build Docker Image
    ↓
Load Image into Minikube
    ↓
Helm Upgrade (or kubectl delete pod for faster iteration)
    ↓
Verify in Browser
    ↓
Check Logs
    ↓
Iterate
```

---

### 12.2 Debugging Workflow

**Problem**: Pod not starting
```bash
kubectl get pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

**Problem**: Application error
```bash
kubectl logs -l app=backend -n todo-app --tail=100 -f
```

**Problem**: Can't access service
```bash
kubectl get services -n todo-app
kubectl port-forward svc/frontend-service 3000:3000 -n todo-app
curl http://localhost:3000
```

**Problem**: Database connection
```bash
kubectl exec -it <backend-pod> -n todo-app -- /bin/sh
# Inside pod:
env | grep DATABASE
curl http://localhost:8000/health
```

---

## 13. AI Operations Integration

### 13.1 Docker AI (Gordon)

**Use Cases**:
```bash
# Get image insights
docker ai "show me the size of all my images"
docker ai "what layers make up the todo-frontend image?"

# Optimization suggestions
docker ai "how can I make the todo-frontend image smaller?"
docker ai "suggest build improvements for this Dockerfile"

# Troubleshooting
docker ai "why is my container not starting?"
docker ai "explain this docker build error"
```

**Integration in Workflow**:
- Use Gordon during image optimization phase
- Document insights in image optimization section
- Compare AI suggestions with actual implementation

---

### 13.2 kubectl-ai

**Use Cases**:
```bash
# Deployment
kubectl-ai "deploy a 2-replica frontend with image todo-frontend:latest"

# Scaling
kubectl-ai "scale the frontend deployment to 3 replicas"

# Debugging
kubectl-ai "why are my backend pods not starting?"
kubectl-ai "show me resource usage of all pods in todo-app namespace"

# Information
kubectl-ai "list all services in todo-app namespace with their types"
kubectl-ai "show me the logs of the failing pod"
```

**Learning Approach**:
1. Try with kubectl-ai first
2. Ask kubectl-ai to explain the command it ran
3. Try the same with standard kubectl
4. Compare results

---

### 13.3 Kagent

**Use Cases**:
```bash
# Cluster Analysis
kagent "analyze the health of my Minikube cluster"
kagent "identify performance bottlenecks in todo-app namespace"

# Optimization
kagent "suggest resource optimizations for my deployments"
kagent "recommend scaling strategy based on current usage"

# Troubleshooting
kagent "diagnose why my pods are pending"
kagent "explain the cluster events from the last 10 minutes"
```

**Integration in Workflow**:
- Use kagent for cluster-wide insights
- Apply recommendations to values.yaml
- Document learnings in troubleshooting guide

---

## 14. Testing Strategy

### 14.1 Pre-Deployment Testing

**Docker Image Testing**:
```bash
# Test frontend locally
docker run --rm -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend:latest

# Test backend locally
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET \
  todo-backend:latest
```

**Helm Chart Validation**:
```bash
helm lint helm-chart/todo-app
helm template todo-app helm-chart/todo-app --debug > /tmp/rendered.yaml
kubectl apply --dry-run=client -f /tmp/rendered.yaml
```

---

### 14.2 Post-Deployment Testing

**Smoke Tests**:
1. All pods Running: `kubectl get pods -n todo-app`
2. All pods Ready: `kubectl get pods -n todo-app | grep "2/2"`
3. No errors in logs: `kubectl logs -l app=frontend -n todo-app | grep ERROR`
4. Health endpoint: `curl http://localhost:8000/health` (via port-forward)
5. Frontend loads: Open browser to NodePort

**Functional Tests**:
1. User login
2. Create task
3. View task list
4. Update task
5. Mark complete
6. Delete task
7. Use chatbot: "Add a task to test Kubernetes deployment"

---

### 14.3 Load Testing (Optional)

**Simple Load Test**:
```bash
# Install hey
go install github.com/rakyll/hey@latest

# Port-forward backend
kubectl port-forward svc/backend-service 8000:8000 -n todo-app

# Run load test
hey -n 1000 -c 10 http://localhost:8000/health

# Monitor pods
kubectl top pods -n todo-app
```

**Observation**:
- CPU/Memory usage
- Response times
- Error rates

---

## 15. Cleanup & Maintenance

### 15.1 Uninstall Application

**Full Cleanup**:
```bash
# Uninstall Helm release
helm uninstall todo-app -n todo-app

# Delete namespace (removes all resources)
kubectl delete namespace todo-app

# Remove images from Minikube
minikube image rm todo-frontend:latest
minikube image rm todo-backend:latest
```

---

### 15.2 Cluster Cleanup

**Stop Minikube**:
```bash
minikube stop
```

**Delete Minikube Cluster**:
```bash
minikube delete
```

**Fresh Start**:
```bash
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker
```

---

## 16. Handoff to Phase V

### 16.1 What Works in Phase IV

✅ Application containerized
✅ Deployed on local Kubernetes
✅ Helm chart created and tested
✅ All features functional
✅ Documentation complete

### 16.2 What Changes in Phase V

- **Target**: Cloud Kubernetes (DigitalOcean, Azure, or GCP)
- **New**: Container Registry (push images, don't use ImagePullPolicy: Never)
- **New**: Ingress Controller (replace NodePort)
- **New**: Kafka integration
- **New**: Dapr integration
- **New**: CI/CD pipeline
- **New**: Production monitoring

### 16.3 Reusable Artifacts

- ✅ Dockerfiles (may need registry tags)
- ✅ Helm chart (modify values.yaml for cloud)
- ✅ Kubernetes manifests (mostly unchanged)
- ✅ Configuration structure (same pattern)

---

## 17. Success Criteria Summary

| Criterion | Target | Verification Method |
|-----------|--------|-------------------|
| Images Built | 2 images | `docker images | grep todo` |
| Images Loaded | In Minikube | `minikube image ls | grep todo` |
| Helm Install | Success | `helm list -n todo-app` |
| Pods Running | 4 pods (2+2) | `kubectl get pods -n todo-app` |
| Pods Ready | All 2/2 | `kubectl get pods -n todo-app` |
| Frontend Access | HTTP 200 | Browser check |
| Backend Health | HTTP 200 | `curl /health` |
| Login Works | Success | Browser test |
| CRUD Works | All ops | Browser test |
| Chatbot Works | Responds | Browser test |
| Zero Errors | No ERRORs | `kubectl logs` |

---

## 18. Risk Mitigation

| Risk | Mitigation | Contingency |
|------|-----------|-------------|
| Image too large | Multi-stage builds, .dockerignore | Document size, optimize later |
| Pods crash | Health checks, resource limits | Check logs, adjust limits |
| Can't access service | Multiple access methods | Port-forward as fallback |
| Database connection fails | Connection string validation | Test connection before deploy |
| Helm install fails | Lint and template first | Debug with --debug flag |
| Minikube crashes | Adequate resources | Restart with correct flags |

---

**Plan Status**: ✅ Approved
**Ready for**: Task Breakdown (tasks.md)
**Next Step**: Create detailed task list with step-by-step instructions

---

**References**:
- Constitution: constitution.md
- Specification: spec.md
- Hackathon PDF: Pages 22-23 (Phase IV)
- Kubernetes Docs: kubernetes.io/docs
- Helm Docs: helm.sh/docs
