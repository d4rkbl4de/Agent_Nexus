SHELL := powershell.exe
.DEFAULT_GOAL := help

.PHONY: setup build up down restart logs ps clean migrate test-backend test-frontend

setup:
	if (!(Test-Path .env)) { Copy-Item .env.example .env }
	cd Agent_Nexus_Backend ; python -m venv .venv ; .\.venv\Scripts\activate ; pip install --upgrade pip ; pip install -r requirements.txt
	cd agent_nexus_frontend ; npm install

build:
	docker-compose build --parallel --no-cache

up:
	docker-compose up -d

down:
	docker-compose down --remove-orphans

restart:
	docker-compose restart

ps:
	docker-compose ps

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend alembic upgrade head

test-backend:
	docker-compose exec backend pytest -v --cov=common --cov-report=term-missing

test-frontend:
	cd agent_nexus_frontend ; npm run test

clean:
	docker-compose down -v
	Get-ChildItem -Path . -Include __pycache__, .pytest_cache, .next, dist, build, .venv, node_modules -Recurse | Remove-Item -Force -Recurse
	if (Test-Path Agent_Nexus_Backend/.venv) { Remove-Item -Path Agent_Nexus_Backend/.venv -Force -Recurse }

help:
	@echo "Agent Nexus Hive Mind Orchestration"
	@echo "-----------------------------------"
	@echo "setup          : Initialize environment, venv, and dependencies"
	@echo "build          : Build all Docker containers"
	@echo "up             : Spin up the Hive Mind (detached)"
	@echo "down           : Stop and remove containers"
	@echo "migrate        : Run database migrations"
	@echo "test-backend   : Execute backend test suite with coverage"
	@echo "clean          : Deep clean all temporary files and volumes"