# Todo App - Kubernetes Deployment (Phase IV)

This directory contains the Helm chart for deploying the Todo application with AI Chatbot to a local Kubernetes cluster using Minikube.

## Overview

The deployment consists of:
- **Frontend**: Next.js application (NodePort service on port 30080)
- **Backend**: FastAPI application (ClusterIP service on port 8000)
- **Database**: Neon PostgreSQL (external, managed)
- **Secrets**: Kubernetes secrets for sensitive configuration

## Prerequisites

Ensure you have the following tools installed:

```bash
# Check versions
docker --version        # Docker 20.10+
minikube version       # Minikube 1.30+
kubectl version        # kubectl 1.27+
helm version           # Helm 3.12+
```

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=7680 --driver=docker

# Verify cluster is running
minikube status
```

### 2. Build and Load Docker Images

```bash
# Navigate to project root
cd /Users/zaib/Panaverse/hackathon-2

# Build frontend image
docker build -t todo-frontend:latest -f frontend/Dockerfile ./frontend

# Build backend image
docker build -t todo-backend:latest -f backend/Dockerfile ./backend

# Load images into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify images are loaded
minikube image ls | grep todo
```

### 3. Create Kubernetes Secrets

Create a secret with your database credentials and API keys:

```bash
kubectl create secret generic todo-secrets \
  '--from-literal=database-url=YOUR_DATABASE_URL' \
  '--from-literal=auth-secret=YOUR_BETTER_AUTH_SECRET' \
  '--from-literal=openai-api-key=YOUR_OPENAI_API_KEY'
```

**Important**: Replace the placeholder values with actual credentials from your `.env` files.

### 4. Deploy with Helm

```bash
# Navigate to helm-chart directory
cd /Users/zaib/Panaverse/hackathon-2/helm-chart

# Install the chart
helm install todo-release todo-app --wait --timeout=5m

# Verify deployment
kubectl get all -l app.kubernetes.io/name=todo-app
```

### 5. Access the Application

#### Option 1: Port Forwarding (Recommended for macOS/Docker)

```bash
# Forward frontend port
kubectl port-forward service/todo-release-todo-app-frontend 3000:3000

# Open browser
open http://localhost:3000
```

#### Option 2: Minikube Service (Alternative)

```bash
# Get service URL (creates tunnel)
minikube service todo-release-todo-app-frontend --url

# Or open directly in browser
minikube service todo-release-todo-app-frontend
```

#### Option 3: NodePort with Minikube IP (Linux)

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Access application
open http://$MINIKUBE_IP:30080
```

## Architecture

### Services

| Service | Type | Port | Access |
|---------|------|------|--------|
| Frontend | NodePort | 3000:30080 | External via NodePort or port-forward |
| Backend | ClusterIP | 8000 | Internal only (accessed by frontend) |

### Deployments

Both frontend and backend run as single-replica deployments with:
- Resource limits: 500m CPU, 512Mi memory
- Resource requests: 250m CPU, 256Mi memory
- Health checks: Liveness and readiness probes
- Security: Non-root user, minimal capabilities

## Monitoring & Debugging

### Check Pod Status

```bash
# View all pods
kubectl get pods -l app.kubernetes.io/name=todo-app

# Detailed pod info
kubectl describe pod <pod-name>

# Pod events
kubectl get events --sort-by='.lastTimestamp'
```

### View Logs

```bash
# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend --tail=50 -f

# Backend logs
kubectl logs -l app.kubernetes.io/component=backend --tail=50 -f

# Specific pod logs
kubectl logs <pod-name> -f
```

### Execute Commands in Pods

```bash
# Shell into frontend
kubectl exec -it deployment/todo-release-todo-app-frontend -- sh

# Shell into backend
kubectl exec -it deployment/todo-release-todo-app-backend -- sh

# Test internal connectivity
kubectl exec deployment/todo-release-todo-app-frontend -- \
  wget -qO- http://todo-release-todo-app-backend:8000/health
```

### Check Services and Endpoints

```bash
# List services
kubectl get svc -l app.kubernetes.io/name=todo-app

# Check endpoints
kubectl get endpoints

# Describe service
kubectl describe svc todo-release-todo-app-frontend
```

## Configuration

### Helm Values

Key configuration in `values.yaml`:

