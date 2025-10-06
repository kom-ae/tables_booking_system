#!/bin/bash

# Скрипт для очистки тестовых баз данных
# Удаляет все созданные для параллельного выполнения тестов базы данных

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
Использование: $0 [ОПЦИИ]

Опции:
    -h, --help              Показать эту справку
    -a, --all               Удалить все тестовые базы данных
    -w, --worker WORKER     Удалить базу данных конкретного worker'а
    -f, --force             Принудительное удаление (завершить все соединения)
    --dry-run               Показать что будет удалено без выполнения
    --docker                Использовать Docker для подключения к БД

Примеры:
    $0 --all                # Удалить все тестовые базы данных
    $0 --worker gw0         # Удалить базу данных worker'а gw0
    $0 --dry-run            # Показать что будет удалено
    $0 --docker --all       # Удалить все через Docker

EOF
}

# Параметры по умолчанию
DELETE_ALL=""
WORKER_ID=""
FORCE=""
DRY_RUN=""
USE_DOCKER=""

# Переменные окружения для подключения к БД
POSTGRES_USER=${POSTGRES_USER:-test_user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-test_password}
POSTGRES_DB=${POSTGRES_DB:-test_db}
POSTGRES_PORT=${POSTGRES_PORT:-5433}
POSTGRES_HOST=${POSTGRES_HOST:-localhost}

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            DELETE_ALL="true"
            shift
            ;;
        -w|--worker)
            WORKER_ID="$2"
            shift 2
            ;;
        -f|--force)
            FORCE="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --docker)
            USE_DOCKER="true"
            shift
            ;;
        -*)
            error "Неизвестная опция: $1"
            show_help
            exit 1
            ;;
        *)
            error "Неизвестный аргумент: $1"
            show_help
            exit 1
            ;;
    esac
done

# Функция для получения списка тестовых баз данных
get_test_databases() {
    if [[ "$USE_DOCKER" == "true" ]]; then
        # Используем Docker для подключения к PostgreSQL
        docker-compose -f infra/docker-compose.test.yml exec -T test-db psql -U $POSTGRES_USER -d $POSTGRES_DB -t -c "
            SELECT datname 
            FROM pg_database 
            WHERE datname LIKE '${POSTGRES_DB}_%' 
            ORDER BY datname;
        " 2>/dev/null | tr -d ' \n' | sed 's/|/\n/g' | grep -v '^$' || true
    else
        # Используем локальное подключение
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -t -c "
            SELECT datname 
            FROM pg_database 
            WHERE datname LIKE '${POSTGRES_DB}_%' 
            ORDER BY datname;
        " 2>/dev/null | tr -d ' \n' | sed 's/|/\n/g' | grep -v '^$' || true
    fi
}

# Функция для удаления базы данных
drop_database() {
    local db_name="$1"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would drop database '$db_name'"
        return 0
    fi
    
    log "Dropping database: $db_name"
    
    if [[ "$USE_DOCKER" == "true" ]]; then
        # Используем Docker
        if [[ "$FORCE" == "true" ]]; then
            # Завершаем все соединения
            docker-compose -f infra/docker-compose.test.yml exec -T test-db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '$db_name' AND pid <> pg_backend_pid();
            " 2>/dev/null || true
        fi
        
        # Удаляем базу данных
        docker-compose -f infra/docker-compose.test.yml exec -T test-db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
            DROP DATABASE IF EXISTS $db_name;
        " 2>/dev/null || true
        
    else
        # Используем локальное подключение
        if [[ "$FORCE" == "true" ]]; then
            # Завершаем все соединения
            PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '$db_name' AND pid <> pg_backend_pid();
            " 2>/dev/null || true
        fi
        
        # Удаляем базу данных
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "
            DROP DATABASE IF EXISTS $db_name;
        " 2>/dev/null || true
    fi
    
    success "Database '$db_name' dropped"
}

# Основная логика
main() {
    log "Очистка тестовых баз данных"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Режим: DRY RUN (показ без выполнения)"
    fi
    
    if [[ "$USE_DOCKER" == "true" ]]; then
        log "Режим: Docker"
        # Проверяем, что Docker контейнер запущен
        if ! docker-compose -f infra/docker-compose.test.yml ps test-db | grep -q "Up"; then
            error "Docker контейнер test-db не запущен"
            log "Запустите: docker-compose -f infra/docker-compose.test.yml up -d test-db"
            exit 1
        fi
    else
        log "Режим: локальное подключение"
    fi
    
    if [[ "$DELETE_ALL" == "true" ]]; then
        log "Удаление всех тестовых баз данных..."
        
        databases=$(get_test_databases)
        
        if [[ -z "$databases" ]]; then
            log "Тестовые базы данных не найдены"
            return 0
        fi
        
        echo "$databases" | while read -r db_name; do
            if [[ -n "$db_name" ]]; then
                drop_database "$db_name"
            fi
        done
        
        success "Все тестовые базы данных удалены"
        
    elif [[ -n "$WORKER_ID" ]]; then
        log "Удаление базы данных для worker'а: $WORKER_ID"
        
        db_name="test_db_$WORKER_ID"
        drop_database "$db_name"
        
    else
        # Показываем список тестовых баз данных
        log "Список тестовых баз данных:"
        
        databases=$(get_test_databases)
        
        if [[ -z "$databases" ]]; then
            log "Тестовые базы данных не найдены"
        else
            echo "$databases" | while read -r db_name; do
                if [[ -n "$db_name" ]]; then
                    log "  - $db_name"
                fi
            done
            
            log ""
            log "Для удаления всех баз данных используйте: $0 --all"
            log "Для удаления конкретной базы данных используйте: $0 --worker WORKER_ID"
        fi
    fi
}

# Запуск основной функции
main "$@"
