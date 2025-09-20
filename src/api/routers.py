from fastapi import APIRouter
from src.api.endpoints import cafes_router, user_router, auth_router  # noqa

from src.api.endpoints import user_router  # Импорты ендпоинтов

main_router = APIRouter()

main_router.include_router(user_router, prefix='/users', tags=['Пользователи'])
main_router.include_router(
    auth_router,
    prefix='/auth',
    tags=['Аутентификация'],
)
main_router.include_router(
    cafes_router,
    prefix='/cafes',
    tags=['Кафе'],
)