```yaml
frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never  # Use local images
  service:
    type: NodePort
    nodePort: 30080

backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never
  service:
    type: ClusterIP
```

### Environment Variables

Environment variables are injected via:
1. **Direct values** in `values.yaml` (e.g., `NODE_ENV=production`)
2. **Secrets** referenced via `secretKeyRef` (e.g., `DATABASE_URL`, `OPENAI_API_KEY`)

## Common Operations

### Update Application

After code changes, rebuild and redeploy:

```bash
# Rebuild images
docker build -t todo-frontend:latest -f frontend/Dockerfile ./frontend
docker build -t todo-backend:latest -f backend/Dockerfile ./backend

# Reload into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Restart deployments
kubectl rollout restart deployment/todo-release-todo-app-frontend
kubectl rollout restart deployment/todo-release-todo-app-backend
```

### Scale Deployments

```bash
# Scale frontend to 2 replicas
kubectl scale deployment todo-release-todo-app-frontend --replicas=2

# Scale backend to 3 replicas
kubectl scale deployment todo-release-todo-app-backend --replicas=3
```

### Update Configuration

```bash
# Edit values
nano todo-app/values.yaml

# Upgrade release
helm upgrade todo-release todo-app --wait
```

### Uninstall

```bash
# Remove helm release
helm uninstall todo-release

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube (optional)
minikube stop
```

## Troubleshooting

### Pods Not Starting

**Symptoms**: Pods stuck in `Pending`, `ContainerCreating`, or `CrashLoopBackOff`

**Solutions**:
1. Check pod events: `kubectl describe pod <pod-name>`
2. Verify secrets exist: `kubectl get secret todo-secrets`
3. Check resource availability: `kubectl top nodes`
4. View logs: `kubectl logs <pod-name>`

### ImagePullBackOff Error

**Symptoms**: Pod shows `ImagePullBackOff` or `ErrImagePull`

**Solutions**:
1. Verify images in Minikube: `minikube image ls | grep todo`
2. Reload images: `minikube image load todo-frontend:latest`
3. Check `pullPolicy` is set to `Never` in values.yaml

### Connection Refused / Timeout

**Symptoms**: Cannot access application via browser

**Solutions**:
1. **macOS/Docker users**: Use port-forward instead of NodePort
   ```bash
   kubectl port-forward service/todo-release-todo-app-frontend 3000:3000
   ```
2. Verify pods are running: `kubectl get pods`
3. Check service endpoints: `kubectl get endpoints`
4. Test internal connectivity:
   ```bash
   kubectl exec deployment/todo-release-todo-app-frontend -- \
     wget -qO- http://localhost:3000
   ```

### Backend Not Reachable from Frontend

**Symptoms**: Frontend cannot connect to backend API

**Solutions**:
1. Verify backend service: `kubectl get svc todo-release-todo-app-backend`
2. Check backend logs: `kubectl logs -l app.kubernetes.io/component=backend`
3. Test connectivity:
   ```bash
   kubectl exec deployment/todo-release-todo-app-frontend -- \
     wget -qO- http://todo-release-todo-app-backend:8000/health
   ```

### Secret Not Found

**Symptoms**: Pods fail with "Secret not found" error

**Solutions**:
1. Create secrets: See step 3 in Quick Start
2. Verify secret exists: `kubectl get secret todo-secrets`
3. Check secret keys: `kubectl describe secret todo-secrets`

### Database Connection Issues

**Symptoms**: Backend logs show database connection errors

**Solutions**:
1. Verify `DATABASE_URL` in secret is correct
2. Check Neon PostgreSQL is accessible from cluster
3. Test connection from backend pod:
   ```bash
   kubectl exec deployment/todo-release-todo-app-backend -- \
     python -c "import psycopg2; print('Connected')"
   ```

## Validation

### Helm Chart Validation

```bash
# Lint chart
helm lint todo-app

# Dry-run installation
helm install test-release todo-app --dry-run --debug

# Template rendering
helm template test-release todo-app
```

### Application Health Checks

```bash
# Backend health
kubectl exec deployment/todo-release-todo-app-backend -- \
  wget -qO- http://localhost:8000/health

# Frontend health (within cluster)
kubectl exec deployment/todo-release-todo-app-backend -- \
  wget -qO- http://todo-release-todo-app-frontend:3000
```

## Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review pod logs and events
3. Consult Kubernetes documentation
4. File an issue in the project repository
