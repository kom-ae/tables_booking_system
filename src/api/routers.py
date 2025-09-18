from fastapi import APIRouter

from src.api.endpoints import user_router  # Импорты ендпоинтов

main_router = APIRouter()

# Подключение роутеров
main_router.include_router(user_router)
