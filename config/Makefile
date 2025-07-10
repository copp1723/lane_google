# Code Quality Configuration

## Makefile for common development tasks

.PHONY: help install format lint test clean security

# Default target
help:
	@echo "Available commands:"
	@echo "  install     Install all dependencies"
	@echo "  format      Format all code (Python and JavaScript)"
	@echo "  lint        Run all linters"
	@echo "  test        Run all tests"
	@echo "  security    Run security scans"
	@echo "  clean       Clean build artifacts and cache"
	@echo "  check       Run all quality checks"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd enterprise_backend/core_api && source venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd mcp_dashboard && pnpm install
	@echo "Installing pre-commit hooks..."
	cd enterprise_backend/core_api && source venv/bin/activate && pre-commit install

# Format code
format:
	@echo "Formatting Python code..."
	cd enterprise_backend/core_api && source venv/bin/activate && black src/ && isort src/
	@echo "Formatting JavaScript/React code..."
	cd mcp_dashboard && pnpm run format

# Run linters
lint:
	@echo "Linting Python code..."
	cd enterprise_backend/core_api && source venv/bin/activate && flake8 src/
	@echo "Linting JavaScript/React code..."
	cd mcp_dashboard && pnpm run lint

# Run tests
test:
	@echo "Running Python tests..."
	cd enterprise_backend/core_api && source venv/bin/activate && python -m pytest tests/ -v
	@echo "Running JavaScript tests..."
	cd mcp_dashboard && pnpm run test

# Security scans
security:
	@echo "Running Python security scan..."
	cd enterprise_backend/core_api && source venv/bin/activate && bandit -r src/ -f json -o bandit-report.json
	cd enterprise_backend/core_api && source venv/bin/activate && safety check
	@echo "Security scans completed"

# Clean artifacts
clean:
	@echo "Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleaning frontend build..."
	cd mcp_dashboard && rm -rf dist/ node_modules/.cache/
	@echo "Cleaning logs..."
	rm -f *.log bandit-report.json

# Run all quality checks
check: format lint security
	@echo "All quality checks completed"

# Development server
dev-backend:
	cd enterprise_backend/core_api && source venv/bin/activate && python src/main.py

dev-frontend:
	cd mcp_dashboard && pnpm run dev

# Production build
build:
	@echo "Building frontend..."
	cd mcp_dashboard && pnpm run build
	@echo "Build completed"

