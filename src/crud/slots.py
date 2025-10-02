from __future__ import annotations

from datetime import time
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.exceptions.slots import SlotNotFoundException, SlotOverlapException
from src.models.slot import Slot
from src.schemas.slots import SlotCreate, SlotUpdate
from src.services.slot_rules import ensure_no_overlap


class CRUDSlot(CRUDBase[Slot, SlotCreate, SlotUpdate]):
    """CRUD для слотов бронирования (с проверкой пересечений)."""

    async def get_or_404(self, obj_id: int, session: AsyncSession) -> Slot:
        """Возвращает слот или кидает 404."""
        slot = await self.get(obj_id=obj_id, session=session)
        if not slot:
            raise SlotNotFoundException()
        return slot

    async def list(
        self,
        session: AsyncSession,
        *,
        cafe_id: int,
        only_active: bool,
    ) -> list[Slot]:
        """Список слотов по кафе с опциональной фильтрацией активности."""
        stmt = select(Slot).where(Slot.cafe_id == cafe_id)
        if only_active:
            stmt = stmt.where(Slot.is_active.is_(True))
        stmt = stmt.order_by(Slot.start_time.asc())
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def _check_overlap(
        self,
        session: AsyncSession,
        *,
        cafe_id: int,
        start_time: time,
        end_time: time,
        exclude_slot_id: Optional[int] = None,
    ) -> None:
        """Проверяет пересечение интервалов в рамках кафе.

        Бросает SlotOverlapException при наличии пересечений.
        """
        try:
            await ensure_no_overlap(
                session,
                cafe_id=cafe_id,
                start_time=start_time,
                end_time=end_time,
                exclude_slot_id=exclude_slot_id,
            )
        except ValueError:
            raise SlotOverlapException()

    async def create(
        self,
        obj_in: SlotCreate,
        session: AsyncSession,
        user: Any | None = None,
        **kwargs: Any,
    ) -> Slot:
        """Создаёт новый слот."""
        _ = user

        cafe_id = kwargs.get('cafe_id')
        if cafe_id is None:
            cafe_id = getattr(obj_in, 'cafe_id', None)
        if cafe_id is None:
            raise ValueError('Необходимо указать cafe_id для создания слота')

        if obj_in.start_time >= obj_in.end_time:
            raise SlotOverlapException()

        existing = (
            await session.execute(
                select(Slot).where(
                    Slot.cafe_id == cafe_id,
                    Slot.start_time == obj_in.start_time,
                    Slot.end_time == obj_in.end_time,
                ),
            )
        ).scalar_one_or_none()

        if existing is not None:
            data = obj_in.model_dump(exclude_unset=True)
            if 'description' in data:
                existing.description = data['description']
            if 'is_active' in data:
                existing.is_active = data['is_active']
            await session.commit()
            await session.refresh(existing)
            return existing

        data = obj_in.model_dump()
        data['cafe_id'] = cafe_id

        new_obj = Slot(**data)
        session.add(new_obj)
        await session.commit()
        await session.refresh(new_obj)
        return new_obj

    async def update(
        self,
        db_obj: Slot,
        obj_in: SlotUpdate,
        session: AsyncSession,
        user: Any | None = None,
    ) -> Slot:
        """Обновляет существующий слот (смена кафе не поддерживается)."""
        data = obj_in.model_dump(exclude_unset=True)

        new_start = data.get('start_time', db_obj.start_time)
        new_end = data.get('end_time', db_obj.end_time)
        new_is_active = data.get('is_active', db_obj.is_active)

        if new_start >= new_end:
            raise SlotOverlapException()

        if new_is_active:
            await self._check_overlap(
                session,
                cafe_id=db_obj.cafe_id,
                start_time=new_start,
                end_time=new_end,
                exclude_slot_id=db_obj.id,
            )

        return await super().update(db_obj, obj_in, session, user=user)

    async def delete_soft(self, db_obj: Slot, session: AsyncSession) -> None:
        """Мягко помечает слот как неактивный (soft delete)."""
        await session.execute(
            sa_update(Slot)
            .where(Slot.id == db_obj.id)
            .values(is_active=False),
        )
        await session.commit()
