from fastapi import APIRouter

from src.api.endpoints import (
    auth_router,
    cafes_router,
    slots_router,
    users_router,
)

main_router = APIRouter()

main_router.include_router(
    users_router,
    prefix='/users',
    tags=['Пользователи'],
)
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
main_router.include_router(
    slots_router,
    tags=["Слоты"],
)
