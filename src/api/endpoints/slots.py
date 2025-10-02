from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.slots import (
    slot_create_responses,
    slot_delete_responses,
    slot_get_responses,
    slot_update_responses,
    slots_list_responses,
)
from src.api.validators import (
    cafe_exists_404_for_slots,
    slot_in_cafe_exists,
    visible_slot_for_user,
)
from src.core.db import get_async_session
from src.core.dependencies import current_manager, current_user
from src.core.logger import log_endpoint
from src.crud.factory import get_slot_crud
from src.models.cafe import Cafe
from src.models.slot import Slot
from src.models.user import User
from src.schemas.slots import SlotCreate, SlotDB, SlotShortDB, SlotUpdate

router = APIRouter()
slot_crud = get_slot_crud()


@router.get(
    '',
    response_model=List[SlotShortDB],
    responses=slots_list_responses,
    summary=(
        'Список слотов. Менеджер/админ видят все; '
        'пользователь — только активные.'
    ),
    response_description='Список временных слотов',
)
@log_endpoint
async def list_time_slots(
    cafe: Cafe = Depends(cafe_exists_404_for_slots),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> List[SlotShortDB]:
    """Список слотов кафе."""
    show_all = user.is_manager() or user.is_admin()
    slots = await slot_crud.list(
        session,
        cafe_id=cafe.id,
        only_active=not show_all,
    )
    return [SlotShortDB.model_validate(s) for s in slots]


@router.get(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_get_responses,
    summary='Полная информация о слоте.',
    response_description='Получить временной слот по ID',
)
@log_endpoint
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
    summary='Созданный слот.',
    response_description='Создать новый временной слот',
)
@log_endpoint
async def create_time_slot(
    cafe: Cafe = Depends(cafe_exists_404_for_slots),
    payload: SlotCreate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    _manager: User = Depends(current_manager),
) -> SlotDB:
    """Создать новый слот для кафе."""
    obj = await slot_crud.create(payload, session, cafe_id=cafe.id)
    return SlotDB.model_validate(obj)


@router.patch(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_update_responses,
    summary='Обновлённый слот.',
    response_description='Частично обновить слот',
)
@log_endpoint
async def update_time_slot(
    slot: Slot = Depends(slot_in_cafe_exists),
    payload: SlotUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    _manager: User = Depends(current_manager),
) -> SlotDB:
    """Частично обновить слот (смена кафе не поддерживается)."""
    obj = await slot_crud.update(slot, payload, session)
    return SlotDB.model_validate(obj)


@router.delete(
    '/{time_slot_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses=slot_delete_responses,
    summary='Слот деактивирован, тело ответа отсутствует.',
    response_description='Удалить (деактивировать) слот',
)
@log_endpoint
async def delete_time_slot(
    slot: Slot = Depends(slot_in_cafe_exists),
    session: AsyncSession = Depends(get_async_session),
    _manager: User = Depends(current_manager),
) -> Response:
    """Мягкое удаление слота: пометить как неактивный."""
    await slot_crud.delete_soft(slot, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
