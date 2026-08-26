.PHONY: help install dev test lint format migrate clean run docker docker-build docker-down

help:
	@echo "Online Shop Django - Makefile Commands"
	@echo ""
	@echo "Virtual Environment:"
	@echo "  make venv        - Virtual environment yaratish"
	@echo "  make install     - Paketlarni o'rnatish"
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Development serverini ishga tushirish"
	@echo "  make run         - Development serverini ishga tushirish (8000 porta)"
	@echo "  make migrate     - Database migratsiyalarini bajarish"
	@echo "  make migrations  - Yangi migratsiyalarni yaratish"
	@echo "  make seed        - Sample ma'lumotlarni qo'shish"
	@echo "  make shell       - Django shell'ga kirish"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Barcha testlarni bajarish"
	@echo "  make pytest      - Pytest bilan testlarni bajarish"
	@echo "  make coverage    - Coverage bilan testlarni bajarish"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint        - Kodni lint'iga birikitirish (flake8)"
	@echo "  make format      - Kodni formatlash (black)"
	@echo "  make check       - Kodni tekshirish"
	@echo ""
	@echo "Database:"
	@echo "  make db-reset    - Databaseni reset qilish"
	@echo "  make db-backup   - Database backup olish"
	@echo ""
	@echo "Admin:"
	@echo "  make admin       - Admin foydalanuvichiyu yaratish"
	@echo ""
	@echo "Static Files:"
	@echo "  make static      - Static fayllarni to'plash"
	@echo "  make clean-static- Static fayllarni o'chirish"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Python cache va backup fayllarni o'chirish"
	@echo "  make clean-all   - Barcha generatsion fayllarni o'chirish"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up   - Docker containers'ni ishga tushirish"
	@echo "  make docker-down - Docker containers'ni o'chirish"
	@echo "  make docker-build- Docker image'ni rebuild qilish"
	@echo "  make docker-logs - Docker logs ko'rish"
	@echo ""
	@echo "Production:"
	@echo "  make prod-check  - Production checklist'ni oʻqish"
	@echo "  make docs        - Dokumentatsiyani oʻqish"

# Virtual Environment
venv:
	python -m venv venv

install:
	pip install -r requirements.txt

# Development
dev:
	python manage.py runserver

run:
	python manage.py runserver 0.0.0.0:8000

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

seed:
	python manage.py seed_data

shell:
	python manage.py shell

# Testing
test:
	python manage.py test

pytest:
	pytest -v

coverage:
	pytest --cov=store --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated: htmlcov/index.html"

# Code Quality
lint:
	flake8 store core --max-line-length=100 --exclude=migrations

format:
	black store core --line-length=100

check:
	python manage.py check

# Database
db-reset:
	python manage.py flush --no-input
	python manage.py migrate
	python manage.py seed_data

db-backup:
	python manage.py dumpdata > backup_`date +%Y%m%d_%H%M%S`.json
	@echo "Backup created: backup_*.json"

# Admin
admin:
	python manage.py createsuperuser

# Static Files
static:
	python manage.py collectstatic --noinput

clean-static:
	rm -rf staticfiles
	rm -rf static

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .tox
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "Cleaned up!"

clean-all: clean
	rm -rf db.sqlite3
	rm -rf venv
	rm -rf media
	rm -rf logs
	rm -rf staticfiles
	@echo "Full cleanup done!"

# Docker
docker-up:
	docker-compose up -d
	@echo "Docker containers started!"
	@echo "App: http://localhost"
	@echo "Admin: http://localhost/admin"

docker-down:
	docker-compose down

docker-build:
	docker-compose build --no-cache

docker-logs:
	docker-compose logs -f web

docker-init: docker-up
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py seed_data
	@echo "Docker setup complete!"

# Production
prod-check:
	@cat DEPLOYMENT_CHECKLIST.md

docs:
	@echo "Opening documentation..."
	@echo ""
	@echo "Available documentation:"
	@echo "1. README.md - Project overview"
	@echo "2. QUICKSTART.md - 30-second setup"
	@echo "3. SETUP.md - Detailed setup guide"
	@echo "4. API_DOCUMENTATION.md - API reference"
	@echo "5. DEPLOYMENT_CHECKLIST.md - Deployment checklist"
	@echo "6. COMPLETION_REPORT.md - Project completion report"

# Default
.DEFAULT_GOAL := help
