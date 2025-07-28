#!/bin/bash
# Setup script for OpenFootManager testing environment

echo "Setting up OpenFootManager testing environment..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
poetry run pre-commit install

# Run initial tests to verify setup
echo "Running fast tests to verify setup..."
poetry run pytest -m fast -v

# Generate initial coverage report
echo "Generating coverage report..."
poetry run pytest --cov=ofm --cov-report=html --cov-report=term-missing -m fast

echo ""
echo "✅ Testing environment setup complete!"
echo ""
echo "Quick commands:"
echo "  make test          - Run all tests"
echo "  make test-fast     - Run fast tests only"
echo "  make coverage      - Generate coverage report"
echo "  make lint          - Run linters"
echo "  make format        - Format code"
echo ""
echo "Pre-commit hooks are now active and will run automatically on git commit."
echo "To run them manually: pre-commit run --all-files"