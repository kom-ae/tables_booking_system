#!/bin/sh

echo "Запуск миграций базы данных..."
alembic upgrade head
create_superuser
uvicorn src.main:app --host 0.0.0.0 --port 8000
celery -A src.celery.app.celery_app worker --loglevel=info