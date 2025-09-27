from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status
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
    require_admin_or_manager,
    slot_in_cafe_exists,
    visible_slot_for_user,
)
from src.constants import ID_MIN
from src.core.db import get_async_session
from src.core.logger import log_endpoint
from src.crud.factory import get_slot_crud
from src.crud.slots import CRUDSlot
from src.exceptions.slots import (
    CafeIdChangeForbiddenException,
    CafeIdMismatchException,
    SlotOverlapException,
)
from src.models.cafes import Cafes
from src.models.slots import Slots
from src.models.user import User
from src.schemas.slots import SlotCreate, SlotDB, SlotUpdate

router = APIRouter(
    prefix="/cafe/{cafe_id}/time_slots",
    tags=["slots"],
)

slot_crud: CRUDSlot = get_slot_crud()


@router.get(
    "",
    response_model=List[SlotDB],
    responses=slots_list_responses,
    summary="Список слотов кафе",
)
@log_endpoint("info")
async def list_time_slots(
    cafe: Cafes = Depends(cafe_exists),
    date_: Optional[date] = Query(
        None,
        alias="date",
        description="Дата (на будущее)",
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(),
) -> List[Slots]:
    """Список слотов кафе."""
    if user.is_superuser or user.role in {"admin", "manager"}:
        return await slot_crud.list_all(session, cafe_id=cafe.id)
    return await slot_crud.list_active(session, cafe_id=cafe.id)


@router.post(
    "",
    response_model=SlotDB,
    status_code=status.HTTP_201_CREATED,
    responses=slot_create_responses,
    summary="Создание слота (только админ/менеджер)",
)
@log_endpoint("info")
async def create_time_slot(
    cafe: Cafes = Depends(cafe_exists),
    payload: SlotCreate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(require_admin_or_manager),
) -> Slots:
    """Создаёт слот для кафе."""
    if payload.cafe_id != cafe.id:
        raise CafeIdMismatchException()
    try:
        return await slot_crud.create(obj_in=payload, session=session)
    except SlotOverlapException:
        raise
    except ValueError:
        raise SlotOverlapException()


@router.get(
    "/{time_slot_id}",
    response_model=SlotDB,
    responses=slot_get_responses,
    summary="Получение слота по ID",
)
@log_endpoint("info")
async def get_time_slot(
    slot: Slots = Depends(visible_slot_for_user),
) -> Slots:
    """Возвращает слот по ID."""
    return slot


@router.patch(
    "/{time_slot_id}",
    response_model=SlotDB,
    responses=slot_update_responses,
    summary="Обновление слота (только админ/менеджер)",
)
@log_endpoint("info")
async def update_time_slot(
    cafe_id: int = Path(..., ge=ID_MIN, description="ID кафе"),
    slot: Slots = Depends(slot_in_cafe_exists),
    payload: SlotUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(require_admin_or_manager),
) -> Slots:
    """Обновляет слот."""
    if payload.cafe_id is not None and payload.cafe_id != cafe_id:
        raise CafeIdChangeForbiddenException()

    try:
        return await slot_crud.update(
            db_obj=slot,
            obj_in=payload,
            session=session,
        )
    except SlotOverlapException:
        raise
    except ValueError:
        raise SlotOverlapException()


@router.delete(
    "/{time_slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=slot_delete_responses,
    summary="Удаление слота (мягкая деактивация)",
)
@log_endpoint("info")
async def delete_time_slot(
    slot: Slots = Depends(slot_in_cafe_exists),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(require_admin_or_manager),
) -> None:
    """Мягко помечает слот как неактивный."""
    await slot_crud.delete_soft(db_obj=slot, session=session)
