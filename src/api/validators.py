from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_user
from src.models.cafes import Cafes
from src.models.slots import Slots
from src.models.user import User
from src.exceptions.slots import (
    CafeOrSlotNotFoundException,
    SlotNotFoundException,
)


async def cafe_exists(
    cafe_id: int = Path(..., ge=1, description='ID кафе'),
    session: AsyncSession = Depends(get_async_session),
) -> Cafes:
    """Возвращает кафе или кидает 404, если не найдено."""
    cafe = await session.get(Cafes, cafe_id)
    if not cafe:
        raise CafeOrSlotNotFoundException()
    return cafe


def require_admin_or_manager(
    user: User = Depends(current_user),
) -> User:
    """
    Пропускает суперпользователя и роли admin/manager.
    Иначе кидает 403.
    """
    if user.is_superuser or user.role in {'admin', 'manager'}:
        return user
    raise HTTPException(status_code=403, detail='Недостаточно прав')


async def slot_in_cafe_exists(
    cafe_id: int = Path(..., ge=1, description='ID кафе'),
    time_slot_id: int = Path(..., ge=1, description='ID слота'),
    session: AsyncSession = Depends(get_async_session),
) -> Slots:
    """
    Возвращает слот по id, принадлежащий cafe_id.
    Кидает 404, если слота нет или он относится к другому кафе.
    """
    slot = await session.get(Slots, time_slot_id)
    if not slot or slot.cafe_id != cafe_id:
        raise CafeOrSlotNotFoundException()
    return slot


async def visible_slot_for_user(
    slot: Slots = Depends(slot_in_cafe_exists),
    user: User = Depends(current_user),
) -> Slots:
    """
    Возвращает слот, скрывая неактивные слоты от обычных пользователей:
    - admin/manager/superuser видят любой слот;
    - прочим 404, если слот не активен.
    """
    if user.is_superuser or user.role in {'admin', 'manager'}:
        return slot
    if not slot.is_active:
        raise SlotNotFoundException()
    return slot
