.PHONY: help install shell run migrate makemigrations createsuperuser test lint format clean docker-build docker-up docker-down docker-logs docker-shell docker-migrate docker-reset minio-standalone

help:
	@echo "Available commands:"
	@echo "  Docker commands:"
	@echo "    docker-build     - Build Docker containers"
	@echo "    docker-up        - Start all services with Docker Compose"
	@echo "    docker-down      - Stop all Docker services"
	@echo "    docker-logs      - View Docker logs"
	@echo "    docker-shell     - Open shell in Django container"
	@echo "    docker-migrate   - Run migrations in Docker"
	@echo "    docker-reset     - Reset and rebuild Docker environment"
	@echo "    minio-standalone - Run standalone MinIO (requires ROOTNAME and ROOTPASS)"
	@echo ""
	@echo "  Legacy commands (without Docker):"
	@echo "    install          - Install dependencies"
	@echo "    shell            - Activate pipenv shell"
	@echo "    run              - Start development server"
	@echo "    migrate          - Apply database migrations"
	@echo "    makemigrations   - Create new migrations"
	@echo "    createsuperuser  - Create Django superuser"
	@echo "    test             - Run tests"
	@echo "    lint             - Check code formatting with black"
	@echo "    format           - Format code with black"
	@echo "    clean            - Remove cache files"

# Docker commands
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-shell:
	docker compose exec web bash

docker-migrate:
	docker compose exec web python manage.py migrate

docker-makemigrations:
	docker compose exec web python manage.py makemigrations

docker-createsuperuser:
	docker compose exec web python manage.py createsuperuser

docker-test:
	docker compose exec web python manage.py test

docker-reset:
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

# Legacy commands (without Docker)
install:
	pipenv install --dev

shell:
	pipenv shell

run:
	pipenv run python manage.py runserver

migrate:
	pipenv run python manage.py migrate

makemigrations:
	pipenv run python manage.py makemigrations

createsuperuser:
	pipenv run python manage.py createsuperuser

test:
	pipenv run python manage.py test

lint:
	pipenv run black --check .

format:
	pipenv run black .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Standalone MinIO command
minio-standalone:
	@if [ -z "$(ROOTNAME)" ] || [ -z "$(ROOTPASS)" ]; then \
		echo "Usage: make minio-standalone ROOTNAME=your_username ROOTPASS=your_password"; \
		echo "Example: make minio-standalone ROOTNAME=admin ROOTPASS=changeme123"; \
		exit 1; \
	fi
	@echo "Starting MinIO with credentials: $(ROOTNAME)/$(ROOTPASS)"
	@mkdir -p ~/minio/data
	docker run \
		-p 9000:9000 \
		-p 9001:9001 \
		--name minio \
		-v ~/minio/data:/data \
		-e "MINIO_ROOT_USER=$(ROOTNAME)" \
		-e "MINIO_ROOT_PASSWORD=$(ROOTPASS)" \
		quay.io/minio/minio server /data --console-address ":9001"