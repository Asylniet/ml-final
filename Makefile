.PHONY: help install data data-mirbase train train-mature train-all dev build run stop down logs

help:
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies"
	@echo "  make data         - Download pre-miRNA data from NCBI"
	@echo "  make data-mirbase - Download mature miRNA data from miRBase"
	@echo "  make train        - Train pre-miRNA classifier, log to MLflow"
	@echo "  make train-mature - Train mature miRNA position predictor, log to MLflow"
	@echo "  make train-all    - Download all data and train both models"
	@echo "  make dev          - Start frontend dev server"
	@echo "  make build        - Build all apps via Turborepo"
	@echo "  make run          - Start all services with Docker Compose"
	@echo "  make stop         - Stop containers"
	@echo "  make down         - Remove containers"
	@echo "  make logs         - Stream container logs"

install:
	cd apps/api && uv sync
	pnpm install

data:
	cd apps/api && uv run python scripts/download_data.py

data-mirbase:
	cd apps/api && uv run python scripts/download_mirbase.py

train:
	cd apps/api && uv run python scripts/train.py

train-mature:
	cd apps/api && uv run python scripts/train_mature.py

train-all: data data-mirbase train train-mature

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
