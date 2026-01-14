# Phase IV: Local Kubernetes Deployment - Tasks

## BREAKDOWN - Atomic, Testable Work Units

**Phase**: Phase IV - Local Kubernetes Deployment
**From**: constitution.md, spec.md, plan.md
**Status**: Task List Approved - Ready for Implementation

---

## Task Execution Guidelines

### Task Format
Each task follows this structure:
- **Task ID**: Unique identifier (e.g., T-A01)
- **Title**: Brief description
- **From Spec**: Links to requirements (FR-X.X, AC-X)
- **Preconditions**: Must be complete before starting
- **Steps**: Detailed implementation steps
- **Outputs**: Expected artifacts
- **Verification**: How to confirm success
- **Estimated Time**: Approximate duration
- **Status**: ⏳ Pending | 🚧 In Progress | ✅ Complete

### Task Groups
- **Group A**: Environment Setup (T-A01 to T-A03)
- **Group B**: Docker Images (T-B01 to T-B06)
- **Group C**: Helm Chart (T-C01 to T-C11)
- **Group D**: Deployment (T-D01 to T-D08)
- **Group E**: Testing (T-E01 to T-E05)
- **Group F**: AI Operations (T-F01 to T-F03) - Optional
- **Group G**: Documentation (T-G01 to T-G05)
- **Group H**: Optimization (T-H01 to T-H04)

---

## GROUP A: Environment Setup

### T-A01: Install Prerequisites
**Status**: ⏳ Pending
**From Spec**: FR-6.3
**Preconditions**: None
**Estimated Time**: 15 minutes

**Steps**:
```bash
# macOS with Homebrew
brew install docker
brew install minikube
brew install kubectl
brew install helm

# Or Linux
# Follow official installation guides for each tool
```

**Outputs**:
- Docker Desktop installed
- Minikube installed
- kubectl installed
- Helm installed

**Verification**:
```bash
docker --version      # Should show Docker version
minikube version      # Should show Minikube version
kubectl version --client  # Should show kubectl version
helm version          # Should show Helm version
```

**Success Criteria**:
- ✅ All four tools respond with version numbers
- ✅ Docker Desktop running (check menu bar icon)

---

### T-A02: Install AI Tools (Optional)
**Status**: ⏳ Pending
**From Spec**: FR-6.1, FR-6.2
**Preconditions**: T-A01 complete
**Estimated Time**: 10 minutes

**Steps**:
```bash
# Install kubectl-ai
brew install kubectl-ai  # Or follow official installation

# Install kagent
# Follow installation instructions from GitHub

# Enable Docker AI (Gordon) in Docker Desktop
# Docker Desktop > Settings > Beta features > Toggle "Docker AI"
```

**Outputs**:
- kubectl-ai installed (optional)
- kagent installed (optional)
- Docker AI enabled (optional)

**Verification**:
```bash
kubectl-ai --version
docker ai "what can you do?"
```

**Success Criteria**:
- ✅ Tools respond correctly OR
- ✅ Documented as "not available, using standard CLI"

---

### T-A03: Start Minikube Cluster
**Status**: ⏳ Pending
**From Spec**: FR-2.1, AC-2
**Preconditions**: T-A01 complete, Docker Desktop running
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Wait for cluster to be ready
```

**Outputs**:
- Running Minikube cluster
- Kubernetes context set to minikube

**Verification**:
```bash
minikube status              # Should show "Running"
kubectl cluster-info         # Should show cluster info
kubectl get nodes            # Should show 1 node in Ready state
```

**Success Criteria**:
- ✅ `minikube status` shows all components "Running"
- ✅ `kubectl get nodes` shows node in "Ready" state
- ✅ Docker shows minikube container running

---

## GROUP B: Docker Containerization

### T-B01: Create Frontend Dockerfile
**Status**: ⏳ Pending
**From Spec**: FR-1.1, AC-1
**Preconditions**: Phase III frontend code exists
**Estimated Time**: 20 minutes

**Steps**:
Create `frontend/Dockerfile`:

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
# Copy source code
COPY . .

# Build Next.js app
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app

# Set to production
ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start application
CMD ["node", "server.js"]
```

**Outputs**:
- `frontend/Dockerfile`

**Verification**:
- ✅ File exists
- ✅ Syntax is valid (check with `docker build --check`)

**Success Criteria**:
- ✅ Dockerfile follows multi-stage build pattern
- ✅ Uses node:20-alpine base image
- ✅ Runs as non-root user

---

### T-B02: Create Backend Dockerfile
**Status**: ⏳ Pending
**From Spec**: FR-1.2, AC-1
**Preconditions**: Phase III backend code exists
**Estimated Time**: 15 minutes

**Steps**:
Create `backend/Dockerfile`:

```dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Outputs**:
- `backend/Dockerfile`

**Verification**:
- ✅ File exists
- ✅ Syntax is valid

**Success Criteria**:
- ✅ Uses python:3.13-slim base image
- ✅ Uses uv for dependency management
- ✅ Runs as non-root user
- ✅ Includes health check

---

### T-B03: Create .dockerignore Files
**Status**: ⏳ Pending
**From Spec**: FR-1.3, AC-1
**Preconditions**: T-B01, T-B02 complete
**Estimated Time**: 5 minutes

**Steps**:
Create `frontend/.dockerignore`:
```
node_modules
.next
.git
.env*
*.md
README*
.gitignore
Dockerfile
docker-compose.yml
```

Create `backend/.dockerignore`:
```
__pycache__
*.pyc
.git
.env*
*.md
README*
.gitignore
Dockerfile
docker-compose.yml
.pytest_cache
tests
```

**Outputs**:
- `frontend/.dockerignore`
- `backend/.dockerignore`

**Verification**:
- ✅ Both files exist
- ✅ Common patterns excluded

**Success Criteria**:
- ✅ Build speed improved
- ✅ Image size reduced

---

### T-B04: Build Frontend Docker Image
**Status**: ⏳ Pending
**From Spec**: FR-1.1, AC-1
**Preconditions**: T-B01, T-B03 complete
**Estimated Time**: 10 minutes (first build)

**Steps**:
```bash
# Navigate to project root
cd /Users/zaib/Panaverse/hackathon-2

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Check image size
docker images todo-frontend:latest
```

**Outputs**:
- Docker image `todo-frontend:latest`

**Verification**:
```bash
# Check image exists
docker images | grep todo-frontend

# Test run locally
docker run --rm -p 3001:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -e BETTER_AUTH_URL=http://localhost:3000 \
  todo-frontend:latest

# Open browser: http://localhost:3001
# Should see login page
```

**Success Criteria**:
- ✅ Build completes without errors
- ✅ Image size <500MB
- ✅ Container starts and serves content
- ✅ No security warnings in build output

---

### T-B05: Build Backend Docker Image
**Status**: ⏳ Pending
**From Spec**: FR-1.2, AC-1
**Preconditions**: T-B02, T-B03 complete
**Estimated Time**: 10 minutes (first build)

**Steps**:
```bash
# Navigate to project root
cd /Users/zaib/Panaverse/hackathon-2

