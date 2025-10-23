# ===== Makefile pour le projet FastAPI / PostgreSQL =====
PY ?= python3
DEFAULT_MARKER ?= "not sql"

.DEFAULT_GOAL := help
GREEN := \033[0;32m
NC := \033[0m

help: ## Liste les commandes disponibles
	@echo "$(GREEN)Cibles disponibles:$(NC)"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;32m%-16s\033[0m %s\n", $$1, $$2}'

venv: ## (Optionnel) Crée un venv .venv
	$(PY) -m venv .venv

install: ## Installe les dépendances (venv activé)
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements.txt

run: ## Lance l'API en mode reload
	$(PY) -m uvicorn app.main:app --reload

test: ## Tous les tests sauf SQL
	$(PY) -m pytest -q -m $(DEFAULT_MARKER)

test-all: ## Tous les tests (unit + integration + SQL)
	$(PY) -m pytest -q

db-up: ## Démarre PostgreSQL (Docker)
	docker compose up -d db

db-down: ## Stoppe PostgreSQL
	docker compose down

migrate: ## Applique les migrations Alembic
	$(PY) -m alembic upgrade head

test-sql: ## Démarre la DB, applique les migrations et exécute tous les tests SQL
	make db-up
	make migrate
	make test-all
	make db-down

lint: ## Ruff + mypy (venv activé)
	$(PY) -m ruff check app tests
	$(PY) -m mypy app

format: ## Black + Ruff --fix
	$(PY) -m black app tests
	$(PY) -m ruff check --fix app tests

last_check:
	make format
	make lint
	make test-sql

clean: ## Supprime les caches Python / pytest / mypy
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache
