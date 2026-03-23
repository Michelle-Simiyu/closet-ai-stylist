.PHONY: help dev-backend dev-frontend install test docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend: ## Start backend dev server
	cd backend && uvicorn src.main:app --reload --port 8000

dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

dev: ## Start both (requires tmux or run in separate terminals)
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals"

test: ## Run all backend tests
	cd backend && pytest -v --tb=short

test-coverage: ## Run tests with coverage
	cd backend && pytest --cov=src --cov-report=term-missing --cov-report=html

lint: ## Lint backend
	cd backend && python -m flake8 src/ --max-line-length=100 --ignore=E501

docker-up: ## Start with Docker Compose
	docker-compose up --build

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

clean: ## Remove build artifacts and cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/.pytest_cache backend/htmlcov backend/*.db
	rm -rf frontend/.svelte-kit frontend/build frontend/node_modules

demo: ## Load demo data (backend must be running)
	@echo "Visit http://localhost:5173/onboarding to load the demo wardrobe"
