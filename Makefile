# ===== Makefile for the FastAPI / PostgreSQL project =====
PY ?= python3
COMPOSE ?= docker compose
DEFAULT_MARKER ?= "not sql"

.DEFAULT_GOAL := help
GREEN := \033[0;32m
NC := \033[0m

help: ## List available targets
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;32m%-16s\033[0m %s\n", $$1, $$2}'

venv: ## (Optional) Create a .venv virtualenv
	$(PY) -m venv .venv

install: ## Install dependencies (venv activated)
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements.txt

run: ## Start the API with reload
	$(PY) -m uvicorn app.main:app --reload

test: ## All tests except SQL
	$(PY) -m pytest -q -m $(DEFAULT_MARKER)

test-all: ## Full test suite (unit + integration + SQL)
	$(PY) -m pytest -q

db-up: ## Start PostgreSQL (Docker)
	$(COMPOSE) up -d db

db-down: ## Stop PostgreSQL
	$(COMPOSE) down

migrate: ## Apply Alembic migrations
	$(PY) -m alembic upgrade head

test-sql: ## Start DB, run migrations, execute SQL tests
	make db-up
	make migrate
	make test-all
	make db-down

lint: ## Ruff + mypy (venv activated)
	$(PY) -m ruff check app tests
	$(PY) -m mypy app

format: ## Black + Ruff --fix
	$(PY) -m black app tests
	$(PY) -m ruff check --fix app tests

last_check:
	make format
	make lint
	make test-sql

clean: ## Remove Python / pytest / mypy caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache
