# Dapr Setup Guide

## Overview

Dapr (Distributed Application Runtime) provides the event-driven messaging infrastructure for the Todo application. This guide covers setting up Dapr for both local development and cloud deployment.

## Prerequisites

- Kubernetes cluster (Minikube for local, AKS for cloud)
- kubectl configured
- Helm 3.x installed
- Docker installed

## Local Development Setup

### 1. Install Dapr CLI

```bash
# macOS
brew install dapr/tap/dapr-cli

# Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify installation
dapr --version
```

### 2. Initialize Dapr on Kubernetes

```bash
# Initialize Dapr on your Kubernetes cluster
dapr init -k --wait

# Verify installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-operator          dapr-system  True     Running  1         1.13.x   1m
dapr-sidecar-injector  dapr-system  True     Running  1         1.13.x   1m
dapr-placement-server  dapr-system  True     Running  1         1.13.x   1m
dapr-sentry            dapr-system  True     Running  1         1.13.x   1m
```

### 3. Deploy Kafka (Strimzi)

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
kubectl wait deployment/strimzi-cluster-operator \
  --for=condition=available \
  --timeout=300s \
  -n kafka

# Deploy Kafka cluster
kubectl apply -f helm-chart/kafka/kafka-cluster.yaml

# Create topics
kubectl apply -f helm-chart/kafka/topics.yaml
```

### 4. Deploy Dapr Components

```bash
# Apply pub/sub component
kubectl apply -f helm-chart/dapr-components/pubsub.yaml

# Apply subscriptions
kubectl apply -f helm-chart/dapr-components/subscription.yaml
```

### 5. Deploy Application with Dapr

```bash
# Deploy with Dapr enabled
helm upgrade --install todo-release helm-chart/todo-app \
  --set dapr.enabled=true \
  --wait
```

## Cloud Deployment (Azure AKS)

### 1. Install Dapr on AKS

Using Azure extension (recommended):
```bash
az k8s-extension create \
  --cluster-type managedClusters \
  --cluster-name todo-app-aks \
  --resource-group todo-app-rg \
  --name dapr \
  --extension-type Microsoft.Dapr
```

Using Helm (generic):
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait
```

### 2. Create Kafka Secrets

```bash
kubectl create secret generic kafka-secrets \
  --namespace production \
  --from-literal=brokers='<redpanda-bootstrap-url>' \
  --from-literal=username='<sasl-username>' \
  --from-literal=password='<sasl-password>'
```

### 3. Deploy Cloud Dapr Components

```bash
kubectl apply -f helm-chart/dapr-components/cloud/pubsub.yaml -n production
kubectl apply -f helm-chart/dapr-components/subscription.yaml -n production
```

## Dapr Configuration

### Pod Annotations

The Helm chart automatically adds these annotations when `dapr.enabled=true`:

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend"
    dapr.io/app-port: "8000"
    dapr.io/enable-mtls: "true"
    dapr.io/log-level: "info"
```

### Environment Variable

The backend uses `DAPR_ENABLED` to conditionally publish events:

```python
DAPR_ENABLED = os.getenv("DAPR_ENABLED", "false").lower() == "true"

if not DAPR_ENABLED:
    logger.info("Dapr is disabled, skipping event publish")
    return True
```

## Using Dapr

### Publishing Events

From the backend application:

```python
from src.core.dapr import dapr_client

# Publish to a topic
await dapr_client.publish("task-events", {
    "type": "task.created",
    "data": {"task_id": 123}
})
```

### State Management

```python
# Save state
await dapr_client.save_state("user_preferences", user_id, {"theme": "dark"})

# Get state
preferences = await dapr_client.get_state("user_preferences", user_id)

# Delete state
await dapr_client.delete_state("user_preferences", user_id)
```

### Service Invocation

```python
# Invoke another service
response = await dapr_client.invoke_service(
    app_id="notification-service",
    method="send",
    data={"message": "Task completed!"}
)
```

## Dapr Dashboard

Access the Dapr dashboard for monitoring:

```bash
dapr dashboard -k
```

This opens a browser at http://localhost:8080 showing:
- Service mesh topology
- Component status
- Pub/sub connections
- Actor state

## Troubleshooting

### Check Dapr Sidecar Logs

```bash
kubectl logs <pod-name> -c daprd
```

### Verify Component Configuration

```bash
kubectl get components
kubectl describe component taskpubsub
```

### Check Subscription Status

```bash
kubectl get subscriptions
kubectl describe subscription task-events-subscription
```

### Test Pub/Sub Locally

```bash
# Port forward Dapr sidecar
kubectl port-forward deployment/todo-release-backend 3500:3500

# Publish test event
curl -X POST http://localhost:3500/v1.0/publish/taskpubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"type": "test.event", "data": {"test": true}}'
```

### Common Issues

1. **Sidecar not injecting**
   - Verify namespace has label: `kubectl label namespace default dapr-injection-enabled=true`
   - Check sidecar injector logs

2. **Pub/sub not connecting**
   - Verify Kafka broker is accessible
   - Check component metadata (broker URL, auth)
   - View Dapr sidecar logs for connection errors

3. **Events not routing**
   - Verify subscription route matches endpoint path
   - Check scopes in subscription match app-id
   - Ensure app port annotation is correct

## Uninstalling Dapr

```bash
# Remove Dapr from Kubernetes
dapr uninstall -k

# Remove Dapr namespace
kubectl delete namespace dapr-system
```
