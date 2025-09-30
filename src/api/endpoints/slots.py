from __future__ import annotations

from typing import List

from fastapi import APIRouter, Body, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.slots import (
    slot_create_responses,
    slot_delete_responses,
    slot_get_responses,
    slot_update_responses,
    slots_list_responses,
)
from src.api.validators import (
    cafe_exists,
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
from src.models.cafe import Cafe
from src.models.slot import Slot
from src.models.user import User
from src.schemas.slots import SlotCreate, SlotDB, SlotShortDB, SlotUpdate

router = APIRouter(prefix='/cafes/{cafe_id}/slots')
slot_crud = get_slot_crud()


@router.get(
        '',
        response_model=List[SlotShortDB],
        responses=slots_list_responses)
async def list_time_slots(
    cafe: Cafe = Depends(cafe_exists),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> List[SlotShortDB]:
    """Список слотов кафе.

    Админ/менеджер/суперпользователь видят все слоты,
    остальные — только активные.
    """
    if user.is_superuser or user.is_admin() or user.is_manager():
        slots = await slot_crud.list_all(session, cafe_id=cafe.id)
    else:
        slots = await slot_crud.list_active(session, cafe_id=cafe.id)
    return [SlotShortDB.model_validate(s) for s in slots]


@router.get(
        '/{time_slot_id}',
        response_model=SlotDB,
        responses=slot_get_responses)
async def get_time_slot(
    slot: Slot = Depends(visible_slot_for_user),
) -> SlotDB:
    """Получить слот по id (учитывая права и активность)."""
    return SlotDB.model_validate(slot)


@router.post(
    '',
    response_model=SlotDB,
    status_code=201,
    responses=slot_create_responses,
)
async def create_time_slot(
    cafe: Cafe = Depends(cafe_exists),
    payload: SlotCreate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
) -> SlotDB:
    """Создать новый слот для кафе."""
    if payload.cafe_id != cafe.id:
        raise CafeIdMismatchException()
    obj = await slot_crud.create(payload, session, user=user)
    return SlotDB.model_validate(obj)


@router.patch(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_update_responses,
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
)
async def delete_time_slot(
    slot: Slot = Depends(slot_in_cafe_exists),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
) -> Response:
    """Мягкое удаление слота: пометить как неактивный."""
    await slot_crud.delete_soft(slot, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