# Build backend image
docker build -t todo-backend:latest ./backend

# Check image size
docker images todo-backend:latest
```

**Outputs**:
- Docker image `todo-backend:latest`

**Verification**:
```bash
# Check image exists
docker images | grep todo-backend

# Test run locally
docker run --rm -p 8001:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET \
  todo-backend:latest

# Test health endpoint
curl http://localhost:8001/health
# Should return {"status": "healthy"}
```

**Success Criteria**:
- ✅ Build completes without errors
- ✅ Image size <300MB
- ✅ Container starts successfully
- ✅ Health endpoint responds with 200

---

### T-B06: Load Images into Minikube
**Status**: ⏳ Pending
**From Spec**: FR-2.1, AC-1
**Preconditions**: T-A03, T-B04, T-B05 complete
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Load frontend image
minikube image load todo-frontend:latest

# Load backend image
minikube image load todo-backend:latest

# Verify images are in Minikube
minikube image ls | grep todo
```

**Outputs**:
- Frontend image in Minikube's Docker daemon
- Backend image in Minikube's Docker daemon

**Verification**:
```bash
minikube image ls | grep todo-frontend
minikube image ls | grep todo-backend
```

**Success Criteria**:
- ✅ Both images listed in `minikube image ls`
- ✅ No errors during load

---

## GROUP C: Helm Chart Creation

### T-C01: Initialize Helm Chart Structure
**Status**: ⏳ Pending
**From Spec**: FR-3.1, AC-5
**Preconditions**: Helm installed (T-A01)
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Navigate to project root
cd /Users/zaib/Panaverse/hackathon-2

# Create helm-chart directory if not exists
mkdir -p helm-chart

# Initialize Helm chart
cd helm-chart
helm create todo-app

# Review generated structure
tree todo-app
```

**Outputs**:
- `helm-chart/todo-app/` directory
- Default Helm chart structure

**Verification**:
```bash
ls helm-chart/todo-app/
# Should show: Chart.yaml, values.yaml, templates/, charts/, .helmignore
```

**Success Criteria**:
- ✅ Chart directory created
- ✅ Standard Helm structure present

---

### T-C02: Update Chart.yaml Metadata
**Status**: ⏳ Pending
**From Spec**: FR-3.1, AC-5
**Preconditions**: T-C01 complete
**Estimated Time**: 5 minutes

**Steps**:
Edit `helm-chart/todo-app/Chart.yaml`:

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

**Outputs**:
- Updated `Chart.yaml`

**Verification**:
```bash
helm lint helm-chart/todo-app
# Should pass with no errors
```

**Success Criteria**:
- ✅ Valid Chart.yaml
- ✅ Metadata matches project

---

### T-C03: Create values.yaml Configuration
**Status**: ⏳ Pending
**From Spec**: FR-3.2, FR-3.3, AC-5
**Preconditions**: T-C02 complete
**Estimated Time**: 20 minutes

**Steps**:
Replace `helm-chart/todo-app/values.yaml` with:

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
    pullPolicy: Never  # Use local image from Minikube

  replicaCount: 2

  service:
    type: NodePort
    port: 3000
    nodePort: 30000  # Fixed port for easy access

  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  probes:
    liveness:
      path: /
      port: 3000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    readiness:
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

# Backend configuration
backend:
  enabled: true

  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never  # Use local image from Minikube

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
      path: /health
      port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    readiness:
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

# ConfigMap data (non-sensitive)
config:
  backendUrl: "http://backend-service:8000"
  nodeEnv: "production"
  logLevel: "info"

# Secrets reference (created separately)
secrets:
  name: app-secrets
  # Actual secrets created manually via kubectl:
  # - DATABASE_URL
  # - OPENAI_API_KEY
  # - BETTER_AUTH_SECRET
  # - BETTER_AUTH_URL

# Labels
labels:
  app: todo-app
  phase: "4"
  project: hackathon-2
```

**Outputs**:
- `helm-chart/todo-app/values.yaml`

**Verification**:
```bash
# Check YAML syntax
helm lint helm-chart/todo-app

# Preview rendered templates
helm template todo-app helm-chart/todo-app
```

**Success Criteria**:
- ✅ Valid YAML syntax
- ✅ All configuration options documented
- ✅ Comments explain each section

---

### T-C04: Create Frontend Deployment Template
**Status**: ⏳ Pending
**From Spec**: FR-2.2, AC-2, AC-5
**Preconditions**: T-C03 complete
**Estimated Time**: 25 minutes

**Steps**:
Create `helm-chart/todo-app/templates/frontend-deployment.yaml`:

```yaml
{{- if .Values.frontend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: frontend
    component: ui
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app: frontend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app: frontend
        component: ui
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        env:
        - name: NODE_ENV
          value: {{ .Values.config.nodeEnv | quote }}
        - name: NEXT_PUBLIC_API_URL
          value: {{ .Values.config.backendUrl | quote }}
        - name: BETTER_AUTH_URL
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secrets.name }}
              key: BETTER_AUTH_URL
        resources:
          {{- toYaml .Values.frontend.resources | nindent 10 }}
        livenessProbe:
          httpGet:
            path: {{ .Values.frontend.probes.liveness.path }}
            port: {{ .Values.frontend.probes.liveness.port }}
          initialDelaySeconds: {{ .Values.frontend.probes.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.frontend.probes.liveness.periodSeconds }}
          timeoutSeconds: {{ .Values.frontend.probes.liveness.timeoutSeconds }}
          failureThreshold: {{ .Values.frontend.probes.liveness.failureThreshold }}
        readinessProbe:
          httpGet:
            path: {{ .Values.frontend.probes.readiness.path }}
            port: {{ .Values.frontend.probes.readiness.port }}
          initialDelaySeconds: {{ .Values.frontend.probes.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.frontend.probes.readiness.periodSeconds }}
          timeoutSeconds: {{ .Values.frontend.probes.readiness.timeoutSeconds }}
          failureThreshold: {{ .Values.frontend.probes.readiness.failureThreshold }}
        securityContext:
          {{- toYaml .Values.frontend.securityContext | nindent 10 }}
{{- end }}
```

**Outputs**:
- `helm-chart/todo-app/templates/frontend-deployment.yaml`

**Verification**:
```bash
helm template todo-app helm-chart/todo-app | grep -A 50 "kind: Deployment" | grep frontend
```

**Success Criteria**:
- ✅ Template renders without errors
- ✅ All values from values.yaml used
- ✅ Proper labels and selectors

---

### T-C05: Create Backend Deployment Template
**Status**: ⏳ Pending
**From Spec**: FR-2.3, AC-2, AC-5
**Preconditions**: T-C03 complete
**Estimated Time**: 25 minutes

**Steps**:
Create `helm-chart/todo-app/templates/backend-deployment.yaml`:

