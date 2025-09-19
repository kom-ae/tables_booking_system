from fastapi import APIRouter

from src.api.endpoints import cafes_fouter, user_router  # Импорты ендпоинтов

main_router = APIRouter()

# Подключение роутеров
# main_router.include_router(user_router)

main_router.include_router(user_router, prefix='/users', tags=['Пользователи'])

main_router.include_router(
    cafes_fouter,
    prefix='/cafes',
    tags=['Кафе'],
)
