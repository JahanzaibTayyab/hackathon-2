# CI/CD Pipeline Documentation

## Overview

The Todo application uses GitHub Actions for continuous integration and deployment. The pipeline automatically builds, tests, and deploys changes to staging and production environments.

## Pipeline Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Commit    │────►│   Build &   │────►│   Docker    │────►│   Deploy    │
│   to main   │     │    Test     │     │   Push      │     │   Staging   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                           ┌─────────────┐
                                                           │   Deploy    │
                                                           │ Production  │
                                                           │ (Approval)  │
                                                           └─────────────┘
```

## Workflow File

Location: `.github/workflows/deploy.yml`

## Pipeline Stages

### 1. Build & Test

**Trigger**: All pushes and pull requests to `main` branch

**Steps**:
- Checkout code
- Setup Node.js 20 + pnpm
- Install frontend dependencies
- Run frontend tests
- Build frontend
- Setup Python 3.11 + uv
- Install backend dependencies
- Run backend tests
- Run linter (non-blocking)

### 2. Docker Build & Push

**Trigger**: Only on push to `main` (not PRs)

**Steps**:
- Setup Docker Buildx
- Login to Azure Container Registry
- Build and push frontend image
- Build and push backend image
- Tag with SHA and `latest`

### 3. Deploy to Staging

**Trigger**: After successful Docker build
**Environment**: `staging` (no approval required)

**Steps**:
- Azure CLI login
- Get AKS credentials
- Deploy Dapr components
- Helm upgrade with staging values
- Verify deployment
- Run smoke tests

### 4. Deploy to Production

**Trigger**: After successful staging deployment
**Environment**: `production` (requires approval)

**Steps**:
- Azure CLI login
- Get AKS credentials
- Deploy Dapr components
- Helm upgrade with production values
- Verify deployment
- Notify success

## GitHub Configuration

### Repository Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Azure service principal JSON |
| `ACR_USERNAME` | Azure Container Registry username |
| `ACR_PASSWORD` | Azure Container Registry password |

### Repository Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ACR_REGISTRY` | Registry URL | `todoappacr.azurecr.io` |
| `AZURE_RESOURCE_GROUP` | Resource group name | `todo-app-rg` |
| `AKS_CLUSTER_NAME` | AKS cluster name | `todo-app-aks` |
| `API_URL` | Backend API URL | `http://backend-service:8000` |

### Environments

1. **staging**
   - No protection rules
   - Auto-deploy on merge to main

2. **production**
   - Required reviewers configured
   - Manual approval before deploy

## Creating Azure Service Principal

```bash
az ad sp create-for-rbac \
  --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/todo-app-rg \
  --sdk-auth
```

Save the output as `AZURE_CREDENTIALS` secret.

## Creating Container Registry Credentials

```bash
# Get ACR credentials
az acr credential show --name todoappacr

# Or create a service principal for ACR
az ad sp create-for-rbac \
  --name github-actions-acr \
  --scopes /subscriptions/<sub-id>/resourceGroups/todo-app-rg/providers/Microsoft.ContainerRegistry/registries/todoappacr \
  --role acrpush
```

## Kubernetes Secrets Setup

Before the first deployment, create secrets in each namespace:

### Staging

```bash
kubectl create namespace staging

kubectl create secret generic todo-secrets -n staging \
  --from-literal=database-url='postgresql://...' \
  --from-literal=auth-secret='your-secret' \
  --from-literal=openai-api-key='sk-...'

kubectl create secret generic kafka-secrets -n staging \
  --from-literal=brokers='...' \
  --from-literal=username='...' \
  --from-literal=password='...'

kubectl create configmap todo-config -n staging \
  --from-literal=frontend-url='https://staging.todoapp.com' \
  --from-literal=cors-origins='https://staging.todoapp.com'
```

### Production

```bash
kubectl create namespace production

kubectl create secret generic todo-secrets -n production \
  --from-literal=database-url='postgresql://...' \
  --from-literal=auth-secret='your-prod-secret' \
  --from-literal=openai-api-key='sk-...'

kubectl create secret generic kafka-secrets -n production \
  --from-literal=brokers='...' \
  --from-literal=username='...' \
  --from-literal=password='...'

kubectl create configmap todo-config -n production \
  --from-literal=frontend-url='https://todoapp.com' \
  --from-literal=cors-origins='https://todoapp.com'
```

## Manual Deployment

If needed, deploy manually:

```bash
# Get AKS credentials
az aks get-credentials -g todo-app-rg -n todo-app-aks

# Deploy to staging
helm upgrade --install todo-app ./helm-chart/todo-app \
  -n staging \
  --set frontend.image.tag=<sha> \
  --set backend.image.tag=<sha> \
  --set dapr.enabled=true \
  -f helm-chart/todo-app/values-staging.yaml

# Deploy to production
helm upgrade --install todo-app ./helm-chart/todo-app \
  -n production \
  --set frontend.image.tag=<sha> \
  --set backend.image.tag=<sha> \
  --set dapr.enabled=true \
  -f helm-chart/todo-app/values-production.yaml
```

## Rollback Procedure

### Using Helm

```bash
# List releases
helm history todo-app -n production

# Rollback to previous revision
helm rollback todo-app <revision> -n production

# Rollback to specific revision
helm rollback todo-app 5 -n production
```

### Using kubectl

```bash
# Rollback deployment
kubectl rollout undo deployment/todo-release-backend -n production
kubectl rollout undo deployment/todo-release-frontend -n production

# Rollback to specific revision
kubectl rollout undo deployment/todo-release-backend -n production --to-revision=3
```

## Monitoring Pipeline

### View Workflow Runs

1. Go to repository → Actions tab
2. Select "Build and Deploy" workflow
3. View run details and logs

### Re-run Failed Jobs

1. Open failed workflow run
2. Click "Re-run failed jobs"
3. Or click "Re-run all jobs"

### Skip CI

Add `[skip ci]` to commit message to skip pipeline:

```bash
git commit -m "Update docs [skip ci]"
```

## Troubleshooting

### Build Failures

1. Check test logs in "Build & Test" job
2. Run tests locally: `pnpm test` / `uv run pytest`
3. Check lint errors (warnings won't fail build)

### Docker Push Failures

1. Verify ACR credentials are valid
2. Check registry URL in variables
3. Ensure service principal has `acrpush` role

### Deployment Failures

1. Check Helm upgrade logs
2. Verify secrets exist in namespace
3. Check pod events: `kubectl describe pod -n <namespace>`
4. View pod logs: `kubectl logs -n <namespace> <pod-name>`

### Approval Pending

1. Go to workflow run
2. Click "Review deployments"
3. Select "production" environment
4. Add comment and approve