```yaml
{{- if .Values.backend.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: backend
    component: api
spec:
  replicas: {{ .Values.backend.replicaCount }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app: backend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app: backend
        component: api
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secrets.name }}
              key: DATABASE_URL
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secrets.name }}
              key: OPENAI_API_KEY
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secrets.name }}
              key: BETTER_AUTH_SECRET
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
        livenessProbe:
          httpGet:
            path: {{ .Values.backend.probes.liveness.path }}
            port: {{ .Values.backend.probes.liveness.port }}
          initialDelaySeconds: {{ .Values.backend.probes.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.backend.probes.liveness.periodSeconds }}
          timeoutSeconds: {{ .Values.backend.probes.liveness.timeoutSeconds }}
          failureThreshold: {{ .Values.backend.probes.liveness.failureThreshold }}
        readinessProbe:
          httpGet:
            path: {{ .Values.backend.probes.readiness.path }}
            port: {{ .Values.backend.probes.readiness.port }}
          initialDelaySeconds: {{ .Values.backend.probes.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.backend.probes.readiness.periodSeconds }}
          timeoutSeconds: {{ .Values.backend.probes.readiness.timeoutSeconds }}
          failureThreshold: {{ .Values.backend.probes.readiness.failureThreshold }}
        securityContext:
          {{- toYaml .Values.backend.securityContext | nindent 10 }}
{{- end }}
```

**Outputs**:
- `helm-chart/todo-app/templates/backend-deployment.yaml`

**Verification**:
```bash
helm template todo-app helm-chart/todo-app | grep -A 50 "kind: Deployment" | grep backend
```

**Success Criteria**:
- ✅ Template renders without errors
- ✅ All secrets referenced correctly
- ✅ Health checks configured

---

### T-C06: Create Frontend Service Template
**Status**: ⏳ Pending
**From Spec**: FR-2.4, AC-2, AC-5
**Preconditions**: T-C04 complete
**Estimated Time**: 10 minutes

**Steps**:
Create `helm-chart/todo-app/templates/frontend-service.yaml`:

```yaml
{{- if .Values.frontend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: frontend
spec:
  type: {{ .Values.frontend.service.type }}
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
    app: frontend
  ports:
  - name: http
    port: {{ .Values.frontend.service.port }}
    targetPort: http
    protocol: TCP
    {{- if and (eq .Values.frontend.service.type "NodePort") .Values.frontend.service.nodePort }}
    nodePort: {{ .Values.frontend.service.nodePort }}
    {{- end }}
{{- end }}
```

**Outputs**:
- `helm-chart/todo-app/templates/frontend-service.yaml`

**Verification**:
```bash
helm template todo-app helm-chart/todo-app | grep -A 10 "kind: Service" | grep frontend
```

**Success Criteria**:
- ✅ Service type NodePort
- ✅ Port 30000 specified
- ✅ Selector matches deployment

---

### T-C07: Create Backend Service Template
**Status**: ⏳ Pending
**From Spec**: FR-2.5, AC-2, AC-5
**Preconditions**: T-C05 complete
**Estimated Time**: 10 minutes

**Steps**:
Create `helm-chart/todo-app/templates/backend-service.yaml`:

```yaml
{{- if .Values.backend.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: backend
spec:
  type: {{ .Values.backend.service.type }}
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
    app: backend
  ports:
  - name: http
    port: {{ .Values.backend.service.port }}
    targetPort: http
    protocol: TCP
{{- end }}
```

**Outputs**:
- `helm-chart/todo-app/templates/backend-service.yaml`

**Verification**:
```bash
helm template todo-app helm-chart/todo-app | grep -A 10 "kind: Service" | grep backend
```

**Success Criteria**:
- ✅ Service type ClusterIP
- ✅ Port 8000
- ✅ Selector matches deployment

---

### T-C08: Create ConfigMap Template
**Status**: ⏳ Pending
**From Spec**: FR-4.1, AC-6
**Preconditions**: T-C03 complete
**Estimated Time**: 10 minutes

**Steps**:
Create `helm-chart/todo-app/templates/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "todo-app.fullname" . }}-config
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
data:
  BACKEND_URL: {{ .Values.config.backendUrl | quote }}
  NODE_ENV: {{ .Values.config.nodeEnv | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
```

**Outputs**:
- `helm-chart/todo-app/templates/configmap.yaml`

**Verification**:
```bash
helm template todo-app helm-chart/todo-app | grep -A 10 "kind: ConfigMap"
```

**Success Criteria**:
- ✅ ConfigMap contains public config only
- ✅ No sensitive data

---

### T-C09: Update _helpers.tpl Template Functions
**Status**: ⏳ Pending
**From Spec**: FR-3.1, AC-5
**Preconditions**: T-C01 complete
**Estimated Time**: 15 minutes

**Steps**:
Edit `helm-chart/todo-app/templates/_helpers.tpl`:

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
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
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
project: hackathon-2
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**Outputs**:
- Updated `_helpers.tpl`

**Verification**:
```bash
helm template todo-app helm-chart/todo-app | grep "phase:"
# Should show phase: "4" in all resources
```

**Success Criteria**:
- ✅ Helper functions work correctly
- ✅ Labels consistent across resources

---

### T-C10: Create NOTES.txt Post-Install Instructions
**Status**: ⏳ Pending
**From Spec**: FR-3.1, AC-4, AC-5
**Preconditions**: T-C06, T-C07 complete
**Estimated Time**: 10 minutes

**Steps**:
Create `helm-chart/todo-app/templates/NOTES.txt`:

```
🎉 Todo App deployed successfully!

Phase: IV - Kubernetes Deployment
Release: {{ .Release.Name }}
Namespace: {{ .Values.global.namespace }}

📊 DEPLOYMENT STATUS
-------------------
Frontend: {{ .Values.frontend.replicaCount }} replica(s)
Backend:  {{ .Values.backend.replicaCount }} replica(s)

Check pod status:
  kubectl get pods -n {{ .Values.global.namespace }}

View logs:
  kubectl logs -l app=frontend -n {{ .Values.global.namespace }}
  kubectl logs -l app=backend -n {{ .Values.global.namespace }}

🌐 ACCESS APPLICATION
---------------------

{{- if eq .Values.frontend.service.type "NodePort" }}
Method 1: Minikube Service
  minikube service {{ include "todo-app.fullname" . }}-frontend -n {{ .Values.global.namespace }}

Method 2: Port Forward
  kubectl port-forward svc/{{ include "todo-app.fullname" . }}-frontend 3000:3000 -n {{ .Values.global.namespace }}
  Then open: http://localhost:3000
{{- end }}

Backend API:
  kubectl port-forward svc/{{ include "todo-app.fullname" . }}-backend 8000:8000 -n {{ .Values.global.namespace }}
  Health: curl http://localhost:8000/health

🔧 MANAGEMENT COMMANDS
---------------------
Upgrade:
  helm upgrade {{ .Release.Name }} ./helm-chart/todo-app -n {{ .Values.global.namespace }}

Rollback:
  helm rollback {{ .Release.Name }} -n {{ .Values.global.namespace }}

Uninstall:
  helm uninstall {{ .Release.Name }} -n {{ .Values.global.namespace }}

📖 DOCUMENTATION
----------------
For troubleshooting, see: ./deployment/TROUBLESHOOTING.md
For full docs, see: ./README.md

✨ Happy tasking!
```

