"""Эндпоинты управления слотами бронирования кафе."""

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

from src.core.db import get_async_session
from src.models.cafes import Cafes
from src.models.user import User
from src.schemas.slots import SlotDB, SlotCreate, SlotUpdate
from src.crud.slots import slot_crud
from src.api.exceptions.slots import (
    SlotNotFoundException,
    SlotOverlapException,
    CafeOrSlotNotFoundException,
)
from src.api.utils.auth import get_current_user


router = APIRouter(
    prefix="/cafe/{cafe_id}/time_slots",
    tags=["slots"],
)


def ensure_role(user: User, allowed: set[str]) -> None:
    """Разрешает доступ суперу или ролям из множества allowed."""
    if user.is_superuser or user.role in allowed:
        return
    raise HTTPException(status_code=403, detail="Недостаточно прав")


@router.get("", response_model=List[SlotDB])
async def list_time_slots(
    cafe_id: int = Path(..., ge=1),
    date_: Optional[date] = Query(None, alias="date"),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Список слотов кафе. Пользователь видит только активные."""
    if not await session.get(Cafes, cafe_id):
        raise HTTPException(status_code=404, detail="Кафе не найдено")

    if user.is_superuser or user.role in {"admin", "manager"}:
        return await slot_crud.list_all(session, cafe_id=cafe_id)
    return await slot_crud.list_active(session, cafe_id=cafe_id)


@router.post("", response_model=SlotDB, status_code=status.HTTP_201_CREATED)
async def create_time_slot(
    cafe_id: int = Path(..., ge=1),
    payload: SlotCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Создаёт слот для кафе (admin/manager)."""
    ensure_role(user, {"admin", "manager"})

    if not await session.get(Cafes, cafe_id):
        raise HTTPException(status_code=404, detail="Кафе не найдено")

    if payload.cafe_id != cafe_id:
        raise HTTPException(
            status_code=400,
            detail="cafe_id в пути и теле должны совпадать",
        )

    try:
        return await slot_crud.create(obj_in=payload, session=session)
    except ValueError:
        raise SlotOverlapException()


@router.get("/{time_slot_id}", response_model=SlotDB)
async def get_time_slot(
    cafe_id: int = Path(..., ge=1),
    time_slot_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Возвращает слот по id, скрывая неактивные от user."""
    slot = await slot_crud.get(obj_id=time_slot_id, session=session)
    if not slot or slot.cafe_id != cafe_id:
        raise CafeOrSlotNotFoundException()

    if not (user.is_superuser or user.role in {"admin", "manager"}):
        if not slot.is_active:
            raise SlotNotFoundException()
    return slot


@router.patch("/{time_slot_id}", response_model=SlotDB)
async def update_time_slot(
    cafe_id: int = Path(..., ge=1),
    time_slot_id: int = Path(..., ge=1),
    payload: SlotUpdate = ...,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    ensure_role(user, {"admin", "manager"})

    slot = await slot_crud.get(obj_id=time_slot_id, session=session)
    if not slot or slot.cafe_id != cafe_id:
        raise CafeOrSlotNotFoundException()

    if payload.cafe_id is not None and payload.cafe_id != cafe_id:
        raise HTTPException(status_code=400, detail="cafe_id менять нельзя")

    try:
        return await slot_crud.update(db_obj=slot,
                                      obj_in=payload,
                                      session=session)
    except ValueError:
        raise SlotOverlapException()


@router.delete("/{time_slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_slot(
    cafe_id: int = Path(..., ge=1),
    time_slot_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    ensure_role(user, {"admin", "manager"})

    slot = await slot_crud.get(obj_id=time_slot_id, session=session)
    if not slot or slot.cafe_id != cafe_id:
        raise CafeOrSlotNotFoundException()

    await slot_crud.delete_soft(db_obj=slot, session=session)
