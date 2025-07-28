# Makefile for OpenFootManager Development

.PHONY: help install test test-fast test-slow test-unit test-integration test-critical \
        coverage lint format type-check security clean pre-commit setup-dev run docs

# Default target
help:
	@echo "OpenFootManager Development Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install project dependencies"
	@echo "  make setup-dev     - Complete development environment setup"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-fast     - Run fast tests only (pre-commit)"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-critical - Run critical tests only"
	@echo "  make coverage      - Generate coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run all linters"
	@echo "  make format        - Format code with black & isort"
	@echo "  make type-check    - Run mypy type checking"
	@echo "  make security      - Run security checks"
	@echo "  make pre-commit    - Run pre-commit hooks"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run the application"
	@echo "  make docs          - Build documentation"
	@echo "  make clean         - Clean generated files"

# Installation
install:
	poetry install

setup-dev: install
	pre-commit install
	@echo "Development environment setup complete!"
	@echo "Pre-commit hooks installed - they will run automatically on git commit"

# Testing targets
test:
	pytest -v

test-fast:
	pytest -m fast -v --tb=short

test-slow:
	pytest -m slow -v

test-unit:
	pytest -m unit -v

test-integration:
	pytest -m integration -v

test-critical:
	pytest -m critical -v --tb=short

coverage:
	pytest --cov=ofm --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# Specific test categories
test-db:
	pytest -m db -v

test-simulation:
	pytest -m simulation -v

test-save:
	pytest -m save -v

test-performance:
	pytest -m performance -v

# Code quality
lint:
	@echo "Running flake8..."
	flake8 ofm/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running bandit security linter..."
	bandit -r ofm/ -ll -i

format:
	@echo "Formatting with black..."
	black ofm/ --line-length=100
	@echo "Sorting imports with isort..."
	isort ofm/ --profile black --line-length=100

type-check:
	@echo "Running mypy type checker..."
	mypy ofm/ --ignore-missing-imports --check-untyped-defs

security:
	@echo "Running security checks..."
	bandit -r ofm/ -f json -o bandit-report.json
	safety check
	@echo "Security report saved to bandit-report.json"

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Development
run:
	python run.py

docs:
	cd docs && make html
	@echo "Documentation built in docs/build/html/"

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -f coverage.xml
	rm -f bandit-report.json

# CI/CD helpers
ci-test:
	pytest -v --cov=ofm --cov-report=xml --cov-report=term-missing

ci-lint:
	black --check --diff ofm/
	isort --check-only --diff ofm/
	flake8 ofm/ --max-line-length=100 --extend-ignore=E203,W503