**Outputs**:
- `helm-chart/todo-app/templates/NOTES.txt`

**Verification**:
```bash
helm install todo-app helm-chart/todo-app -n todo-app --dry-run
# Should show NOTES content at the end
```

**Success Criteria**:
- ✅ Clear access instructions
- ✅ Helpful commands provided
- ✅ Templates render correctly

---

### T-C11: Validate Complete Helm Chart
**Status**: ⏳ Pending
**From Spec**: FR-3.4, AC-5
**Preconditions**: T-C02 through T-C10 complete
**Estimated Time**: 10 minutes

**Steps**:
```bash
# Lint the chart
helm lint helm-chart/todo-app

# Template the chart (dry-run)
helm template todo-app helm-chart/todo-app --debug > /tmp/rendered.yaml

# Validate rendered YAML
kubectl apply --dry-run=client -f /tmp/rendered.yaml

# Check template output
cat /tmp/rendered.yaml | less
```

**Outputs**:
- Validated Helm chart
- Rendered YAML for review

**Verification**:
```bash
helm lint helm-chart/todo-app
# Should show: ==> Linting ./helm-chart/todo-app
#              1 chart(s) linted, 0 chart(s) failed
```

**Success Criteria**:
- ✅ `helm lint` passes with no warnings
- ✅ `helm template` renders valid YAML
- ✅ `kubectl apply --dry-run` succeeds
- ✅ All resources present in rendered output

---

## GROUP D: Deployment & Verification

### T-D01: Create Kubernetes Namespace
**Status**: ⏳ Pending
**From Spec**: FR-2.1, AC-2
**Preconditions**: T-A03 complete (Minikube running)
**Estimated Time**: 2 minutes

**Steps**:
```bash
# Create namespace
kubectl create namespace todo-app

# Add labels
kubectl label namespace todo-app phase=4 project=hackathon-2
```

**Outputs**:
- Namespace `todo-app` created

**Verification**:
```bash
kubectl get namespace todo-app
kubectl describe namespace todo-app
```

**Success Criteria**:
- ✅ Namespace exists
- ✅ Labels applied

---

### T-D02: Create Kubernetes Secrets
**Status**: ⏳ Pending
**From Spec**: FR-4.2, AC-6
**Preconditions**: T-D01 complete, environment variables set
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Ensure environment variables are set
echo $DATABASE_URL         # Should show Neon connection string
echo $OPENAI_API_KEY       # Should show sk-...
echo $BETTER_AUTH_SECRET   # Should show secret key

# Create secret
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=BETTER_AUTH_URL="http://localhost:30000" \
  -n todo-app

# Verify secret created (but don't show values)
kubectl get secret app-secrets -n todo-app
```

**Outputs**:
- Secret `app-secrets` in namespace `todo-app`

**Verification**:
```bash
kubectl get secret app-secrets -n todo-app
kubectl describe secret app-secrets -n todo-app
# Should show keys but not values
```

**Success Criteria**:
- ✅ Secret exists
- ✅ All four keys present
- ✅ Values not visible in kubectl output

---

### T-D03: Install Helm Chart
**Status**: ⏳ Pending
**From Spec**: FR-3.4, AC-2, AC-5
**Preconditions**: T-C11, T-D01, T-D02, T-B06 complete
**Estimated Time**: 10 minutes

**Steps**:
```bash
# Navigate to project root
cd /Users/zaib/Panaverse/hackathon-2

# Install Helm chart with wait flag
helm install todo-app helm-chart/todo-app \
  --namespace todo-app \
  --wait \
  --timeout 5m

# The NOTES will be displayed automatically
```

**Outputs**:
- Helm release `todo-app` installed
- All Kubernetes resources created

**Verification**:
```bash
# Check Helm release
helm list -n todo-app

# Check release status
helm status todo-app -n todo-app
```

**Success Criteria**:
- ✅ Helm install completes without errors
- ✅ NOTES.txt displayed with access instructions
- ✅ Release status: "deployed"

---

### T-D04: Verify Pod Status
**Status**: ⏳ Pending
**From Spec**: AC-2
**Preconditions**: T-D03 complete
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Watch pods come up
kubectl get pods -n todo-app -w

# Wait for all pods to be Running and Ready (2/2)
# Press Ctrl+C when all pods are ready

# Final check
kubectl get pods -n todo-app
```

**Expected Output**:
```
NAME                                  READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxxxxxx-xxxxx      2/2     Running   0          1m
todo-app-backend-xxxxxxxxx-xxxxx      2/2     Running   0          1m
todo-app-frontend-xxxxxxxxx-xxxxx     2/2     Running   0          1m
todo-app-frontend-xxxxxxxxx-xxxxx     2/2     Running   0          1m
```

**Verification**:
```bash
kubectl get pods -n todo-app | grep -c "2/2"
# Should output: 4
```

**Success Criteria**:
- ✅ All 4 pods in Running state
- ✅ All pods show 2/2 Ready
- ✅ No CrashLoopBackOff
- ✅ Pods ready within 2 minutes

---

### T-D05: Check Pod Logs for Errors
**Status**: ⏳ Pending
**From Spec**: AC-2, AC-7
**Preconditions**: T-D04 complete
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Check frontend logs
kubectl logs -l app=frontend -n todo-app --tail=50

# Check backend logs
kubectl logs -l app=backend -n todo-app --tail=50

# Look for ERROR or FATAL messages
kubectl logs -l app=backend -n todo-app | grep -i error
```

**Outputs**:
- Log output from all pods

**Verification**:
```bash
# Should see successful startup messages
# Backend should show: "Application startup complete"
# Frontend should show: "Ready on http://0.0.0.0:3000"
```

**Success Criteria**:
- ✅ No ERROR or FATAL log messages
- ✅ Backend shows successful DB connection
- ✅ Frontend shows successful startup
- ✅ No uncaught exceptions

---

### T-D06: Verify Services
**Status**: ⏳ Pending
**From Spec**: AC-2
**Preconditions**: T-D04 complete
**Estimated Time**: 2 minutes

**Steps**:
```bash
# List services
kubectl get services -n todo-app

# Describe frontend service
kubectl describe service todo-app-frontend -n todo-app

# Describe backend service
kubectl describe service todo-app-backend -n todo-app
```

**Expected Output**:
```
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
todo-app-backend    ClusterIP   10.96.xxx.xxx   <none>        8000/TCP         2m
todo-app-frontend   NodePort    10.96.xxx.xxx   <none>        3000:30000/TCP   2m
```

**Verification**:
```bash
# Frontend should have NodePort 30000
kubectl get service todo-app-frontend -n todo-app -o jsonpath='{.spec.ports[0].nodePort}'
# Should output: 30000

# Backend should have ClusterIP (no NodePort)
kubectl get service todo-app-backend -n todo-app -o jsonpath='{.spec.type}'
# Should output: ClusterIP
```

**Success Criteria**:
- ✅ Frontend service type: NodePort on port 30000
- ✅ Backend service type: ClusterIP on port 8000
- ✅ Services have endpoints (pods selected)

---

### T-D07: Access Frontend Application
**Status**: ⏳ Pending
**From Spec**: AC-3
**Preconditions**: T-D06 complete
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Method 1: Minikube service (opens browser automatically)
minikube service todo-app-frontend -n todo-app

# Or Method 2: Port forward (manual)
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app
# Then open browser: http://localhost:3000
```

**Outputs**:
- Browser opens to frontend application

**Verification**:
- Open browser to frontend URL
- Should see login page
- No console errors (check browser DevTools)

**Success Criteria**:
- ✅ Frontend loads in browser
- ✅ Login page displays correctly
- ✅ No JavaScript errors in console
- ✅ Page renders within 2 seconds

---

### T-D08: Test Backend API Health Endpoint
**Status**: ⏳ Pending
**From Spec**: AC-2, AC-4
**Preconditions**: T-D06 complete
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Port forward backend service
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app &

# Wait a moment for port-forward to establish
sleep 2

# Test health endpoint
curl http://localhost:8000/health

# Test API docs
curl http://localhost:8000/docs

# Kill port-forward
pkill -f "port-forward.*backend"
```

**Expected Output**:
```json
{"status": "healthy", "database": "connected"}
```

**Verification**:
```bash
curl -s http://localhost:8000/health | jq .status
# Should output: "healthy"
```

**Success Criteria**:
- ✅ Health endpoint returns 200
- ✅ Response shows "healthy" status
- ✅ Database shows "connected"
- ✅ Response time <200ms

---

## GROUP E: Application Testing

### T-E01: Test User Authentication
**Status**: ⏳ Pending
**From Spec**: AC-4
**Preconditions**: T-D07 complete, browser open to frontend
**Estimated Time**: 5 minutes

**Steps**:
1. Navigate to frontend URL (from T-D07)
2. Click "Sign In" or navigate to login page
3. Enter existing user credentials:
   - Email: (use your test email from Phase III)
   - Password: (use your test password)
4. Click "Sign In"
5. Verify redirect to dashboard

**Expected Behavior**:
- Login form submits
- No errors displayed
- Redirects to `/dashboard` or home page
- User name/email shown in header

**Verification**:
```bash
# Check backend logs for authentication
kubectl logs -l app=backend -n todo-app --tail=20 | grep -i auth
# Should show successful JWT verification
```

**Success Criteria**:
- ✅ Login succeeds
- ✅ JWT token stored in browser
- ✅ Redirected to authenticated page
- ✅ No authentication errors in logs

---

### T-E02: Test Task CRUD Operations
**Status**: ⏳ Pending
**From Spec**: AC-4
**Preconditions**: T-E01 complete, user logged in
**Estimated Time**: 10 minutes

**Steps**:

**Create Task**:
1. Click "Add Task" or "+" button
2. Enter title: "Test Kubernetes Deployment"
3. Enter description: "Verify Phase IV works correctly"
4. Click "Create" or "Save"
5. Verify task appears in list

**View Task**:
1. Locate the newly created task in list
2. Verify title and description displayed
3. Verify status shows "Pending" or unchecked

**Update Task**:
1. Click "Edit" on the test task
2. Change title to: "Test Kubernetes Deployment ✅"
3. Click "Save"
4. Verify updated title in list

**Mark Complete**:
1. Click checkbox or "Complete" on the task
2. Verify task marked as complete
3. Verify visual indicator (strikethrough, checkmark, etc.)

**Delete Task**:
1. Click "Delete" on the test task
2. Confirm deletion if prompted
3. Verify task removed from list

**Verification**:
```bash
# Check backend logs for API calls
kubectl logs -l app=backend -n todo-app --tail=50 | grep -E "POST|PUT|DELETE|PATCH"
# Should show successful CRUD operations
```

**Success Criteria**:
- ✅ Task created successfully
- ✅ Task appears in list immediately
- ✅ Task updated correctly
- ✅ Task marked complete
- ✅ Task deleted successfully
- ✅ All operations <1 second response time

---

### T-E03: Test AI Chatbot Functionality
**Status**: ⏳ Pending
**From Spec**: AC-4
**Preconditions**: T-E01 complete, user logged in
**Estimated Time**: 10 minutes

**Steps**:
1. Navigate to Chat interface (e.g., `/chat` page)
2. Type message: "Add a task to test the chatbot"
3. Send message
4. Wait for response
5. Verify:
   - Chatbot responds with confirmation
   - Task was actually created
   - Task visible in task list

6. Type message: "Show me all my tasks"
7. Wait for response
8. Verify:
   - Chatbot lists tasks
   - Includes the task just created

9. Type message: "Mark the chatbot test task as complete"
10. Wait for response
11. Verify:
    - Chatbot confirms completion
    - Task marked complete in task list

**Verification**:
```bash
# Check backend logs for OpenAI API calls
kubectl logs -l app=backend -n todo-app --tail=100 | grep -i openai
# Should show successful API calls

# Check for MCP tool calls
kubectl logs -l app=backend -n todo-app --tail=100 | grep -E "add_task|list_tasks|complete_task"
```

**Success Criteria**:
- ✅ Chat interface loads correctly
- ✅ Chatbot responds to messages
- ✅ Natural language understood
- ✅ MCP tools executed correctly
- ✅ Tasks created/modified via chat
- ✅ Response time <5 seconds per message

---

### T-E04: Verify Database Connectivity
**Status**: ⏳ Pending
**From Spec**: FR-4.3, AC-5
**Preconditions**: T-D05 complete
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Check backend logs for database connection
kubectl logs -l app=backend -n todo-app | grep -i database

# Look for connection success messages
kubectl logs -l app=backend -n todo-app | grep -i "connected to database"

# Or exec into backend pod and test connection
BACKEND_POD=$(kubectl get pods -n todo-app -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $BACKEND_POD -n todo-app -- python -c "
from sqlmodel import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()
print('Database connection successful!')
conn.close()
"
```

**Expected Output**:
```
Database connection successful!
```

**Verification**:
```bash
# Verify no database connection errors in logs
kubectl logs -l app=backend -n todo-app | grep -i "database.*error"
# Should return nothing (no matches)
```

**Success Criteria**:
- ✅ Backend connects to Neon database
- ✅ No connection errors in logs
- ✅ Database queries execute successfully
- ✅ Connection pool working

---

