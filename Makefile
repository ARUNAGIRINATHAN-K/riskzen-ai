.PHONY: dev stop build logs backend-logs frontend-logs db-logs ollama-logs \
       migrate seed test lint clean pull-model health

# ──────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────

## Start all services in development mode
dev:
	docker compose up -d
	@echo ""
	@echo "🚀 RiskZen is starting..."
	@echo "   Frontend:  http://localhost:3000"
	@echo "   Backend:   http://localhost:8000"
	@echo "   API Docs:  http://localhost:8000/docs"
	@echo "   Database:  localhost:5432"
	@echo "   Ollama:    localhost:11434"
	@echo ""

## Stop all services
stop:
	docker compose down

## Rebuild all images
build:
	docker compose build --no-cache

## View logs for all services
logs:
	docker compose logs -f

## View logs for specific services
backend-logs:
	docker compose logs -f backend

frontend-logs:
	docker compose logs -f frontend

db-logs:
	docker compose logs -f db

ollama-logs:
	docker compose logs -f ollama

# ──────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────

## Run database migrations
migrate:
	docker compose exec backend alembic upgrade head

## Generate a new migration
migration:
	@read -p "Migration message: " msg; \
	docker compose exec backend alembic revision --autogenerate -m "$$msg"

## Seed database with test data
seed:
	docker compose exec backend python -m app.seed

## Open psql shell
db-shell:
	docker compose exec db psql -U riskzen -d riskzen

# ──────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────

## Run backend tests
test:
	docker compose exec backend pytest -v

## Run backend tests with coverage
test-cov:
	docker compose exec backend pytest --cov=app --cov-report=html -v

# ──────────────────────────────────────────────
# Linting
# ──────────────────────────────────────────────

## Run backend linter
lint:
	docker compose exec backend ruff check app/
	docker compose exec backend ruff format --check app/

## Auto-fix backend lint issues
lint-fix:
	docker compose exec backend ruff check --fix app/
	docker compose exec backend ruff format app/

# ──────────────────────────────────────────────
# LLM
# ──────────────────────────────────────────────

## Pull the default Ollama model
pull-model:
	docker compose exec ollama ollama pull llama3.1

# ──────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────

## Check system health
health:
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool

## Remove all containers, volumes, and build cache
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

## Copy environment template
env:
	cp .env.example .env
	@echo "✅ Created .env from .env.example — edit it with your values"

## Show available commands
help:
	@echo "RiskZen Development Commands"
	@echo "───────────────────────────"
	@echo ""
	@echo "  make dev          Start all services"
	@echo "  make stop         Stop all services"
	@echo "  make build        Rebuild all images"
	@echo "  make logs         View all logs"
	@echo "  make migrate      Run database migrations"
	@echo "  make migration    Generate new migration"
	@echo "  make seed         Seed database with test data"
	@echo "  make db-shell     Open PostgreSQL shell"
	@echo "  make test         Run backend tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make lint         Run linter"
	@echo "  make lint-fix     Auto-fix lint issues"
	@echo "  make pull-model   Pull Ollama LLM model"
	@echo "  make health       Check system health"
	@echo "  make clean        Remove everything (volumes included)"
	@echo "  make env          Create .env from template"
	@echo ""
