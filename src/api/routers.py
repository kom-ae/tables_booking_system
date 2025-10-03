from fastapi import APIRouter

from src.api.endpoints import (
    actions_router,
    auth_router,
    cafes_router,
    slots_router,
    dishes_router,
    tables_router,
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
    prefix='/cafe/{cafe_id}/time_slots',
    tags=['Временные слоты'],
)

main_router.include_router(
    actions_router,
    prefix='/actions',
    tags=['Акции'],
)

main_router.include_router(
    tables_router,
    prefix='/cafe/{cafe_id}/tables',
    tags=['Столы'],
)

main_router.include_router(
    dishes_router,
    prefix='/dishes',
    tags=['Блюда'],
)
