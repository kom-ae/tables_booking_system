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


router = APIRouter()


@router.get(
    '',
    response_model=List[TableDB],
    summary='Получить все столы кафе',
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
        raise HTTPException(status_code=404, detail='Кафе не найдено')

    only_active = user.role == "user"
    return await tables_crud.get_tables_by_cafe_id(
        cafe_id,
        session,
        only_active=only_active,
    )


@router.post(
    '',
    response_model=TableDB,
    status_code=status.HTTP_201_CREATED,
    summary='Создать стол в кафе',
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
        raise HTTPException(status_code=404, detail='Кафе не найдено')

    return await tables_crud.create_table(cafe_id, table_in, session)


@router.get(
    '/{table_id}',
    response_model=TableDB,
    summary='Получить стол по ID',
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
    only_active = user.role == 'user'
    table = await tables_crud.get_by_id_and_cafe(
        table_id, cafe_id, session, only_active=only_active,
    )
    if not table:
        raise HTTPException(status_code=404, detail='Стол не найден')
    return table


@router.patch(
    '/{table_id}',
    response_model=TableDB,
    summary='Обновить стол',
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
        raise HTTPException(status_code=404, detail='Стол не найден')

    return await tables_crud.update(table, table_in, session)
