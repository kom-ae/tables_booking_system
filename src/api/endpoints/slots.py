from datetime import date
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.slots import (
    slots_list_responses,
    slot_create_responses,
    slot_get_responses,
    slot_update_responses,
    slot_delete_responses,
)
from src.api.validators import (
    cafe_exists,
    require_admin_or_manager,
    slot_in_cafe_exists,
    visible_slot_for_user,
)
from src.core.db import get_async_session
from src.core.logger import log_endpoint
from src.crud.factory import get_slot_crud
from src.crud.slots import CRUDSlot
from src.exceptions.slots import SlotOverlapException
from src.models.cafes import Cafes
from src.models.slots import Slots
from src.models.user import User
from src.schemas.slots import SlotDB, SlotCreate, SlotUpdate
from src.constants import ID_MIN


router = APIRouter(
    prefix='/cafe/{cafe_id}/time_slots',
    tags=['slots'],
)

slot_crud: CRUDSlot = get_slot_crud()


@router.get(
    '',
    response_model=List[SlotDB],
    responses=slots_list_responses,
    summary='Список слотов кафе (пользователь видит только активные)',
)
@log_endpoint('info')
async def list_time_slots(
    cafe: Cafes = Depends(cafe_exists),
    date_: Optional[date] = Query(None, alias='date', description='Дата (на будущее)'),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(),
):
    """Список слотов кафе. Пользователь видит только активные, админ/менеджер — все."""
    if user.is_superuser or user.role in {'admin', 'manager'}:
        return await slot_crud.list_all(session, cafe_id=cafe.id)
    return await slot_crud.list_active(session, cafe_id=cafe.id)


@router.post(
    '',
    response_model=SlotDB,
    status_code=status.HTTP_201_CREATED,
    responses=slot_create_responses,
    summary='Создание слота (только админ/менеджер)',
)
@log_endpoint('info')
async def create_time_slot(
    cafe: Cafes = Depends(cafe_exists),
    payload: SlotCreate = ...,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(require_admin_or_manager),
):
    """Создаёт слот для кафе (admin/manager)."""
    if payload.cafe_id != cafe.id:
        raise HTTPException(
            status_code=400,
            detail='cafe_id в пути и теле должны совпадать',
        )

    try:
        return await slot_crud.create(obj_in=payload, session=session)
    except SlotOverlapException:
        raise
    except ValueError:
        raise SlotOverlapException()


@router.get(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_get_responses,
    summary='Получение слота по ID',
)
@log_endpoint('info')
async def get_time_slot(
    slot: Slots = Depends(visible_slot_for_user),
):
    """
    Возвращает слот по ID.
    - admin/manager/superuser видят любой слот;
    - прочим 404, если слот не активен.
    """
    return slot


@router.patch(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_update_responses,
    summary='Обновление слота (только админ/менеджер)',
)
@log_endpoint('info')
async def update_time_slot(
    cafe_id: int = Path(..., ge=ID_MIN, description='ID кафе'),
    slot: Slots = Depends(slot_in_cafe_exists),
    payload: SlotUpdate = ...,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(require_admin_or_manager),
):
    """Обновляет слот. Пересечения и границы времени валидируются в CRUD."""
    if getattr(payload, 'cafe_id', None) is not None and payload.cafe_id != cafe_id:
        raise HTTPException(status_code=400, detail='cafe_id менять нельзя')

    try:
        return await slot_crud.update(
            db_obj=slot,
            obj_in=payload,
            session=session
        )
    except SlotOverlapException:
        raise
    except ValueError:
        raise SlotOverlapException()


@router.delete(
    '/{time_slot_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses=slot_delete_responses,
    summary='Удаление слота (мягкое — деактивация, только админ/менеджер)',
)
@log_endpoint('info')
async def delete_time_slot(
    slot: Slots = Depends(slot_in_cafe_exists),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(require_admin_or_manager),
):
    """Мягкое удаление: просто деактивируем слот."""
    await slot_crud.delete_soft(db_obj=slot, session=session)
