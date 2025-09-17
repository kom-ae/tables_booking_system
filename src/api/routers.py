from app.api.endpoints import users  # Импорты ендпоинтов
from fastapi import APIRouter

main_router = APIRouter()

# Подключение роутеров
main_router.include_router(users)
