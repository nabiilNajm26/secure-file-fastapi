.PHONY: help install dev up down logs clean migrate superuser test docker-shell docker-migrate rebuild

help:
	@echo "Available commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make dev          - Start development server"
	@echo "  make up           - Start all services with Docker"
	@echo "  make down         - Stop all Docker services"
	@echo "  make logs         - Show Docker logs"
	@echo "  make clean        - Clean up Docker volumes"
	@echo "  make migrate      - Initialize database tables"
	@echo "  make superuser    - Create a superuser"
	@echo "  make test         - Run tests"
	@echo "  make docker-shell - Open shell in API container"
	@echo "  make docker-migrate - Run migrations in Docker"
	@echo "  make rebuild      - Rebuild Docker containers"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --port 8001

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf uploads/*

migrate:
	python scripts/init_db.py

superuser:
	python scripts/create_superuser.py

test:
	pytest tests/ -v

docker-shell:
	docker-compose exec api /bin/bash

docker-migrate:
	docker-compose exec api alembic upgrade head

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d