from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import cafe_create_responses, cafes_list_responses
from src.api.validators import check_duplicate_cafe
from src.core.db import get_async_session
from src.core.logger import log_endpoint, log_event
from src.core.user import current_admin, current_user
from src.crud.factory import get_cafe_crud
from src.models import User
from src.schemas.cafes import CafeCreate, CafeDB


cafe_crud = get_cafe_crud()

router = APIRouter()


@router.get(
    '/',
    response_model=list[CafeDB],
    response_model_exclude_none=True,
    response_description='Список кафе',
    responses=cafes_list_responses,
    summary='Получение списка кафе'
    ' (только для администратора, пользователь - только активные).',
)
@log_endpoint()
async def get_cafes(
    show_all: bool = Query(
        None,
        description='Показать все кафе'
        '(если не задан, возвращаются только активные кафе)'),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[CafeDB]:
    """Список с данными о кафе."""
    log_message = 'Получение {}'.format(
        'всех кафе.' if user.is_admin() and show_all else 'активных кафе.',
    )
    log_event(
        'info',
        log_message,
        username=user.username,
        user_id=user.id,
    )
    if user.is_admin() and show_all:
        return await cafe_crud.get_multi_all(session)
    return await cafe_crud.get_multi_active(session)


@router.post(
    '/',
    response_model=CafeDB,
    response_model_exclude_none=True,
    response_description='Данные созданного кафе',
    responses=cafe_create_responses,
    summary='Создание кафе (только для администратора)',
)
@log_endpoint()
async def create_cafe(
    cafe: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_admin),
) -> CafeDB:
    """Создание кафе (только для администратора)."""
    await check_duplicate_cafe(cafe=cafe, session=session)
    return await cafe_crud.create_cafe(
        obj_in=cafe,
        user=user,
        session=session,
    )
