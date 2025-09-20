from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_admin, current_user
from src.crud.cafes import cafes_crud
from src.schemas.cafes import CafeDB

router = APIRouter()


@router.get(
    '/',
    response_model=list[CafeDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user), Depends(current_admin)],
    summary='Получение списка кафе'
    ' (только для администратора, пользователь - только активные).',
    response_description='Список кафе'
)
async def get_all_cafes(
    show_all: bool = Query(
        None,
        description='Показать всех кафе'
        '(если не задан, возвращаются только активные кафе)'),
    session: AsyncSession = Depends(get_async_session),
):
    """Список с данными о кафе."""

    return await cafes_crud.get_multi(session)
