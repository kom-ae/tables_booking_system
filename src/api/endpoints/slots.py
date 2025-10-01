from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.slots import (
    slot_create_responses,
    slot_delete_responses,
    slot_get_responses,
    slot_update_responses,
    slots_list_responses,
)
from src.api.validators import (
    cafe_existence,
    slot_in_cafe_exists,
    visible_slot_for_user,
)
from src.core.db import get_async_session
from src.core.dependencies import current_manager, current_user
from src.crud.factory import get_slot_crud
from src.exceptions.slots import (
    CafeIdChangeForbiddenException,
    CafeIdMismatchException,
)
from src.models.slot import Slot
from src.models.user import User
from src.schemas.slots import SlotCreate, SlotDB, SlotShortDB, SlotUpdate

router = APIRouter()
slot_crud = get_slot_crud()


@router.get(
    '',
    response_model=List[SlotShortDB],
    responses=slots_list_responses,
    summary='Список временных слотов кафе',
    response_description=(
        'Список слотов. Менеджер/админ видят все; '
        'пользователь — только активные.'
    ),
)
async def list_time_slots(
    cafe_id: int = Path(..., description='ID кафе'),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> List[SlotShortDB]:
    """Список слотов кафе."""
    await cafe_existence(session, cafe_id)

    show_all = user.is_manager()
    slots = await slot_crud.list(
        session,
        cafe_id=cafe_id,
        only_active=not show_all,
    )
    return [SlotShortDB.model_validate(s) for s in slots]


@router.get(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_get_responses,
    summary='Получить временной слот по ID',
    response_description='Полная информация о слоте.',
)
async def get_time_slot(
    slot: Slot = Depends(visible_slot_for_user),
    _date: Optional[date] = Query(
        None,
        alias='date',
        description='Дата для контекстной проверки видимости слота.',
    ),
) -> SlotDB:
    """Получить слот по id (учитывая права и активность)."""
    return SlotDB.model_validate(slot)


@router.post(
    '',
    response_model=SlotDB,
    status_code=status.HTTP_201_CREATED,
    responses=slot_create_responses,
    summary='Создать новый временной слот',
    response_description='Созданный слот.',
)
async def create_time_slot(
    cafe_id: int = Path(..., description='ID кафе'),
    payload: SlotCreate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
) -> SlotDB:
    """Создать новый слот для кафе."""
    await cafe_existence(session, cafe_id)
    if payload.cafe_id != cafe_id:
        raise CafeIdMismatchException()
    obj = await slot_crud.create(payload, session, user=user)
    return SlotDB.model_validate(obj)


@router.patch(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_update_responses,
    summary='Частично обновить слот',
    response_description='Обновлённый слот.',
)
async def update_time_slot(
    slot: Slot = Depends(slot_in_cafe_exists),
    payload: SlotUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
) -> SlotDB:
    """Частично обновить слот (смена cafe_id запрещена)."""
    if payload.cafe_id is not None and payload.cafe_id != slot.cafe_id:
        raise CafeIdChangeForbiddenException()
    obj = await slot_crud.update(slot, payload, session, user=user)
    return SlotDB.model_validate(obj)


@router.delete(
    '/{time_slot_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses=slot_delete_responses,
    summary='Удалить (деактивировать) слот',
    response_description='Слот деактивирован, тело ответа отсутствует.',
)
async def delete_time_slot(
    slot: Slot = Depends(slot_in_cafe_exists),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
) -> Response:
    """Мягкое удаление слота: пометить как неактивный."""
    await slot_crud.delete_soft(slot, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
