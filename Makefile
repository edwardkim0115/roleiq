DC = docker compose

.PHONY: up down build api-test api-lint web-lint migrate

up:
	$(DC) up --build

down:
	$(DC) down

build:
	$(DC) build

api-test:
	$(DC) run --rm api pytest

api-lint:
	$(DC) run --rm api ruff check .

web-lint:
	$(DC) run --rm web npm run lint

migrate:
	$(DC) run --rm api alembic upgrade head
 
