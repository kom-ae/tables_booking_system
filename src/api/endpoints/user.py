from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select

from src.core.user import (
    auth_backend,
    current_admin,
    current_user,
    fastapi_users,
)
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# -------------------
# Auth routes (аутентификация)
# -------------------
auth_router = fastapi_users.get_auth_router(auth_backend)
router.include_router(auth_router, prefix='/auth', tags=['Аутентификация'])

for route in router.routes:
    if route.path == '/auth/login' and route.methods == {'POST'}:
        route.summary = 'Аутентификация пользователя'
    elif route.path == '/auth/logout' and route.methods == {'POST'}:
        route.summary = 'Выход из аккаунта'

# -------------------
# Пользователи (свои ручки вместо users_router)
# -------------------


@router.get(
    '/users',
    response_model=List[UserRead],
    tags=['Пользователи'],
    summary='Получение списка пользователей (только для администратора)',
)
async def get_users(
    show_all: bool = Query(
        default=None,
        description='Показать всех пользователей'
        '(если не задан, возвращаются только'
        'пользователи с активным статусом)',
    ),
    admin: User = Depends(current_admin),
) -> List[UserRead]:
    """Возвращает список пользователей."""
    stmt = select(User)
    if not show_all:
        stmt = stmt.where(User.is_active)
    result = await fastapi_users.user_db.session.execute(stmt)
    return result.scalars().all()


@router.post(
    '/users',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Создание пользователя',
)
async def create_user(user_create: UserCreate) -> UserRead:
    """Создаёт нового пользователя."""
    user_manager = await fastapi_users.get_user_manager()
    return await user_manager.create(user_create)


@router.get(
    '/users/{user_id}',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Получение пользователя по ID (только для администратора)',
)
async def get_user_by_id(
    user_id: int = Path(...),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Возвращает пользователя по его ID."""
    user = await fastapi_users.user_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    return user


@router.patch(
    '/users/{user_id}',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Обновление данных пользователя по ID (только для администратора)',
)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    admin: User = Depends(current_admin),
) -> UserRead:
    """Обновляет данные пользователя по ID."""
    user = await fastapi_users.user_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    return await fastapi_users.user_db.update(
        user,
        user_update.model_dump(exclude_unset=True),
    )


@router.get(
    '/users/me',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Получение данных текущего пользователя'
    '(доступно только текущему пользователю)',
)
async def get_current_user(user: User = Depends(current_user)) -> UserRead:
    """Возвращает данные текущего пользователя."""
    return user


@router.patch(
    '/users/me',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Обновление данных текущего пользователя'
    '(доступно только текущему пользователю)',
)
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(current_user),
) -> UserRead:
    """Обновляет данные текущего пользователя."""
    return await fastapi_users.user_db.update(
        user,
        user_update.model_dump(exclude_unset=True),
    )
