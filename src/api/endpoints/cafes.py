from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_admin, current_user
from src.crud.cafes import cafe_crud
from src.models import Cafes, User
from src.schemas.cafes import CafeCreate, CafeDB
from src.core.logger import log_endpoint, log_event

router = APIRouter()


@router.get(
    '/',
    response_model=list[CafeDB],
    response_model_exclude_none=True,
    summary='Получение списка кафе'
    ' (только для администратора, пользователь - только активные).',
    response_description='Список кафе',
)
@log_endpoint()
async def get_all_cafes(
    show_all: bool = Query(
        None,
        description='Показать все кафе'
        '(если не задан, возвращаются только активные кафе)'),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[CafeDB]:
    """Список с данными о кафе."""

    if user.is_admin() and show_all:
        log_event(
            'info',
            'Получены все кафе',
            username=user.username,
            user_id=user.id,
        )
        return await cafe_crud.get_multi_all(session)
    log_event(
        'info',
        'Получены активные кафе',
        username=user.username,
        user_id=user.id,
    )
    return await cafe_crud.get_multi_active(session)


@router.post(
    '/',
    response_model=CafeDB,
    response_model_exclude_none=True,
    summary='Создание кафе (только для администратора)',
    response_description='Данные созданного кафе',
)
@log_endpoint()
async def create_cafe(
    cafe: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_admin)
) -> Cafes:
    """Создание кафе (только для администратора)."""
    db_cafe = await cafe_crud.create_cafe(cafe, session)
    log_event(
        'info',
        f'Создано кафе c id={db_cafe.id}',
        username=user.username,
        user_id=user.id,
    )
    return db_cafe
