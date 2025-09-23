#!/bin/bash

# Development script for IIC3964 Backend

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

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    print_error "Poetry is not installed. Please install Poetry first."
    print_status "Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Function to install dependencies
install_deps() {
    print_status "Installing dependencies..."
    poetry install
    print_status "Dependencies installed successfully!"
}

# Function to run the development server
run_dev() {
    print_status "Starting development server..."
    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    poetry run pytest tests/ -v
}

# Function to run linting
run_lint() {
    print_status "Running linting..."
    poetry run flake8 app tests
    poetry run black --check app tests
    poetry run isort --check-only app tests
    poetry run mypy app
    print_status "Linting completed successfully!"
}

# Function to format code
format_code() {
    print_status "Formatting code..."
    poetry run black app tests
    poetry run isort app tests
    print_status "Code formatted successfully!"
}

# Function to run pre-commit hooks
run_pre_commit() {
    print_status "Running pre-commit hooks..."
    poetry run pre-commit run --all-files
}

# Function to show help
show_help() {
    echo "IIC3964 Backend Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install dependencies"
    echo "  dev         Run development server"
    echo "  test        Run tests"
    echo "  lint        Run linting"
    echo "  format      Format code"
    echo "  pre-commit  Run pre-commit hooks"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 dev"
    echo "  $0 test"
}

# Main script logic
case "${1:-help}" in
    install)
        install_deps
        ;;
    dev)
        run_dev
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    format)
        format_code
        ;;
    pre-commit)
        run_pre_commit
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
