from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions.user import (
    InvalidPhoneException,
    UserAlreadyExistsException,
)
from src.api.responses.user import (
    current_user_get_responses,
    current_user_update_responses,
    user_create_responses,
    user_update_responses,
    users_list_responses,
)
from src.api.utils.user import parse_bool
from src.core.db import get_async_session
from src.core.user import current_admin, current_user
from src.crud import user_crud
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


# -------------------
# Текущий пользователь
# -------------------
@router.get(
    '/me',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Получение данных текущего пользователя'
    '(доступно только текущему пользователю)',
    responses=current_user_get_responses,
)
async def get_current_user_endpoint(
    user: User = Depends(current_user),
) -> UserRead:
    """Возвращает данные текущего пользователя."""
    return user


@router.patch(
    '/me',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Обновление данных текущего пользователя'
    '(доступно только текущему пользователю)',
    responses=current_user_update_responses,
)
async def update_current_user(
    user_update: UserUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Обновляет данные текущего пользователя."""
    try:
        return await user_crud.update(
            db_obj=user,
            obj_in=user_update,
            session=session,
        )
    except (UserAlreadyExistsException, InvalidPhoneException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# -------------------
# Список пользователей (только админ)
# -------------------
@router.get(
    '/',
    response_model=List[UserRead],
    tags=['Пользователи'],
    summary='Получение списка пользователей (только для администратора)',
    responses=users_list_responses,
)
async def get_users(
    show_all: bool = Depends(parse_bool),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> List[UserRead]:
    """Возвращает список пользователей через CRUD."""
    return await user_crud.get_users(session=session, show_all=show_all)


# -------------------
# Создание пользователя (только админ)
# -------------------
@router.post(
    '',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Создание пользователя',
    responses=user_create_responses,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreate,
    admin: User = Depends(current_admin),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Создаёт нового пользователя через CRUD."""
    try:
        return await user_crud.create(obj_in=user_create, session=session)
    except (UserAlreadyExistsException, InvalidPhoneException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# -------------------
# Пользователь по ID (только админ)
# -------------------
@router.get(
    '/{user_id}',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Получение пользователя по ID (только для администратора)',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Недействительный токен',
        },
        status.HTTP_404_NOT_FOUND: {'description': 'Пользователь не найден'},
    },
)
async def get_user_by_id(
    user_id: int = Path(..., title='ID пользователя'),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Возвращает пользователя по ID через CRUD."""
    user = await user_crud.get(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    return user


# -------------------
# Обновление пользователя по ID (только админ)
# -------------------
@router.patch(
    '/{user_id}',
    response_model=UserRead,
    tags=['Пользователи'],
    summary='Обновление данных пользователя по ID (только для администратора)',
    responses=user_update_responses,
)
async def update_user_by_id(
    user_update: UserUpdate,
    user_id: int = Path(..., description='ID пользователя'),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> UserRead:
    """Обновляет данные пользователя по ID через CRUD."""
    user = await user_crud.get(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    try:
        return await user_crud.update(
            db_obj=user,
            obj_in=user_update,
            session=session,
        )
    except (UserAlreadyExistsException, InvalidPhoneException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
