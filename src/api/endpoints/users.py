from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status

from src.api.responses.user import (
    current_user_get_responses,
    current_user_id_get_responses,
    current_user_update_responses,
    user_create_responses,
    user_update_responses,
    users_list_responses,
)
from src.core.db import get_async_session
from src.core.dependencies import (
    current_admin,
    current_user,
    get_current_user_or_none,
)
from src.core.logger import log_endpoint, project_log
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
@log_endpoint('info')
async def get_current_user_endpoint(
    user: User = Depends(current_user),
) -> UserRead:
    """Возвращает текущего пользователя."""
    project_log('info', 'Текущий пользователь получен', user=user)
    return user


@router.patch(
    '/me',
    response_model=UserRead,
    summary='Обновление данных текущего пользователя '
    '(доступно только текущему пользователю)',
    responses=current_user_update_responses,
)
@log_endpoint('info')
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(current_user),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: get_async_session = Depends(),
) -> UserRead:
    """Обновляет текущего пользователя."""
    project_log(
        'info',
        f'Попытка обновления пользователя {user.id}',
        user=user,
    )
    updated_user = await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
        user=user,
    )
    project_log('info', f'Пользователь {user.id} обновлён', user=user)
    return updated_user


# -------------------
# Список пользователей (только админ)
# -------------------
@router.get(
    '',
    response_model=list[UserRead],
    summary='Получение списка пользователей (только для администратора)',
    responses=users_list_responses,
)
@log_endpoint('info')
async def get_users(
    show_all: bool = Query(None, description='Показать всех пользователей'),
    admin: User = Depends(current_admin),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: get_async_session = Depends(),
) -> list[UserRead]:
    """Возвращает список пользователей."""
    project_log(
        'info',
        f'Запрос списка пользователей, show_all={show_all}',
        user=admin,
    )
    users = await user_crud.get_users(
        session=session,
        show_all=show_all,
        user=admin,
    )
    project_log(
        'info',
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
async def create_user(
    user_create: UserCreate,
    session: get_async_session = Depends(),
    user_crud: CRUDUser = Depends(get_user_crud),
    token_user: Optional[User] = Depends(get_current_user_or_none),
) -> UserRead:
    """Создаёт нового пользователя."""
    initiator_info = (
        f'id={token_user.id}, username={token_user.username}'
        if token_user
        else 'Аноним'
    )
    project_log(
        'info',
        'Попытка создать пользователя '
        f'{getattr(user_create, "email", None)} от {initiator_info}',
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
@log_endpoint('info')
async def get_user_by_id(
    user_id: int = Path(..., description='ID пользователя'),
    admin: User = Depends(current_admin),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: get_async_session = Depends(),
) -> UserRead:
    """Возвращает пользователя по ID."""
    project_log('info', f'Запрошен пользователь {user_id}', user=admin)
    user = await user_crud.get_user_id_or_404(user_id, session)
    project_log('info', f'Пользователь {user.id} получен', user=admin)
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
@log_endpoint('info')
async def update_user_by_id(
    user_update: UserUpdate,
    user_id: int = Path(..., description='ID пользователя'),
    admin: User = Depends(current_admin),
    user_crud: CRUDUser = Depends(get_user_crud),
    session: get_async_session = Depends(),
) -> UserRead:
    """Обновляет пользователя по ID."""
    project_log(
        'info',
        f'Попытка обновления пользователя {user_id}',
        user=admin,
    )
    user = await user_crud.get_user_id_or_404(user_id, session)
    updated_user = await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
        user=admin,
    )
    project_log('info', f'Пользователь {user.id} обновлён', user=admin)
    return updated_user
