from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_admin, current_user
from src.crud.cafes import cafes_crud
from src.models import Cafes, User
from src.schemas.cafes import CafeCreate, CafeDB

router = APIRouter()


@router.get(
    '/',
    response_model=list[CafeDB],
    response_model_exclude_none=True,
    summary='Получение списка кафе'
    ' (только для администратора, пользователь - только активные).',
    response_description='Список кафе',
)
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
        return await cafes_crud.get_multi_all(session)
    return await cafes_crud.get_multi_active(session)


@router.post(
    '/',
    response_model=CafeDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_admin)],
    summary='Создание кафе (только для администратора)',
    response_description='Данные созданного кафе',
)
async def create_cafe(
    cafe: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Cafes:
    """Создание кафе (только для администратора)."""
    return await cafes_crud.create_cafe(cafe, session)
