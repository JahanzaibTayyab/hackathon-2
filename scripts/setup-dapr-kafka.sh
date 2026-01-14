#!/bin/bash
# Phase V: Dapr + Kafka Setup Script for Local Development
# This script sets up Dapr, Strimzi Kafka, and the Todo application on Minikube
#
# Prerequisites:
# - Minikube installed
# - Docker installed
# - kubectl installed
# - Helm installed
# - Dapr CLI installed (brew install dapr/tap/dapr-cli)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MINIKUBE_CPUS=4
MINIKUBE_MEMORY=7168
KAFKA_NAMESPACE="kafka"
APP_NAMESPACE="default"
STRIMZI_VERSION="0.46.0"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    if ! command -v minikube &> /dev/null; then
        missing+=("minikube")
    fi

    if ! command -v kubectl &> /dev/null; then
        missing+=("kubectl")
    fi

    if ! command -v helm &> /dev/null; then
        missing+=("helm")
    fi

    if ! command -v dapr &> /dev/null; then
        missing+=("dapr CLI (brew install dapr/tap/dapr-cli)")
    fi

    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing prerequisites: ${missing[*]}"
        exit 1
    fi

    log_success "All prerequisites are installed"
}

start_minikube() {
    log_info "Starting Minikube with $MINIKUBE_CPUS CPUs and ${MINIKUBE_MEMORY}MB RAM..."

    # Check if Minikube is already running
    if minikube status | grep -q "Running"; then
        log_warning "Minikube is already running. Checking resources..."

        # Check current resources
        local current_cpus=$(minikube config get cpus 2>/dev/null || echo "2")
        local current_memory=$(minikube config get memory 2>/dev/null || echo "2048")

        if [ "$current_cpus" -lt "$MINIKUBE_CPUS" ] || [ "$current_memory" -lt "$MINIKUBE_MEMORY" ]; then
            log_warning "Current Minikube resources are insufficient. Restarting with more resources..."
            minikube stop
            minikube delete
            minikube start --cpus=$MINIKUBE_CPUS --memory=$MINIKUBE_MEMORY --driver=docker
        else
            log_success "Minikube has sufficient resources"
        fi
    else
        minikube start --cpus=$MINIKUBE_CPUS --memory=$MINIKUBE_MEMORY --driver=docker
    fi

    # Enable required addons
    log_info "Enabling Minikube addons..."
    minikube addons enable metrics-server

    log_success "Minikube is ready"
}

install_dapr() {
    log_info "Installing Dapr on Kubernetes..."

    # Check if Dapr is already installed
    if kubectl get namespace dapr-system &> /dev/null; then
        log_warning "Dapr namespace exists. Checking status..."
        if dapr status -k 2>/dev/null | grep -q "Running"; then
            log_success "Dapr is already installed and running"
            return
        fi
    fi

    # Initialize Dapr on Kubernetes
    dapr init -k --wait

    # Verify installation
    log_info "Verifying Dapr installation..."
    dapr status -k

    log_success "Dapr is installed and running"
}

install_strimzi() {
    log_info "Installing Strimzi Kafka Operator..."

    # Create Kafka namespace
    kubectl create namespace $KAFKA_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Check if Strimzi is already installed
    if kubectl get deployment strimzi-cluster-operator -n $KAFKA_NAMESPACE &> /dev/null; then
        log_warning "Strimzi operator is already installed"
    else
        # Install Strimzi operator
        kubectl create -f "https://strimzi.io/install/latest?namespace=$KAFKA_NAMESPACE" -n $KAFKA_NAMESPACE

        # Wait for Strimzi operator to be ready
        log_info "Waiting for Strimzi operator to be ready..."
        kubectl wait deployment/strimzi-cluster-operator \
            --for=condition=available \
            --timeout=300s \
            -n $KAFKA_NAMESPACE
    fi

    log_success "Strimzi Kafka Operator is ready"
}

deploy_kafka_cluster() {
    log_info "Deploying Kafka cluster..."

    # Apply Kafka cluster configuration
    kubectl apply -f helm-chart/kafka/kafka-cluster.yaml

    # Wait for Kafka cluster to be ready
    log_info "Waiting for Kafka cluster to be ready (this may take a few minutes)..."
    kubectl wait kafka/todo-kafka \
        --for=condition=Ready \
        --timeout=600s \
        -n $KAFKA_NAMESPACE

    log_success "Kafka cluster is ready"
}

