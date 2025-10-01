from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.dependencies import current_manager, current_user
from src.core.logger import log_endpoint
from src.crud.cafes import CRUDCafe
from src.crud.factory import get_cafe_crud, get_table_crud
from src.crud.tables import CRUDTable
from src.models.user import User
from src.schemas.table import TableCreate, TableDB, TableUpdate
from src.api.responses.tables import (
    tables_list_responses,
    table_create_responses,
    table_get_responses,
    table_update_responses,
)

router = APIRouter()


@router.get(
    '',
    response_model=List[TableDB],
    response_description='Список столов кафе',
    responses=tables_list_responses,
    summary='Получение списка столов в кафе '
    '(только для администратора и менеджера, пользователь - только активные)',
)
@log_endpoint
async def get_tables(
    cafe_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    tables_crud: CRUDTable = Depends(get_table_crud),
    cafe_crud: CRUDCafe = Depends(get_cafe_crud),
) -> List[TableDB]:
    """Получить все столы кафе."""
    cafe = await cafe_crud.get_active(cafe_id, session)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено',
        )

    only_active = not user.is_admin() and not user.is_manager()
    return await tables_crud.get_tables_by_cafe_id(
        cafe_id,
        session,
        only_active=only_active,
    )


@router.post(
    '',
    response_model=TableDB,
    status_code=status.HTTP_201_CREATED,
    summary='Создание стола в кафе (только для администратора и менеджера)',
    response_description='Стол успешно создан',
    responses=table_create_responses,
)
@log_endpoint
async def create_table(
    cafe_id: int,
    table_in: TableCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
    tables_crud: CRUDTable = Depends(get_table_crud),
    cafe_crud: CRUDCafe = Depends(get_cafe_crud),
) -> TableDB:
    """Создать стол."""
    cafe = await cafe_crud.get_active(cafe_id, session)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено',
        )

    return await tables_crud.create_table(cafe_id, table_in, session)


@router.get(
    '/{table_id}',
    response_model=TableDB,
    response_description='Данные стола',
    responses=table_get_responses,
    summary='Получение стола по ID '
    '(только для администратора и менеджера, пользователь - только активные)',
)
@log_endpoint
async def get_table(
    cafe_id: int,
    table_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    tables_crud: CRUDTable = Depends(get_table_crud),
) -> TableDB:
    """Получить стол по ID."""
    only_active = not user.is_admin() and not user.is_manager()
    table = await tables_crud.get_by_id_and_cafe(
        table_id, cafe_id, session, only_active=only_active,
    )
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол не найден',
        )
    return table


@router.patch(
    '/{table_id}',
    response_model=TableDB,
    summary='Обновление стола по ID (только для администратора и менеджера)',
    response_description='Стол успешно обновлён',
    responses=table_update_responses,
)
@log_endpoint
async def update_table(
    cafe_id: int,
    table_id: int,
    table_in: TableUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
    tables_crud: CRUDTable = Depends(get_table_crud),
) -> TableDB:
    """Обновить стол."""
    table = await tables_crud.get_by_id_and_cafe(
        table_id, cafe_id, session, only_active=False,
    )
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол не найден',
        )

    return await tables_crud.update(table, table_in, session)
