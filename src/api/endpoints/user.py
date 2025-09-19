from typing import List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.user import (
    current_user_get_responses,
    current_user_update_responses,
    user_create_responses,
    user_update_responses,
    users_list_responses,
)
from src.core.db import get_async_session
from src.core.user import current_admin, current_user
from src.crud.user import user_crud
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(
    prefix='',
    tags=['Пользователи'],
)


# -------------------
# Текущий пользователь
# -------------------
@router.get(
    '/me',
    response_model=UserRead,
    summary='Данные текущего пользователя',
    responses=current_user_get_responses,
)
async def get_current_user_endpoint(
    user: User = Depends(current_user),
) -> UserRead:
    """Возвращает текущего пользователя."""
    return user


@router.patch(
    '/me',
    response_model=UserRead,
    summary='Обновление текущего пользователя',
    responses=current_user_update_responses,
)
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Обновляет данные текущего пользователя."""
    return await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
    )


# -------------------
# Список пользователей (только админ)
# -------------------
@router.get(
    '',
    response_model=List[UserRead],
    summary='Список пользователей (только админ)',
    responses=users_list_responses,
    dependencies=[Depends(current_admin)],
)
async def get_users(
    show_all: bool = Query(
        False,
        description='Показать всех пользователей; False — только активные',
    ),
    session: AsyncSession = Depends(get_async_session),
) -> List[UserRead]:
    """Возвращает список пользователей с фильтром по активности."""
    return await user_crud.get_users(session=session, show_all=show_all)


# -------------------
# Создание пользователя (только админ)
# -------------------
@router.post(
    '',
    response_model=UserRead,
    summary='Создание пользователя',
    responses=user_create_responses,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_admin)],
)
async def create_user(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Создает нового пользователя."""
    return await user_crud.create(obj_in=user_create, session=session)


# -------------------
# Пользователь по ID (только админ)
# -------------------
@router.get(
    '/{user_id}',
    response_model=UserRead,
    summary='Пользователь по ID (только админ)',
    responses=current_user_get_responses,
    dependencies=[Depends(current_admin)],
)
async def get_user_by_id(
    user_id: int = Path(..., title='ID пользователя'),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Возвращает пользователя по ID или 404."""
    return await user_crud.get_or_404(user_id, session)


# -------------------
# Обновление пользователя по ID (только админ)
# -------------------
@router.patch(
    '/{user_id}',
    response_model=UserRead,
    summary='Обновление пользователя по ID (только админ)',
    responses=user_update_responses,
    dependencies=[Depends(current_admin)],
)
async def update_user_by_id(
    user_update: UserUpdate,
    user_id: int = Path(..., description='ID пользователя'),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Обновляет данные пользователя по ID."""
    user = await user_crud.get_or_404(user_id, session)
    return await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
    )
