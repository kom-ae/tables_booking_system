#!/bin/bash

# Скрипт для запуска тестов в Docker с PostgreSQL

set -e

echo "🚀 Запуск тестов в Docker с PostgreSQL..."

# Переходим в директорию infra
cd "$(dirname "$0")/infra"

# Останавливаем и удаляем предыдущие контейнеры
echo "🧹 Очистка предыдущих контейнеров..."
docker-compose -f docker-compose.test.yml down -v --remove-orphans

# Удаляем старые образы тестового раннера
echo "🗑️ Удаление старых образов..."
docker image rm tables_booking_system_team2-test-runner 2>/dev/null || true

# Создаем директорию для данных PostgreSQL если её нет
mkdir -p test-pgdata

# Запускаем тесты
echo "🏃 Запуск тестов..."
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Получаем код выхода последнего контейнера
EXIT_CODE=${PIPESTATUS[0]}

# Останавливаем контейнеры
echo "🛑 Остановка контейнеров..."
docker-compose -f docker-compose.test.yml down

# Выводим результат
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Тесты прошли успешно!"
else
    echo "❌ Тесты завершились с ошибкой (код: $EXIT_CODE)"
fi

exit $EXIT_CODE
