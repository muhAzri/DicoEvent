.PHONY: help install shell run migrate makemigrations createsuperuser test lint format clean db-start db-stop db-reset

help:
	@echo "Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  shell          - Activate pipenv shell"
	@echo "  run            - Start development server"
	@echo "  migrate        - Apply database migrations"
	@echo "  makemigrations - Create new migrations"
	@echo "  createsuperuser - Create Django superuser"
	@echo "  test           - Run tests"
	@echo "  lint           - Check code formatting with black"
	@echo "  format         - Format code with black"
	@echo "  clean          - Remove cache files"
	@echo "  db-start       - Start PostgreSQL service"
	@echo "  db-stop        - Stop PostgreSQL service"
	@echo "  db-reset       - Reset database (migrate from scratch)"

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

db-start:
	brew services start postgresql@17

db-stop:
	brew services stop postgresql@17

db-reset:
	pipenv run python manage.py migrate