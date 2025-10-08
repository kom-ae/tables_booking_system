set -e

case "$1" in
  backend)
    echo "Запуск миграций базы данных..."
    alembic upgrade head
    create_superuser || true

    echo "Запуск backend (uvicorn)..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000
    ;;
  celery)
    echo "Запуск Celery worker..."
    exec celery -A src.celery.app.celery_app worker --loglevel=info
    ;;
  beat)
    echo "Запуск Celery beat..."
    exec celery -A src.celery.app.celery_app beat --loglevel=info
    ;;
  flower)
    echo "Запуск Flower..."
    exec celery --broker=$CELERY_BROKER_URL flower --port=5555
    ;;
  *)
    exec "$@"
    ;;
esac