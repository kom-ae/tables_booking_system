# Makefile для управления проектом

.PHONY: help test-docker test-local test-parallel test-serial clean-docker clean-test-db clean-test-databases setup-test-db

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test-docker: ## Запустить тесты в Docker с PostgreSQL
	@echo "🚀 Запуск тестов в Docker с PostgreSQL..."
	@./run_tests.sh --docker-only

test-local: ## Запустить тесты локально (требует локальную PostgreSQL)
	@echo "🏃 Запуск тестов локально..."
	@./run_tests.sh --no-docker

test-parallel: ## Запустить тесты параллельно
	@echo "⚡ Запуск тестов параллельно..."
	@./run_tests.sh --parallel

test-serial: ## Запустить тесты последовательно
	@echo "🐌 Запуск тестов последовательно..."
	@./run_tests.sh --serial

test-fast: ## Запустить только быстрые тесты (unit тесты)
	@echo "🏃 Запуск быстрых тестов..."
	@./run_tests.sh --fast

test-auth: ## Запустить только тесты аутентификации
	@echo "🔐 Запуск тестов аутентификации..."
	@./run_tests.sh --auth

test-users: ## Запустить только тесты пользователей
	@echo "👥 Запуск тестов пользователей..."
	@./run_tests.sh --users

test-cafes: ## Запустить только тесты кафе
	@echo "☕ Запуск тестов кафе..."
	@./run_tests.sh --cafes

test-coverage: ## Запустить тесты с покрытием кода
	@echo "📊 Запуск тестов с покрытием кода..."
	@./run_tests.sh --coverage

clean-docker: ## Очистить Docker контейнеры и образы
	@echo "🧹 Очистка Docker контейнеров и образов..."
	@docker-compose -f infra/docker-compose.test.yml down -v --remove-orphans
	@docker image rm tables_booking_system_team2-test-runner 2>/dev/null || true
	@docker system prune -f

clean-test-db: ## Очистить тестовую базу данных
	@echo "🗑️ Очистка тестовой базы данных..."
	@rm -rf infra/test-pgdata

clean-test-databases: ## Очистить все тестовые базы данных (для параллельного выполнения)
	@echo "🗑️ Очистка всех тестовых баз данных..."
	@./cleanup_test_databases.sh --all --force

clean-test-databases-dry-run: ## Показать какие тестовые базы данных будут удалены
	@echo "🔍 Просмотр тестовых баз данных для удаления..."
	@./cleanup_test_databases.sh --dry-run

setup-test-db: ## Настроить локальную тестовую базу данных
	@echo "🔧 Настройка локальной тестовой базы данных..."
	@echo "Создайте базу данных PostgreSQL с параметрами:"
	@echo "  Host: localhost"
	@echo "  Port: 5433"
	@echo "  Database: test_db"
	@echo "  User: test_user"
	@echo "  Password: test_password"
	@echo ""
	@echo "Или используйте команду: make test-docker"

install-deps: ## Установить зависимости для тестов
	@echo "📦 Установка зависимостей для тестов..."
	@pip install -r requirements.txt
	@pip install pytest-xdist pytest-cov

lint: ## Запустить линтеры
	@echo "🔍 Запуск линтеров..."
	@ruff check src/ tests/
	@black --check src/ tests/
	@isort --check-only src/ tests/

format: ## Форматировать код
	@echo "✨ Форматирование кода..."
	@black src/ tests/
	@isort src/ tests/
	@ruff check --fix src/ tests/
