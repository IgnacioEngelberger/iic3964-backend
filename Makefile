# IIC3964 Backend Makefile

.PHONY: help install dev test lint format pre-commit clean docker-build docker-dev docker-stop docker-test docker-lint

# Default target
help: ## Show this help message
	@echo "IIC3964 Backend - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
install: ## Install dependencies
	poetry install

dev: ## Run development server
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	poetry run pytest tests/ -v

lint: ## Run linting
	poetry run flake8 app tests
	poetry run black --check app tests
	poetry run isort --check-only app tests
	poetry run mypy app

format: ## Format code
	poetry run black app tests
	poetry run isort app tests

pre-commit: ## Run pre-commit hooks
	poetry run pre-commit run --all-files

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Docker commands
docker-build: ## Build Docker image
	docker build -t iic3964-backend:latest .

docker-dev: ## Run development environment with Docker
	docker-compose up --build

docker-dev-bg: ## Run development environment in background
	docker-compose up --build -d

docker-stop: ## Stop Docker containers
	docker-compose down

docker-test: ## Run tests in Docker
	docker-compose run --rm app poetry run pytest tests/ -v

docker-lint: ## Run linting in Docker
	docker-compose run --rm app poetry run flake8 app tests
	docker-compose run --rm app poetry run black --check app tests
	docker-compose run --rm app poetry run isort --check-only app tests
	docker-compose run --rm app poetry run mypy app

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-clean: ## Clean up Docker resources
	docker-compose down -v --remove-orphans
	docker system prune -f

# Production commands
prod: ## Run production environment
	docker-compose -f docker-compose.prod.yml up --build

# Setup commands
setup: install ## Initial setup
	@echo "Setting up pre-commit hooks..."
	poetry run pre-commit install
	@echo "Setup completed!"

# All-in-one commands
all-checks: lint test ## Run all checks (lint + test)
	@echo "All checks completed successfully!"

docker-all: docker-build docker-test docker-lint ## Build, test and lint with Docker
	@echo "Docker build, test and lint completed successfully!"
