# Sales Call Prep Assistant - Development Makefile

# Colors for output
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Sales Call Prep Assistant - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Frontend commands
.PHONY: frontend-install
frontend-install: ## Install frontend dependencies
	@echo "$(YELLOW)Installing frontend dependencies...$(NC)"
	cd frontend && pnpm install

.PHONY: frontend-dev
frontend-dev: ## Run frontend development server (http://localhost:3000)
	@echo "$(YELLOW)Starting frontend development server...$(NC)"
	cd frontend && pnpm dev

.PHONY: frontend-build
frontend-build: ## Build frontend for production
	@echo "$(YELLOW)Building frontend for production...$(NC)"
	cd frontend && pnpm build

.PHONY: frontend-start
frontend-start: ## Start production frontend server
	@echo "$(YELLOW)Starting production frontend server...$(NC)"
	cd frontend && pnpm start

.PHONY: frontend-test
frontend-test: ## Run frontend tests
	@echo "$(YELLOW)Running frontend tests...$(NC)"
	cd frontend && pnpm test

.PHONY: frontend-lint
frontend-lint: ## Run frontend linting
	@echo "$(YELLOW)Running frontend linting...$(NC)"
	cd frontend && pnpm lint

# Backend commands
.PHONY: backend-install
backend-install: ## Install backend dependencies
	@echo "$(YELLOW)Installing backend dependencies...$(NC)"
	cd backend && uv sync

.PHONY: backend-install-dev
backend-install-dev: ## Install backend dependencies with dev packages
	@echo "$(YELLOW)Installing backend dev dependencies...$(NC)"
	cd backend && uv sync --group dev

.PHONY: backend-dev
backend-dev: ## Run backend development server (http://localhost:8000)
	@echo "$(YELLOW)Starting backend development server...$(NC)"
	uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: backend-test
backend-test: ## Run backend tests
	@echo "$(YELLOW)Running backend tests...$(NC)"
	pytest

# Combined commands
.PHONY: install
install: frontend-install backend-install ## Install all dependencies
	@echo "$(GREEN)All dependencies installed!$(NC)"

.PHONY: install-dev
install-dev: frontend-install backend-install-dev ## Install all dependencies including dev packages
	@echo "$(GREEN)All dependencies installed!$(NC)"

.PHONY: dev
dev: ## Run both frontend and backend in development mode
	@echo "$(YELLOW)Starting both frontend and backend...$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000$(NC)"
	@echo "$(BLUE)Backend:  http://localhost:8000$(NC)"
	@echo "$(BLUE)API Docs: http://localhost:8000/docs$(NC)"
	@echo ""
	$(MAKE) frontend-dev & $(MAKE) backend-dev

.PHONY: build
build: frontend-build ## Build frontend for production
	@echo "$(GREEN)Frontend build complete!$(NC)"

.PHONY: test
test: frontend-test backend-test ## Run all tests
	@echo "$(GREEN)All tests passed!$(NC)"

.PHONY: lint
lint: frontend-lint ## Run all linting
	@echo "$(GREEN)Linting complete!$(NC)"

# Database commands
.PHONY: db-start
db-start: ## Start local Supabase
	@echo "$(YELLOW)Starting local Supabase...$(NC)"
	cd backend && supabase start

.PHONY: db-push
db-push: ## Apply database migrations
	@echo "$(YELLOW)Applying database migrations...$(NC)"
	cd backend && supabase db push

.PHONY: db-logs
db-logs: ## View Supabase logs
	cd backend && supabase logs

# Cleanup commands
.PHONY: clean
clean: ## Clean all build artifacts and caches
	@echo "$(YELLOW)Cleaning frontend build artifacts...$(NC)"
	cd frontend && rm -rf .next node_modules dist
	@echo "$(GREEN)Clean complete!$(NC)"

.PHONY: clean-all
clean-all: clean ## Clean all build artifacts, caches, and installed dependencies
	@echo "$(YELLOW)Cleaning all dependencies and caches...$(NC)"
	cd frontend && rm -rf .next node_modules pnpm-lock.yaml
	cd backend && rm -rf .venv
	@echo "$(GREEN)Deep clean complete!$(NC)"

# Development workflow
.PHONY: setup
setup: install-dev ## Initial project setup (installs all dependencies)
	@echo ""
	@echo "$(GREEN)Setup complete! Next steps:$(NC)"
	@echo "  1. Copy backend/.env.example to backend/.env and fill in your API keys"
	@echo "  2. Copy frontend/.env.example to frontend/.env.local and fill in your Supabase credentials"
	@echo "  3. Run 'make db-push' to set up the database"
	@echo "  4. Run 'make dev' to start both servers"

.PHONY: reset
reset: clean-all install-dev ## Reset project (clean + fresh install)
	@echo "$(GREEN)Project reset complete!$(NC)"

# Quick commands
.PHONY: serve
serve: frontend-build backend-dev ## Build frontend then start backend
	@echo "$(GREEN)Serving production frontend with dev backend!$(NC)"

# Status commands
.PHONY: status
status: ## Show project status
	@echo "$(BLUE)Project Status:$(NC)"
	@echo "Frontend: $(shell [ -d frontend/node_modules ] && echo '$(GREEN)Installed$(NC)' || echo '$(RED)Not installed$(NC)')"
	@echo "Backend:  $(shell [ -d backend/.venv ] && echo '$(GREEN)Installed$(NC)' || echo '$(RED)Not installed$(NC)')"