### T-E05: Test Resource Usage
**Status**: ⏳ Pending
**From Spec**: NFR-1
**Preconditions**: T-D04 complete, application running for 5+ minutes
**Estimated Time**: 5 minutes

**Steps**:
```bash
# Install metrics-server if not already installed
minikube addons enable metrics-server

# Wait for metrics to be available (1-2 minutes)
sleep 60

# Check pod resource usage
kubectl top pods -n todo-app

# Check node resource usage
kubectl top nodes
```

**Expected Output**:
```
NAME                           CPU(cores)   MEMORY(bytes)
todo-app-backend-xxx-xxx       50m          200Mi
todo-app-backend-xxx-xxx       50m          200Mi
todo-app-frontend-xxx-xxx      30m          100Mi
todo-app-frontend-xxx-xxx      30m          100Mi
```

**Verification**:
```bash
# Verify pods are within resource limits
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].resources.limits.memory}{"\n"}{end}'
```

**Success Criteria**:
- ✅ All pods show reasonable CPU/Memory usage
- ✅ No pods close to resource limits
- ✅ Backend CPU <200m, Memory <500Mi
- ✅ Frontend CPU <100m, Memory <300Mi

---

## GROUP F: AI Operations (Optional)

### T-F01: Demonstrate Docker AI (Gordon)
**Status**: ⏳ Pending (Optional)
**From Spec**: FR-6.1
**Preconditions**: T-A02 complete, Gordon enabled
**Estimated Time**: 10 minutes

**Steps**:
```bash
# Show image information
docker ai "show me all images with 'todo' in the name"

# Get size analysis
docker ai "what is the total size of todo-frontend and todo-backend images?"

# Ask for optimization suggestions
docker ai "how can I make the todo-backend image smaller?"

# Compare images
docker ai "compare the todo-frontend and todo-backend images"

# Get build insights
docker ai "explain the layers in the todo-frontend image"
```

**Outputs**:
- AI-generated insights about images
- Optimization suggestions

**Documentation**:
- Save commands and responses to `deployment/AIOPS.md`
- Document any optimizations applied

**Success Criteria**:
- ✅ Gordon responds to queries
- ✅ Useful insights generated
- ✅ Commands documented

---

### T-F02: Demonstrate kubectl-ai
**Status**: ⏳ Pending (Optional)
**From Spec**: FR-6.2
**Preconditions**: T-A02 complete, kubectl-ai installed
**Estimated Time**: 15 minutes

**Steps**:
```bash
# Query pod status
kubectl-ai "show me all pods in todo-app namespace with their status"

# Scale deployment
kubectl-ai "show me how to scale the frontend deployment to 3 replicas"
# Note: Don't actually scale, just get the command

# Debugging assistance
kubectl-ai "how do I check why a pod is not starting?"

# Resource query
kubectl-ai "show me resource usage of all pods in todo-app namespace"

# Service information
kubectl-ai "list all services in todo-app namespace with their types and ports"

# Log analysis
kubectl-ai "how do I view logs from all backend pods?"
```

**Outputs**:
- kubectl-ai responses
- Equivalent kubectl commands

**Documentation**:
- Save commands to `deployment/AIOPS.md`
- Show both AI and standard CLI versions

**Success Criteria**:
- ✅ kubectl-ai provides helpful responses
- ✅ Generated commands work correctly
- ✅ Both approaches documented

---

### T-F03: Demonstrate Kagent (Optional)
**Status**: ⏳ Pending (Optional)
**From Spec**: FR-6.2
**Preconditions**: T-A02 complete, kagent installed
**Estimated Time**: 10 minutes

**Steps**:
```bash
# Analyze cluster health
kagent "analyze the health of my Minikube cluster"

# Check resource optimization
kagent "suggest resource optimizations for pods in todo-app namespace"

# Performance analysis
kagent "identify any performance issues in my cluster"

# Best practices check
kagent "review my todo-app deployments for Kubernetes best practices"
```

**Outputs**:
- Cluster analysis report
- Optimization recommendations

**Documentation**:
- Save insights to `deployment/AIOPS.md`
- Implement valid recommendations

**Success Criteria**:
- ✅ Kagent provides cluster insights
- ✅ Recommendations are actionable
- ✅ Insights documented

---

## GROUP G: Documentation

### T-G01: Create Deployment README
**Status**: ⏳ Pending
**From Spec**: AC-8
**Preconditions**: All deployment tasks (Group D) complete
**Estimated Time**: 30 minutes

**Steps**:
Create `deployment/README.md` with:

**Table of Contents**:
1. Prerequisites
2. Quick Start
3. Detailed Setup
4. Deployment Steps
5. Accessing the Application
6. Verification
7. Troubleshooting (link to TROUBLESHOOTING.md)
8. Cleanup

**Content Structure**:
```markdown
# Phase IV: Kubernetes Deployment Guide

## Prerequisites
- Docker Desktop 4.53+
- Minikube 1.32+
- kubectl 1.28+
- Helm 3.0+
- Phase III application working

## Quick Start
[5-minute deployment steps]

## Detailed Setup
[Step-by-step with explanations]

## Accessing the Application
[Methods to access frontend and backend]

## Verification Checklist
[ ] All pods running
[ ] Services accessible
[ ] Application works
[etc.]

## Troubleshooting
See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## Cleanup
[Uninstall instructions]
```

**Outputs**:
- `deployment/README.md`

**Verification**:
- Follow the README yourself to verify completeness
- Test on a fresh terminal session

**Success Criteria**:
- ✅ Complete prerequisites list
- ✅ Step-by-step instructions
- ✅ Copy-pasteable commands
- ✅ Clear section headers
- ✅ Troubleshooting linked

---

### T-G02: Create Helm Chart Documentation
**Status**: ⏳ Pending
**From Spec**: AC-8
**Preconditions**: T-C11 complete
**Estimated Time**: 20 minutes

**Steps**:
Create `helm-chart/todo-app/README.md` with:

**Content**:
- Chart description
- Installation instructions
- Configuration options (all values.yaml parameters)
- Examples of common configurations
- Upgrade/rollback instructions

**Format**:
```markdown
# Todo App Helm Chart

## Installation
[helm install command]

## Configuration
| Parameter | Description | Default |
|-----------|-------------|---------|
| frontend.replicaCount | Number of frontend replicas | 2 |
[etc.]

## Examples
### Custom Replicas
[example]

### Custom Resources
[example]
```

**Outputs**:
- `helm-chart/todo-app/README.md`

**Verification**:
- All values.yaml parameters documented
- Examples are valid

**Success Criteria**:
- ✅ All configuration options documented
- ✅ Examples provided
- ✅ Installation steps clear

---

### T-G03: Update Root README
**Status**: ⏳ Pending
**From Spec**: AC-8
**Preconditions**: T-G01 complete
**Estimated Time**: 15 minutes

**Steps**:
Update `/Users/zaib/Panaverse/hackathon-2/README.md`:

