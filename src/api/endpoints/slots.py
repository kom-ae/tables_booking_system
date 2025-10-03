from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.slots import (
    slot_create_responses,
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
from src.core.logger import log_endpoint, logger
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
        'Получение списка временных слотов в кафе '
        '(только для администратора и менеджера, '
        'пользователь — только активные)'
    ),
    response_description='Список временных слотов',
)
@log_endpoint
async def list_time_slots(
    cafe: Cafe = Depends(cafe_exists_404_for_slots),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    q_date: Optional[date] = Query(
        None,
        alias='date',
        description='Фильтрация по дате (YYYY-MM-DD).',
    ),
) -> List[Slot]:
    """Получает список временных слотов в кафе."""
    show_all = True if user.is_manager() else False
    logger.info(
        f'{list_time_slots.__doc__} Cafe ID: {cafe.id}',
        user=user,
    )
    return await slot_crud.list(
        session,
        cafe_id=cafe.id,
        show_all=show_all,
        on_date=q_date,
    )


@router.get(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_get_responses,
    summary=(
        'Получение временного слота по ID '
        '(только для администратора и менеджера, '
        'пользователь — только активные)'
    ),
    response_description='Полная информация о временном слоте',
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
    """Получает временной слот в кафе по ID. (учитывая права и активность)."""
    logger.info(f'{get_time_slot.__doc__} ID: {slot.id}')
    return slot


@router.post(
    '',
    response_model=SlotDB,
    status_code=status.HTTP_201_CREATED,
    responses=slot_create_responses,
    summary=(
        'Создание временного слота в кафе '
        '(только для администратора и менеджера)'
    ),
    response_description='Данные созданного временного слота',
)
@log_endpoint
async def create_time_slot(
    cafe: Cafe = Depends(cafe_exists_404_for_slots),
    payload: SlotCreate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    _manager: User = Depends(current_manager),
) -> SlotDB:
    """Создаёт новый временной слот для кафе."""
    logger.info(
        f'{create_time_slot.__doc__} Данные',
        user=_manager,
        info_dict=payload,
    )
    return await slot_crud.create(payload, session, cafe_id=cafe.id)


@router.patch(
    '/{time_slot_id}',
    response_model=SlotDB,
    responses=slot_update_responses,
    summary=(
        'Обновление временного слота по ID '
        '(только для администратора и менеджера)'
    ),
    response_description='Обновлённый временный слот',
)
@log_endpoint
async def update_time_slot(
    slot: Slot = Depends(slot_in_cafe_exists),
    payload: SlotUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    _manager: User = Depends(current_manager),
) -> SlotDB:
    """Частично обновляет слот."""
    logger.info(
        f'{update_time_slot.__doc__} Данные',
        user=_manager,
        info_dict=payload,
    )
    return await slot_crud.update(slot, payload, session)
