import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.user import (
    current_user_get_responses,
    current_user_id_get_responses,
    current_user_update_responses,
    user_create_responses,
    user_update_responses,
    users_list_responses,
)
from src.core.db import get_async_session  # noqa
from src.core.dependencies import (
    current_admin,
    current_user,
    get_current_user_or_none,
)
from src.core.logger import log_endpoint, logger
from src.crud.factory import CRUDUser, get_user_crud
from src.models.user import User
from src.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter()


# -------------------
# Текущий пользователь
# -------------------
@router.get(
    '/me',
    response_model=UserRead,
    summary='Получение данных текущего пользователя '
    '(доступно только текущему пользователю)',
    responses=current_user_get_responses,
)
@log_endpoint
async def get_current_user_endpoint(
    user: User = Depends(current_user),
) -> UserRead:
    """Возвращает текущего пользователя."""
    logger.info(f'Текущий пользователь c id:{user.id} получен', user=user)
    return user


@router.patch(
    '/me',
    response_model=UserRead,
    summary='Обновление данных текущего пользователя '
    '(доступно только текущему пользователю)',
    responses=current_user_update_responses,
)
@log_endpoint
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(current_user),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Обновляет текущего пользователя."""
    logger.info(f'Попытка обновления пользователя с id:{user.id}', user=user)

    return await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
        user=user,
    )


# -------------------
# Список пользователей (только админ)
# -------------------
@router.get(
    '',
    response_model=list[UserRead],
    summary='Получение списка пользователей (только для администратора)',
    responses=users_list_responses,
)
@log_endpoint
async def get_users(
    show_all: bool = Query(None, description='Показать всех пользователей'),
    admin: User = Depends(current_admin),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: AsyncSession = Depends(get_async_session),
) -> list[UserRead]:
    """Возвращает список пользователей."""
    logger.info(
        f'Запрос списка пользователей, show_all={show_all}',
        user=admin,
    )
    users = await user_crud.get_users(
        session=session,
        show_all=show_all,
        user=admin,
    )
    logger.info(
        f'Список пользователей получен, count={len(users)}',
        user=admin,
    )
    return users


# -------------------
# Создание пользователя (публичная регистрация)
# -------------------
@router.post(
    '',
    response_model=UserRead,
    summary='Создание пользователя',
    responses=user_create_responses,
    status_code=status.HTTP_201_CREATED,
)
@log_endpoint
async def create_user(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session),
    user_crud: CRUDUser = Depends(get_user_crud),
    token_user: Optional[User] = Depends(get_current_user_or_none),
) -> UserRead:
    """Создаёт нового пользователя."""
    initiator_info = (
        f'id={token_user.id}, username={token_user.username}'
        if token_user
        else 'Аноним'
    )

    email = getattr(user_create, 'email', None)
    email_hash = (
        hashlib.md5(email.encode()).hexdigest()[:8] if email else 'unknown'
    )

    logger.info(
        f'Попытка создать пользователя '
        f'(hash: {email_hash}) от пользователя: {initiator_info}',
        user=token_user,
    )

    return await user_crud.create(
        obj_in=user_create,
        session=session,
        user=token_user,
    )


# -------------------
# Пользователь по ID (только админ)
# -------------------
@router.get(
    '/{user_id}',
    response_model=UserRead,
    summary='Получение пользователя по ID (только для администратора)',
    responses=current_user_id_get_responses,
)
@log_endpoint
async def get_user_by_id(
    user_id: int = Path(..., description='ID пользователя'),
    admin: User = Depends(current_admin),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Возвращает пользователя по ID."""
    logger.info(f'Запрошен пользователь {user_id}', user=admin)
    user = await user_crud.get_user_id_or_404(user_id, session)
    logger.info(f'Пользователь c id:{user.id} получен', user=admin)
    return user


# -------------------
# Обновление пользователя по ID (только админ)
# -------------------
@router.patch(
    '/{user_id}',
    response_model=UserRead,
    summary='Обновление данных пользователя по ID (только для администратора)',
    responses=user_update_responses,
)
@log_endpoint
async def update_user_by_id(
    user_update: UserUpdate,
    user_id: int = Path(..., description='ID пользователя'),
    admin: User = Depends(current_admin),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: AsyncSession = Depends(get_async_session),
    token_user: Optional[User] = Depends(get_current_user_or_none),
) -> UserRead:
    """Обновляет пользователя по ID."""
    initiator_info = (
        f'id={token_user.id}, username={token_user.username}'
        if token_user
        else 'Аноним'
    )
    logger.info(
        f'Попытка обновления пользователя {user_id} '
        f'от пользователя c: {initiator_info}',
        user=admin,
    )
    user = await user_crud.get_user_id_or_404(user_id, session)

    return await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
        user=admin,
    )
