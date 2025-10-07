#!/bin/bash

# Скрипт для запуска тестов с различными режимами выполнения
# Поддерживает последовательное и параллельное выполнение

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Функция для показа справки
show_help() {
    cat << EOF
Использование: $0 [ОПЦИИ] [ТЕСТЫ]

Опции:
    -h, --help              Показать эту справку
    -p, --parallel          Запустить тесты параллельно (по умолчанию)
    -s, --serial            Запустить тесты последовательно
    -w, --workers N         Количество worker'ов для параллельного выполнения (по умолчанию: auto)
    -v, --verbose           Подробный вывод
    -q, --quiet             Минимальный вывод
    -c, --coverage          Запустить с покрытием кода
    -f, --fast              Быстрый режим (только unit тесты)
    -i, --integration       Только интеграционные тесты
    -a, --auth              Только тесты аутентификации
    -u, --users             Только тесты пользователей
    -r, --cafes             Только тесты кафе
    --no-docker             Запустить тесты локально (без Docker)
    --docker-only           Запустить тесты только в Docker
    --clean                 Очистить тестовые данные перед запуском

Примеры:
    $0                                    # Параллельное выполнение всех тестов
    $0 -s                                 # Последовательное выполнение всех тестов
    $0 -w 4                               # Параллельное выполнение с 4 worker'ами
    $0 -f                                 # Быстрый режим (только unit тесты)
    $0 -a                                 # Только тесты аутентификации
    $0 tests/test_auth.py                 # Конкретный файл тестов
    $0 --no-docker                        # Локальное выполнение
    $0 --docker-only                      # Только Docker

EOF
}

# Параметры по умолчанию
MODE="parallel"
WORKERS="auto"
VERBOSE=""
QUIET=""
COVERAGE=""
FAST=""
INTEGRATION=""
AUTH=""
USERS=""
CAFES=""
NO_DOCKER=""
DOCKER_ONLY=""
CLEAN=""
TEST_ARGS=""

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--parallel)
            MODE="parallel"
            shift
            ;;
        -s|--serial)
            MODE="serial"
            shift
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -q|--quiet)
            QUIET="-q"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=src --cov-report=html --cov-report=term"
            shift
            ;;
        -f|--fast)
            FAST="-m unit"
            shift
            ;;
        -i|--integration)
            INTEGRATION="-m integration"
            shift
            ;;
        -a|--auth)
            AUTH="-m auth"
            shift
            ;;
        -u|--users)
            USERS="-m users"
            shift
            ;;
        -r|--cafes)
            CAFES="-m cafes"
            shift
            ;;
        --no-docker)
            NO_DOCKER="true"
            shift
            ;;
        --docker-only)
            DOCKER_ONLY="true"
            shift
            ;;
        --clean)
            CLEAN="true"
            shift
            ;;
        -*)
            error "Неизвестная опция: $1"
            show_help
            exit 1
            ;;
        *)
            TEST_ARGS="$TEST_ARGS $1"
            shift
            ;;
    esac
done

# Функция для запуска тестов локально
run_local_tests() {
    log "Запуск тестов локально..."
    
    # Проверяем наличие виртуального окружения
    if [[ -z "$VIRTUAL_ENV" ]]; then
        warning "Виртуальное окружение не активировано"
        if [[ -f "venv/bin/activate" ]]; then
            log "Активируем виртуальное окружение..."
            source venv/bin/activate
        else
            error "Виртуальное окружение не найдено. Создайте его с помощью: python -m venv venv"
            exit 1
        fi
    fi
    
    # Устанавливаем переменные окружения для тестов
    export DB_ENGINE=postgres
    export DB_HOST=${POSTGRES_HOST:-localhost}
    export DB_PORT=${POSTGRES_PORT:-5433}
    export DB_NAME=${POSTGRES_DB:-test_db}
    export DB_USER=${POSTGRES_USER:-test_user}
    export DB_PASSWORD=${POSTGRES_PASSWORD:-test_password}
    export SECRET=test_secret_key_for_testing_only
    export JWT_ALGORITHM=HS256
    export ACCESS_TOKEN_EXPIRE_MINUTES=30
    export LOG_FILE=test.log
    export MAX_BYTES=1048576
    export BACKUP_COUNT=1
    
    # Формируем команду pytest
    PYTEST_CMD="python -m pytest"
    
    if [[ "$MODE" == "parallel" ]]; then
        PYTEST_CMD="$PYTEST_CMD -n $WORKERS"
    fi
    
    if [[ -n "$VERBOSE" ]]; then
        PYTEST_CMD="$PYTEST_CMD $VERBOSE"
    fi
    
    if [[ -n "$QUIET" ]]; then
        PYTEST_CMD="$PYTEST_CMD $QUIET"
    fi
    
    if [[ -n "$COVERAGE" ]]; then
        PYTEST_CMD="$PYTEST_CMD $COVERAGE"
    fi
    
    if [[ -n "$FAST" ]]; then
        PYTEST_CMD="$PYTEST_CMD $FAST"
    fi
    
    if [[ -n "$INTEGRATION" ]]; then
        PYTEST_CMD="$PYTEST_CMD $INTEGRATION"
    fi
    
    if [[ -n "$AUTH" ]]; then
        PYTEST_CMD="$PYTEST_CMD $AUTH"
    fi
    
    if [[ -n "$USERS" ]]; then
        PYTEST_CMD="$PYTEST_CMD $USERS"
    fi
    
    if [[ -n "$CAFES" ]]; then
        PYTEST_CMD="$PYTEST_CMD $CAFES"
    fi
    
    PYTEST_CMD="$PYTEST_CMD --tb=short --strict-markers --disable-warnings"
    
    if [[ -n "$TEST_ARGS" ]]; then
        PYTEST_CMD="$PYTEST_CMD $TEST_ARGS"
    else
        PYTEST_CMD="$PYTEST_CMD tests/"
    fi
    
    log "Выполняем команду: $PYTEST_CMD"
    eval $PYTEST_CMD
}

