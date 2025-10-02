# Makefile for LLM Knowledge Extractor
SHELL := /bin/bash

.PHONY: help
help:
	@echo "LLM Knowledge Extractor - Available Commands:"
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup          : Install dependencies via uv"
	@echo "  make run            : Start development server"
	@echo "  make test           : Run all tests (unit + integration)"
	@echo "  make test-unit      : Run only unit tests"
	@echo "  make test-api       : Run only API integration tests"
	@echo "  make eval           : Run LLM quality evaluations"
	@echo "  make clean          : Clean unnecessary files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build   : Build Docker image"
	@echo "  make docker-run     : Run container with docker-compose"
	@echo "  make docker-stop    : Stop running container"
	@echo "  make docker-logs    : View container logs"
	@echo "  make docker-shell   : Open shell in running container"
	@echo ""
	@echo "Quality Checks:"
	@echo "  make lint           : Run linting checks"
	@echo "  make format         : Format code with black"

# Setup & Development
.PHONY: setup
setup:
	@echo "Installing dependencies..."
	uv sync
	@echo "Downloading spaCy model..."
	uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
	@echo "Setup complete! Copy .env.example to .env and add your OPENAI_API_KEY"

.PHONY: run
run:
	@echo "Starting development server at http://localhost:8000"
	@echo "API docs available at http://localhost:8000/docs"
	uv run uvicorn app.main:app --reload

# Testing & Evaluation
.PHONY: test
test:
	@echo "Running all tests..."
	uv run pytest tests/ -v

.PHONY: test-unit
test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/test_services.py -v

.PHONY: test-api
test-api:
	@echo "Running API integration tests..."
	@echo "Make sure server is running at http://localhost:8000"
	uv run python tests/test_api.py

.PHONY: eval
eval:
	@echo "Running LLM quality evaluations..."
	@echo "Make sure server is running at http://localhost:8000"
	@echo "This will make multiple API calls and may take a few minutes."
	uv run python evals/eval_llm_quality.py

# Cleaning
.PHONY: clean
clean:
	find . -type f -iname ".DS_Store" -delete
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ipynb_checkpoints" -delete
	rm -f .coverage

# Docker
.PHONY: docker-build
docker-build:
	@echo "Building Docker image..."
	docker build -t llm-knowledge-extractor:latest .

.PHONY: docker-run
docker-run:
	@echo "Starting containers with docker-compose..."
	@echo "API will be available at http://localhost:8000"
	docker-compose up -d

.PHONY: docker-stop
docker-stop:
	@echo "Stopping containers..."
	docker-compose down

.PHONY: docker-logs
docker-logs:
	@echo "Streaming container logs (Ctrl+C to exit)..."
	docker-compose logs -f api

.PHONY: docker-shell
docker-shell:
	@echo "Opening shell in running container..."
	docker-compose exec api /bin/bash

# Quality Checks
.PHONY: lint
lint:
	@echo "Running linting checks..."
	@echo "Note: Install ruff with 'uv add --dev ruff' for full linting"
	uv run python -m py_compile app/*.py app/services/*.py

.PHONY: format
format:
	@echo "Formatting code..."
	@echo "Note: Install black with 'uv add --dev black' for formatting"
	@echo "Skipping for now (not a dependency)"