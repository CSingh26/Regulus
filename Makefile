.PHONY: help up down dev format lint test seed-demo

help:
	@echo "Regulus dev commands"
	@echo "  make up        - start postgres + redis"
	@echo "  make down      - stop postgres + redis"
	@echo "  make dev       - run api + worker + web"
	@echo "  make format    - run formatters"
	@echo "  make lint      - run linters"
	@echo "  make test      - run tests"
	@echo "  make seed-demo - register and index current repo"

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

dev:
	./scripts/dev.sh

format:
	./scripts/format.sh

lint:
	./scripts/lint.sh

test:
	./scripts/test.sh

seed-demo:
	./scripts/demo.sh
