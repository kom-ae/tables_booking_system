from fastapi import APIRouter
from app.api.endpoints import users  # Импорты ендпоинтов


main_router = APIRouter()

# Подключение роутеров
main_router.include_router(users)