**Add Section**:
```markdown
## Phase IV: Kubernetes Deployment

The application is now deployed on local Kubernetes (Minikube).

### Quick Deploy
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Build and load images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Deploy with Helm
kubectl create namespace todo-app
kubectl create secret generic app-secrets --from-env-file=.env -n todo-app
helm install todo-app helm-chart/todo-app -n todo-app

# Access application
minikube service todo-app-frontend -n todo-app
```

### Documentation
- Deployment Guide: [deployment/README.md](./deployment/README.md)
- Troubleshooting: [deployment/TROUBLESHOOTING.md](./deployment/TROUBLESHOOTING.md)
- Helm Chart: [helm-chart/todo-app/README.md](./helm-chart/todo-app/README.md)
```

**Outputs**:
- Updated root README

**Success Criteria**:
- ✅ Phase IV section added
- ✅ Quick deploy commands work
- ✅ Links to detailed docs

---

### T-G04: Create Troubleshooting Guide
**Status**: ⏳ Pending
**From Spec**: AC-8
**Preconditions**: Testing complete, common issues identified
**Estimated Time**: 20 minutes

**Steps**:
Create `deployment/TROUBLESHOOTING.md` covering:

**Common Issues**:
1. Pods not starting (ImagePullBackOff)
2. Database connection failures
3. Service not accessible
4. Health checks failing
5. Out of memory errors
6. Minikube not starting

**Format**:
```markdown
# Troubleshooting Guide

## Issue: Pods stuck in ImagePullBackOff

**Symptom**:
[description]

**Cause**:
[explanation]

**Solution**:
[step-by-step fix]

