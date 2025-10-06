set -e

echo "🚀 Запуск миграций базы данных..."
alembic upgrade head || true

echo "👤 Создание суперпользователя (если нужно)..."
create_superuser || true

case "$1" in
  celery)
    echo "📦 Запуск Celery worker..."
    shift
    exec celery -A src.celery.celery_app.celery_app worker --loglevel=info "$@"
    ;;
  flower)
    echo "🌸 Запуск Flower..."
    shift
    exec celery -A src.celery.celery_app.celery_app flower --port=5555 "$@"
    ;;
  *)
    echo "🖥 Запуск FastAPI (Uvicorn)..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000 "$@"
    ;;
esac