# Функция для запуска тестов в Docker
run_docker_tests() {
    log "Запуск тестов в Docker..."
    
    # Проверяем наличие docker-compose
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose не найден. Установите Docker Compose."
        exit 1
    fi
    
    # Очистка если запрошена
    if [[ "$CLEAN" == "true" ]]; then
        log "Очистка тестовых данных..."
        docker-compose -f infra/docker-compose.test.yml down -v
        docker-compose -f infra/docker-compose.test.yml rm -f
    fi
    
    # Запуск тестовой базы данных
    log "Запуск тестовой базы данных..."
    docker-compose -f infra/docker-compose.test.yml up -d test-db
    
    # Ждем готовности базы данных
    log "Ожидание готовности базы данных..."
    timeout=60
    while ! docker-compose -f infra/docker-compose.test.yml exec test-db pg_isready -U test_user -d test_db; do
        sleep 1
        timeout=$((timeout - 1))
        if [[ $timeout -eq 0 ]]; then
            error "Таймаут ожидания готовности базы данных"
            exit 1
        fi
    done
    
    # Формируем команду для Docker
    DOCKER_CMD="docker-compose -f infra/docker-compose.test.yml run --rm test-runner"
    
    if [[ "$MODE" == "serial" ]]; then
        DOCKER_CMD="$DOCKER_CMD python -m pytest /app/tests -v --tb=short"
    else
        DOCKER_CMD="$DOCKER_CMD python -m pytest /app/tests -v --tb=short -n $WORKERS"
    fi
    
    if [[ -n "$FAST" ]]; then
        DOCKER_CMD="$DOCKER_CMD $FAST"
    fi
    
    if [[ -n "$INTEGRATION" ]]; then
        DOCKER_CMD="$DOCKER_CMD $INTEGRATION"
    fi
    
    if [[ -n "$AUTH" ]]; then
        DOCKER_CMD="$DOCKER_CMD $AUTH"
    fi
    
    if [[ -n "$USERS" ]]; then
        DOCKER_CMD="$DOCKER_CMD $USERS"
    fi
    
    if [[ -n "$CAFES" ]]; then
        DOCKER_CMD="$DOCKER_CMD $CAFES"
    fi
    
    if [[ -n "$TEST_ARGS" ]]; then
        DOCKER_CMD="$DOCKER_CMD $TEST_ARGS"
    fi
    
    log "Выполняем команду: $DOCKER_CMD"
    eval $DOCKER_CMD
    
    # Останавливаем контейнеры
    log "Остановка тестовых контейнеров..."
    docker-compose -f infra/docker-compose.test.yml down
}

# Основная логика
main() {
    log "Запуск тестов системы бронирования столов"
    log "Режим: $MODE"
    
    if [[ "$MODE" == "parallel" ]]; then
        log "Количество worker'ов: $WORKERS"
    fi
    
    if [[ -n "$FAST" ]]; then
        log "Режим: быстрый (только unit тесты)"
    fi
    
    if [[ -n "$INTEGRATION" ]]; then
        log "Режим: интеграционные тесты"
    fi
    
    if [[ -n "$AUTH" ]]; then
        log "Режим: тесты аутентификации"
    fi
    
    if [[ -n "$USERS" ]]; then
        log "Режим: тесты пользователей"
    fi
    
    if [[ -n "$CAFES" ]]; then
        log "Режим: тесты кафе"
    fi
    
    if [[ "$NO_DOCKER" == "true" ]]; then
        run_local_tests
    elif [[ "$DOCKER_ONLY" == "true" ]]; then
        run_docker_tests
    else
        # По умолчанию пробуем Docker, если не получается - локально
        if command -v docker-compose &> /dev/null; then
            run_docker_tests
        else
            warning "Docker Compose не найден, запускаем тесты локально"
            run_local_tests
        fi
    fi
    
    success "Тесты завершены"
}

# Запуск основной функции
main "$@"