**Verification**:
[how to confirm it's fixed]

---

[Repeat for each issue]
```

**Outputs**:
- `deployment/TROUBLESHOOTING.md`

**Success Criteria**:
- ✅ At least 6 common issues covered
- ✅ Clear symptoms and solutions
- ✅ Commands are copy-pasteable
- ✅ Verification steps included

---

### T-G05: Create Demo Video
**Status**: ⏳ Pending
**From Spec**: AC-9
**Preconditions**: Application fully working (Group E complete)
**Estimated Time**: 30 minutes

**Steps**:

**Preparation**:
1. Clean terminal
2. Browser with no extra tabs
3. Minikube running
4. Application deployed

**Script** (90 seconds):
1. [0-15s] Show Minikube cluster
   - `kubectl get nodes`
   - `kubectl get pods -n todo-app`

2. [15-30s] Show Helm deployment
   - `helm list -n todo-app`
   - `helm status todo-app -n todo-app`

3. [30-60s] Show application in browser
   - Open frontend
   - Log in
   - Create a task: "Demo Phase IV"

4. [60-90s] Show chatbot feature
   - Open chat
   - Type: "Show me my tasks"
   - Chatbot lists tasks including "Demo Phase IV"
   - Type: "Mark Demo Phase IV as complete"
   - Chatbot confirms

**Recording**:
- Use screen recording tool (macOS: Cmd+Shift+5)
- Or use NotebookLM
- Ensure audio is clear or add captions
- Keep under 90 seconds

**Outputs**:
- Demo video file (MP4)
- Upload to accessible location (YouTube, Drive, etc.)
- Add link to README

**Verification**:
- Video plays correctly
- Duration <90 seconds
- Audio/captions clear
- All features demonstrated

**Success Criteria**:
- ✅ Video recorded and uploaded
- ✅ Duration under 90 seconds
- ✅ Shows cluster, deployment, and working app
- ✅ Demonstrates one feature (chatbot)
- ✅ Clear audio or captions

---

## GROUP H: Optimization

### T-H01: Optimize Docker Images
**Status**: ⏳ Pending
**From Spec**: FR-1.3, AC-1
**Preconditions**: T-B04, T-B05 complete
**Estimated Time**: 20 minutes

**Steps**:

**Check Current Sizes**:
```bash
docker images | grep todo
```

**Frontend Optimization**:
1. Review Dockerfile for unnecessary layers
2. Ensure .dockerignore is comprehensive
3. Check if node_modules in final image
4. Verify only standalone output included

**Backend Optimization**:
1. Use slim Python base image (already doing)
2. Remove unnecessary Python packages
3. Clear pip cache
4. Combine RUN commands to reduce layers

**Rebuild and Compare**:
```bash
# Rebuild images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Check new sizes
docker images | grep todo

# Compare
docker history todo-frontend:latest
docker history todo-backend:latest
```

**Outputs**:
- Optimized Docker images

**Verification**:
```bash
# Frontend should be <500MB
# Backend should be <300MB
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep todo
```

**Success Criteria**:
- ✅ Frontend image <500MB
- ✅ Backend image <300MB
- ✅ No unnecessary files in images
- ✅ Images still work correctly

---

### T-H02: Fine-tune Resource Limits
**Status**: ⏳ Pending
**From Spec**: NFR-1
**Preconditions**: T-E05 complete, actual usage known
**Estimated Time**: 15 minutes

**Steps**:

**Analyze Current Usage**:
```bash
# Check actual resource usage
kubectl top pods -n todo-app

# Check over time (sample for 5 minutes)
for i in {1..5}; do
  echo "Sample $i:"
  kubectl top pods -n todo-app
  sleep 60
done
```

**Adjust values.yaml**:
Based on actual usage, update resource requests/limits:

```yaml
# If frontend uses ~50m CPU and ~150Mi Memory:
frontend:
  resources:
    requests:
      cpu: 50m        # Slightly below average
      memory: 128Mi   # Slightly below average
    limits:
      cpu: 200m       # 4x request for burst
      memory: 512Mi   # Room for growth
```

**Apply Changes**:
```bash
helm upgrade todo-app helm-chart/todo-app -n todo-app
kubectl get pods -n todo-app -w
```

**Outputs**:
- Updated values.yaml with realistic limits

**Verification**:
```bash
kubectl describe pod <frontend-pod> -n todo-app | grep -A 5 "Limits:"
kubectl describe pod <backend-pod> -n todo-app | grep -A 5 "Limits:"
```

**Success Criteria**:
- ✅ Limits based on actual usage
- ✅ Requests allow efficient scheduling
- ✅ Limits prevent resource starvation
- ✅ Pods still work after adjustment

---

### T-H03: Add Comprehensive Health Checks
**Status**: ⏳ Pending
**From Spec**: FR-5.1, AC-7
**Preconditions**: Application deployed
**Estimated Time**: 15 minutes

**Steps**:

**Verify Current Health Checks**:
```bash
kubectl describe pod <pod-name> -n todo-app | grep -A 10 "Liveness:"
kubectl describe pod <pod-name> -n todo-app | grep -A 10 "Readiness:"
```

**Adjust If Needed**:
Review values.yaml health check settings:
- Initial delay: Long enough for startup
- Period: Frequent enough to detect issues
- Timeout: Reasonable for response time
- Failure threshold: Not too aggressive

**Test Health Checks**:
```bash
# Simulate backend failure (kill process)
BACKEND_POD=$(kubectl get pods -n todo-app -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec $BACKEND_POD -n todo-app -- pkill -9 uvicorn

# Watch Kubernetes restart it
kubectl get pods -n todo-app -w
```

**Outputs**:
- Verified health checks

**Verification**:
```bash
kubectl describe pod <pod-name> -n todo-app | grep -E "Liveness|Readiness"
# Should show both probes configured
```

**Success Criteria**:
- ✅ Liveness probes configured
- ✅ Readiness probes configured
- ✅ Probes use correct endpoints
- ✅ Kubernetes restarts failed containers

---

### T-H04: Test Helm Upgrade (Zero Downtime)
**Status**: ⏳ Pending
**From Spec**: FR-3.4
**Preconditions**: Application deployed and working
**Estimated Time**: 10 minutes

**Steps**:

**Make a Minor Change**:
```yaml
# In values.yaml, change:
frontend:
  replicaCount: 3  # Was 2
```

**Upgrade with Watch**:
In terminal 1:
```bash
kubectl get pods -n todo-app -w
```

In terminal 2:
```bash
helm upgrade todo-app helm-chart/todo-app -n todo-app
```

**Observe Rolling Update**:
- New pods created
- Wait for new pods to be Ready
- Old pods terminated
- At all times, at least 1 frontend pod Running

**Test During Upgrade**:
In terminal 3:
```bash
# Continuously test frontend availability
while true; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:30000
  sleep 1
done
```

**Outputs**:
- Successful zero-downtime upgrade

**Verification**:
```bash
# Check current replica count
kubectl get deployment todo-app-frontend -n todo-app
# Should show 3/3

# Check revision
helm history todo-app -n todo-app
# Should show 2 revisions
```

**Success Criteria**:
- ✅ Upgrade completes successfully
- ✅ No downtime (all curl requests succeed)
- ✅ Rolling update strategy works
- ✅ New replica count applied

---

## Implementation Order Summary

### Day 1: Setup & Containerization
1. **Group A**: Environment Setup (30 min)
   - T-A01: Install Prerequisites
   - T-A02: Install AI Tools (optional)
   - T-A03: Start Minikube

2. **Group B**: Containerization (60 min)
   - T-B01: Frontend Dockerfile
   - T-B02: Backend Dockerfile
   - T-B03: .dockerignore files
   - T-B04: Build Frontend Image
   - T-B05: Build Backend Image
   - T-B06: Load into Minikube

**Checkpoint**: Docker images built and loaded ✅

---

### Day 2: Helm Chart Creation
3. **Group C**: Helm Chart (165 min = 2.75 hours)
   - T-C01: Initialize Helm Chart
   - T-C02: Update Chart.yaml
   - T-C03: Create values.yaml
   - T-C04: Frontend Deployment template
   - T-C05: Backend Deployment template
   - T-C06: Frontend Service template
   - T-C07: Backend Service template
   - T-C08: ConfigMap template
   - T-C09: Update _helpers.tpl
   - T-C10: Create NOTES.txt
   - T-C11: Validate Helm Chart

**Checkpoint**: Helm chart complete and validated ✅

---

### Day 3: Deployment & Testing
4. **Group D**: Deployment (39 min)
   - T-D01: Create Namespace
   - T-D02: Create Secrets
   - T-D03: Install Helm Chart
   - T-D04: Verify Pod Status
   - T-D05: Check Logs
   - T-D06: Verify Services
   - T-D07: Access Frontend
   - T-D08: Test Backend API

5. **Group E**: Testing (35 min)
   - T-E01: Test Authentication
   - T-E02: Test CRUD Operations
   - T-E03: Test Chatbot
   - T-E04: Verify Database
   - T-E05: Test Resource Usage

**Checkpoint**: Application deployed and working ✅

---

### Day 4: Polish & Documentation
6. **Group F**: AI Operations (35 min, optional)
   - T-F01: Docker AI demo
   - T-F02: kubectl-ai demo
   - T-F03: Kagent demo

7. **Group G**: Documentation (115 min)
   - T-G01: Deployment README
   - T-G02: Helm Chart docs
   - T-G03: Update Root README
   - T-G04: Troubleshooting Guide
   - T-G05: Demo Video

8. **Group H**: Optimization (60 min)
   - T-H01: Optimize Images
   - T-H02: Fine-tune Resources
   - T-H03: Health Checks
   - T-H04: Test Upgrade

**Checkpoint**: Phase IV Complete! 🎉

---

## Total Estimated Time
- **Core Tasks** (A, B, C, D, E, G, H): ~8-10 hours
- **Optional AI Tasks** (F): +35 minutes
- **With breaks and debugging**: ~2-3 days

---

## Success Checklist

Use this checklist to verify Phase IV completion:

### Environment
- [ ] Docker Desktop running
- [ ] Minikube cluster running
- [ ] kubectl connected to Minikube
- [ ] Helm installed

### Images
- [ ] Frontend image built (<500MB)
- [ ] Backend image built (<300MB)
- [ ] Both images loaded in Minikube
- [ ] Images tagged correctly

### Helm Chart
- [ ] Chart structure created
- [ ] All templates present
- [ ] values.yaml complete
- [ ] `helm lint` passes
- [ ] NOTES.txt informative

### Deployment
- [ ] Namespace created
- [ ] Secrets created
- [ ] Helm install successful
- [ ] All pods Running (4/4)
- [ ] All pods Ready (2/2)
- [ ] No errors in logs

### Services
- [ ] Frontend service NodePort accessible
- [ ] Backend service ClusterIP working
- [ ] Services have endpoints

### Application
- [ ] Frontend loads in browser
- [ ] Login works
- [ ] Create task works
- [ ] View tasks works
- [ ] Update task works
- [ ] Mark complete works
- [ ] Delete task works
- [ ] Chatbot responds
- [ ] All Phase III features work

### Database
- [ ] Backend connects to Neon
- [ ] No connection errors
- [ ] Data persists across pod restarts

### Documentation
- [ ] deployment/README.md complete
- [ ] deployment/TROUBLESHOOTING.md complete
- [ ] helm-chart/todo-app/README.md complete
- [ ] Root README updated
- [ ] Demo video recorded (<90s)

### Optional
- [ ] Docker AI demonstrated
- [ ] kubectl-ai demonstrated
- [ ] Kagent demonstrated
- [ ] AI operations documented

---

## Next Steps After Phase IV

Once all tasks complete:
1. ✅ Commit all changes to Git
2. ✅ Push to GitHub
3. ✅ Submit Phase IV via form
4. ✅ Prepare for Phase V (Cloud Deployment)

---

**Tasks Status**: Ready for Implementation
**Start Date**: TBD
**Target Completion**: 3-4 days
**Next Phase**: Phase V - Cloud Deployment (DigitalOcean/Azure/GCP)
