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
from src.core.logger import log_endpoint, log_event
from src.core.user import current_admin, current_user
from src.crud.factory import get_user_crud
from src.models.user import User
from src.schemas.users import UserCreate, UserRead, UserUpdate

user_crud = get_user_crud()

router = APIRouter()


# -------------------
# Текущий пользователь
# -------------------
@router.get(
    '/me',
    response_model=UserRead,
    summary='Получение данных текущего пользователя'
    ' (доступно только текущему пользователю)',
    responses=current_user_get_responses,
)
@log_endpoint('info')
async def get_current_user_endpoint(
    user: User = Depends(current_user),
) -> UserRead:
    """Возвращает текущего пользователя."""
    log_event(
        'info',
        'Получены данные текущего пользователя',
        username=user.username,
        user_id=user.id,
    )
    return user


@router.patch(
    '/me',
    response_model=UserRead,
    summary='Обновление данных текущего пользователя'
    ' (доступно только текущему пользователю)',
    responses=current_user_update_responses,
)
@log_endpoint('info')
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Обновляет данные текущего пользователя."""
    updated_user = await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
        user_id=user.id,
    )

    log_event(
        'info',
        f'Обновлены данные пользователя {user.id}',
        username=user.username,
        user_id=user.id,
    )
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
    show_all: bool = Query(
        False,
        description='Показать всех пользователей; False — только активные',
    ),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> list[UserRead]:
    """Возвращает список пользователей с фильтром по активности."""
    users = await user_crud.get_users(
        session=session,
        show_all=show_all,
        current_user=admin,
    )
    log_event(
        'info',
        f'Получен список пользователей, show_all={show_all}',
        username=admin.username,
        user_id=admin.id,
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
@log_endpoint('info')
async def create_user(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Создает нового пользователя (хэширование пароля выполняется в CRUD)."""
    new_user = await user_crud.create(obj_in=user_create, session=session)

    log_event(
        'info',
        f'Создан новый пользователь {new_user.id}',
        username=new_user.username,
        user_id=new_user.id,
    )
    return new_user


# -------------------
# Пользователь по ID (только админ)
# -------------------
@router.get(
    '/{user_id}',
    response_model=UserRead,
    summary='Получение пользователя по ID (только для администратора)',
    responses=current_user_get_responses,
)
@log_endpoint('info')
async def get_user_by_id(
    user_id: int = Path(..., title='ID пользователя'),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Возвращает пользователя по ID или 404."""
    user = await user_crud.get_user_id_or_404(user_id, session)
    log_event(
        'info',
        f'Получен пользователь {user.id}',
        username=admin.username,
        user_id=admin.id,
    )
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
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Обновляет данные пользователя по ID."""
    user = await user_crud.get_user_id_or_404(user_id, session)

    updated_user = await user_crud.update(
        db_obj=user,
        obj_in=user_update,
        session=session,
        user_id=admin.id,
    )

    log_event(
        'info',
        f'Обновлены данные пользователя {user.id}',
        username=admin.username,
        user_id=admin.id,
    )
    return updated_user
