# Makefile for Lipton Webserver Development

.PHONY: help install test test-unit test-integration test-cov test-watch lint format clean

help:
	@echo "Lipton Webserver - Development Commands"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run all tests"
	@echo "  make test-unit         Run only unit tests (fast)"
	@echo "  make test-integration  Run only integration tests"
	@echo "  make test-cov          Run tests with coverage report"
	@echo "  make test-watch        Run tests in watch mode"
	@echo "  make test-e2e          Run Playwright E2E tests"
	@echo ""
	@echo "Quality:"
	@echo "  make lint              Run linters"
	@echo "  make format            Format code"
	@echo "  make typecheck         Run type checking"
	@echo ""
	@echo "Setup:"
	@echo "  make install           Install all dependencies"
	@echo "  make install-dev       Install dev dependencies"
	@echo ""
	@echo "Server:"
	@echo "  make api               Start FastAPI server"
	@echo "  make server            Start Node.js server"
	@echo ""
	@echo "Other:"
	@echo "  make clean             Clean temporary files"

# Installation
install:
	pip install -r requirements.txt
	npm install

install-dev: install
	pip install pytest pytest-cov pytest-asyncio pytest-mock httpx coverage[toml]
	pip install black flake8 mypy
	npm install --include=dev

# Testing - Python API
test:
	@echo "🧪 Running all tests..."
	./venv/bin/pytest -v

test-unit:
	@echo "🧪 Running unit tests..."
	./venv/bin/pytest -v -m unit

test-integration:
	@echo "🧪 Running integration tests..."
	./venv/bin/pytest -v -m integration

test-cov:
	@echo "📊 Running tests with coverage..."
	./venv/bin/pytest --cov=api --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "📈 Coverage report generated in htmlcov/index.html"

test-watch:
	@echo "👀 Running tests in watch mode..."
	@command -v ./venv/bin/ptw >/dev/null 2>&1 || { echo "Installing pytest-watch..."; ./venv/bin/pip install pytest-watch; }
	./venv/bin/ptw -- -v

test-critical:
	@echo "🔥 Running critical path tests..."
	./venv/bin/pytest -v -m critical

test-smoke:
	@echo "💨 Running smoke tests..."
	./venv/bin/pytest -v -m smoke

# Testing - E2E
test-e2e:
	@echo "🎭 Running Playwright E2E tests..."
	npm test

test-e2e-headed:
	@echo "🎭 Running Playwright E2E tests (headed)..."
	npm run test:headed

test-e2e-debug:
	@echo "🔍 Running Playwright E2E tests (debug mode)..."
	npm run test:debug

# Code Quality
lint:
	@echo "🔍 Running linters..."
	@echo "Python linting..."
	@command -v flake8 >/dev/null 2>&1 && flake8 api/ --max-line-length=100 --exclude=api/tests/__pycache__,api/__pycache__ || echo "⚠️  flake8 not installed (optional)"
	@echo "JavaScript linting..."
	npm run lint 2>/dev/null || echo "No npm lint script configured"

format:
	@echo "✨ Formatting code..."
	@command -v black >/dev/null 2>&1 && black api/ || echo "⚠️  black not installed (optional)"
	@echo "✅ Code formatted"

typecheck:
	@echo "📝 Running type checking..."
	@command -v mypy >/dev/null 2>&1 && mypy api/ --ignore-missing-imports || echo "⚠️  mypy not installed (optional)"

# Server commands
api:
	@echo "🚀 Starting FastAPI server..."
	cd api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

server:
	@echo "🚀 Starting Node.js server..."
	node server.js

dev:
	@echo "🚀 Starting development servers..."
	@echo "Note: Start API and Node.js server in separate terminals"
	@echo "Terminal 1: make api"
	@echo "Terminal 2: make server"

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "✅ Cleanup complete"

# Database
db-migrate:
	@echo "📦 Running database migrations..."
	psql -U postgres -d lipton_forms -f database/schema.sql

db-seed:
	@echo "🌱 Seeding database..."
	psql -U postgres -d lipton_forms -f database/official_baseline_taxonomy.sql

# CI/CD
ci: lint test-cov
	@echo "✅ CI checks passed"

pre-commit: format lint test
	@echo "✅ Pre-commit checks passed"

# Coverage
coverage-report:
	@echo "📊 Opening coverage report..."
	open htmlcov/index.html || xdg-open htmlcov/index.html

# Docker (if using monitoring stack)
monitoring-up:
	@echo "🐳 Starting monitoring stack..."
	cd monitoring && docker-compose up -d

monitoring-down:
	@echo "🐳 Stopping monitoring stack..."
	cd monitoring && docker-compose down

# Help is default
.DEFAULT_GOAL := help

