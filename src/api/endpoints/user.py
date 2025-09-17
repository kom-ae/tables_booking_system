from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import (
    UserManager,
    auth_backend,
    current_admin,
    current_user,
    fastapi_users,
)
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# -------------------
# Auth routes
# -------------------
auth_router = fastapi_users.get_auth_router(auth_backend)
router.include_router(auth_router, prefix='/auth/jwt', tags=['Аутентификация'])

for route in router.routes:
    if route.path == '/auth/jwt/login' and route.methods == {'POST'}:
        route.summary = 'Аутентификация пользователя'
    elif route.path == '/auth/jwt/logout' and route.methods == {'POST'}:
        route.summary = 'Выход из аккаунта'


# -------------------
# Пользователи
# -------------------
@router.get(
    '/users',
    response_model=List[UserRead],
    tags=['Пользователи'],
    summary='Список пользователей (только админ)',
)
async def get_users(
    show_all: bool = Query(
        default=None,
        description='Все или только активные',
    ),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> List[UserRead]:
    """Возвращает пользователей."""
    stmt = select(User)
    if not show_all:
        stmt = stmt.where(User.is_active)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post(
    '/users',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Создание пользователя',
)
async def create_user(
    user_create: UserCreate,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager),
) -> UserRead:
    """Создает нового пользователя."""
    return await user_manager.create(user_create)


@router.get(
    '/users/{user_id}',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Пользователь по ID (только админ)',
)
async def get_user_by_id(
    user_id: int = Path(...),
    user_manager: UserManager = Depends(fastapi_users.get_user_manager),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Возвращает пользователя по ID."""
    user = await user_manager.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найден',
        )
    return user


@router.patch(
    '/users/{user_id}',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Обновление пользователя по ID (только админ)',
)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Обновляет данные пользователя."""
    user = await user_manager.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найден',
        )
    return await user_manager.update(user_update, user)


@router.get(
    '/users/me',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Текущий пользователь',
)
async def get_current_user(user: User = Depends(current_user)) -> UserRead:
    """Данные текущего пользователя."""
    return user


@router.patch(
    '/users/me',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Обновление текущего пользователя',
)
async def update_current_user(
    user_update: UserUpdate,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager),
    user: User = Depends(current_user),
) -> UserRead:
    """Обновляет данные текущего пользователя."""
    return await user_manager.update(user_update, user)
