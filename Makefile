# CommitQuest Makefile
# Common development commands

.PHONY: help install dev test lint format migrate shell docker-up docker-down

# Default target
help:
	@echo "CommitQuest Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install all dependencies"
	@echo "  make dev          Start development environment"
	@echo ""
	@echo "Backend:"
	@echo "  make migrate      Run database migrations"
	@echo "  make shell        Open Django shell"
	@echo "  make test-backend Run backend tests"
	@echo "  make lint-backend Lint backend code"
	@echo ""
	@echo "Frontend:"
	@echo "  make test-frontend Run frontend tests"
	@echo "  make lint-frontend Lint frontend code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    Start all services with Docker"
	@echo "  make docker-down  Stop all services"
	@echo "  make docker-logs  View logs from all services"
	@echo ""
	@echo "Quality:"
	@echo "  make test         Run all tests"
	@echo "  make lint         Run all linters"
	@echo "  make format       Format all code"
	@echo "  make security     Run security scans"

# Installation
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm ci

# Development
dev:
	docker-compose up -d db redis
	@echo "Starting backend..."
	cd backend && python manage.py runserver &
	@echo "Starting frontend..."
	cd frontend && npm start

# Backend commands
migrate:
	cd backend && python manage.py migrate

shell:
	cd backend && python manage.py shell

test-backend:
	cd backend && pytest -v

lint-backend:
	cd backend && ruff check .
	cd backend && black --check .
	cd backend && isort --check-only .

format-backend:
	cd backend && black .
	cd backend && isort .
	cd backend && ruff check --fix .

# Frontend commands
test-frontend:
	cd frontend && npm test -- --watchAll=false

lint-frontend:
	cd frontend && npm run lint
	cd frontend && npm run type-check

format-frontend:
	cd frontend && npm run format

# Combined commands
test: test-backend test-frontend

lint: lint-backend lint-frontend

format: format-backend format-frontend

# Security
security:
	cd backend && pip-audit
	cd backend && bandit -r . -x ./tests
	cd frontend && npm audit

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

# Database
db-reset:
	cd backend && python manage.py flush --no-input
	cd backend && python manage.py migrate

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache
	rm -rf frontend/build
	rm -rf frontend/coverage
