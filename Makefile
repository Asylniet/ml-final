.PHONY: help install data train dev build run stop down logs

help:
	@echo "Available commands:"
	@echo "  make install  - Install all dependencies"
	@echo "  make train    - Train models and log to MLflow"
	@echo "  make dev      - Start frontend dev server"
	@echo "  make build    - Build all apps via Turborepo"
	@echo "  make run      - Start all services with Docker Compose"
	@echo "  make stop     - Stop containers"
	@echo "  make down     - Remove containers"
	@echo "  make logs     - Stream container logs"

install:
	cd apps/api && uv sync
	pnpm install

train:
	cd apps/api && uv run python scripts/train.py

dev:
	pnpm dev

build:
	pnpm build

run:
	DOCKER_BUILDKIT=1 docker compose up -d --build

stop:
	docker compose stop

down:
	docker compose down

logs:
	docker compose logs -f