create_kafka_topics() {
    log_info "Creating Kafka topics..."

    # Apply topics configuration
    kubectl apply -f helm-chart/kafka/topics.yaml

    # Wait for topics to be created
    sleep 10

    # Verify topics
    log_info "Verifying Kafka topics..."
    kubectl get kafkatopics -n $KAFKA_NAMESPACE

    log_success "Kafka topics are created"
}

deploy_dapr_components() {
    log_info "Deploying Dapr components..."

    # Apply Dapr configuration (disable mTLS for local dev)
    kubectl apply -f helm-chart/dapr-components/appconfig.yaml

    # Apply Dapr pub/sub component
    kubectl apply -f helm-chart/dapr-components/pubsub.yaml

    # Apply Dapr subscriptions
    kubectl apply -f helm-chart/dapr-components/subscription.yaml

    log_success "Dapr components are deployed"
}

build_and_load_images() {
    log_info "Building and loading Docker images into Minikube..."

    # Configure Docker to use Minikube's Docker daemon
    eval $(minikube docker-env)

    # Build frontend image
    log_info "Building frontend image..."
    docker build -t todo-frontend:latest ./frontend

    # Build backend image
    log_info "Building backend image..."
    docker build -t todo-backend:latest ./backend

    log_success "Docker images are built and loaded"
}

deploy_application() {
    log_info "Deploying Todo application with Dapr..."

    # Check if secrets exist
    if ! kubectl get secret todo-secrets &> /dev/null; then
        log_error "todo-secrets not found. Please create secrets first:"
        echo "kubectl create secret generic todo-secrets \\"
        echo "  --from-literal=database-url='your-neon-database-url' \\"
        echo "  --from-literal=auth-secret='your-better-auth-secret' \\"
        echo "  --from-literal=openai-api-key='your-openai-api-key'"
        exit 1
    fi

    # Deploy with Helm
    helm upgrade --install todo-release ./helm-chart/todo-app \
        --set dapr.enabled=true \
        --set kafka.enabled=true \
        --wait \
        --timeout 300s

    log_success "Todo application is deployed"
}

verify_deployment() {
    log_info "Verifying deployment..."

    echo ""
    echo "=== Pods ==="
    kubectl get pods -o wide

    echo ""
    echo "=== Services ==="
    kubectl get services

    echo ""
    echo "=== Dapr Status ==="
    dapr status -k

    echo ""
    echo "=== Kafka Topics ==="
    kubectl get kafkatopics -n $KAFKA_NAMESPACE

    log_success "Deployment verification complete"
}

show_access_info() {
    echo ""
    echo "=========================================="
    echo "           Deployment Complete!           "
    echo "=========================================="
    echo ""
    log_info "Access the application:"
    echo "  Frontend: http://$(minikube ip):30080"
    echo "  Backend API: http://$(minikube ip):30080/api/v1"
    echo ""
    log_warning "On macOS with Docker driver, run 'minikube tunnel' in a separate terminal"
    echo "  Then access: http://localhost:30080"
    echo ""
    log_info "Useful commands:"
    echo "  View pods:        kubectl get pods"
    echo "  View logs:        kubectl logs -f deployment/todo-release-backend"
    echo "  Dapr dashboard:   dapr dashboard -k"
    echo "  Kafka topics:     kubectl get kafkatopics -n kafka"
    echo ""
    log_info "To test Kafka events:"
    echo "  kubectl exec -it todo-kafka-dual-role-0 -n kafka -- \\"
    echo "    bin/kafka-console-consumer.sh \\"
    echo "    --bootstrap-server localhost:9092 \\"
    echo "    --topic task-events \\"
    echo "    --from-beginning"
    echo ""
}

# Main script
main() {
    echo "========================================"
    echo " Phase V: Dapr + Kafka Setup Script"
    echo "========================================"
    echo ""

    check_prerequisites
    start_minikube
    install_dapr
    install_strimzi
    deploy_kafka_cluster
    create_kafka_topics
    deploy_dapr_components

    # Optional: Build and deploy application
    if [ "$1" == "--deploy-app" ]; then
        build_and_load_images
        deploy_application
    fi

    verify_deployment
    show_access_info
}

# Help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --deploy-app    Also build and deploy the Todo application"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Setup Dapr + Kafka only"
    echo "  $0 --deploy-app     # Setup everything including the app"
}

# Parse arguments
case "$1" in
    --help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
