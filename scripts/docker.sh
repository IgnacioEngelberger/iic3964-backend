#!/bin/bash

# Docker management script for IIC3964 Backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to build the Docker image
build() {
    print_status "Building Docker image..."
    docker build -t iic3964-backend:latest .
    print_status "Docker image built successfully!"
}

# Function to run development environment
dev() {
    print_status "Starting development environment..."
    docker-compose up --build
}

# Function to run development environment in background
dev_detached() {
    print_status "Starting development environment in background..."
    docker-compose up --build -d
    print_status "Development environment started!"
    print_status "API available at: http://localhost:8000"
    print_status "Database available at: localhost:5432"
    print_status "Redis available at: localhost:6379"
}

# Function to stop development environment
stop() {
    print_status "Stopping development environment..."
    docker-compose down
    print_status "Development environment stopped!"
}

# Function to run production environment
prod() {
    print_status "Starting production environment..."
    if [ ! -f .env ]; then
        print_error ".env file not found. Please create one based on .env.example"
        exit 1
    fi
    docker-compose -f docker-compose.prod.yml up --build
}

# Function to run tests in Docker
test() {
    print_status "Running tests in Docker..."
    docker-compose run --rm app poetry run pytest tests/ -v
}

# Function to run linting in Docker
lint() {
    print_status "Running linting in Docker..."
    docker-compose run --rm app poetry run flake8 app tests
    docker-compose run --rm app poetry run black --check app tests
    docker-compose run --rm app poetry run isort --check-only app tests
    docker-compose run --rm app poetry run mypy app
    print_status "Linting completed successfully!"
}

# Function to clean up Docker resources
clean() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_status "Docker resources cleaned up!"
}

# Function to show logs
logs() {
    docker-compose logs -f
}

# Function to show help
show_help() {
    echo "IIC3964 Backend Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker image"
    echo "  dev         Run development environment"
    echo "  dev-bg      Run development environment in background"
    echo "  stop        Stop development environment"
    echo "  prod        Run production environment"
    echo "  test        Run tests in Docker"
    echo "  lint        Run linting in Docker"
    echo "  logs        Show logs"
    echo "  clean       Clean up Docker resources"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 dev"
    echo "  $0 dev-bg"
    echo "  $0 stop"
}

# Main script logic
case "${1:-help}" in
    build)
        build
        ;;
    dev)
        dev
        ;;
    dev-bg)
        dev_detached
        ;;
    stop)
        stop
        ;;
    prod)
        prod
        ;;
    test)
        test
        ;;
    lint)
        lint
        ;;
    logs)
        logs
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
