from src.api.endpoints import user_router, auth_router  # noqa
from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router(user_router, prefix='/users', tags=['Пользователи'])
main_router.include_router(
    auth_router,
    prefix='/auth',
    tags=['Аутентификация'],
)
