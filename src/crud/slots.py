from datetime import time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.exceptions.slots import SlotNotFoundException, SlotOverlapException
from src.models.slots import Slots
from src.schemas.slots import SlotCreate, SlotUpdate
from src.services.slot_rules import ensure_no_overlap


class CRUDSlot(CRUDBase[Slots, SlotCreate, SlotUpdate]):
    """CRUD для слотов бронирования (с проверкой пересечений)."""

    async def get_or_404(self, obj_id: int, session: AsyncSession) -> Slots:
        """Возвращает слот или кидает 404."""
        slot = await self.get(obj_id=obj_id, session=session)
        if not slot:
            raise SlotNotFoundException()
        return slot

    async def list_all(
        self,
        session: AsyncSession,
        *,
        cafe_id: Optional[int] = None,
    ) -> List[Slots]:
        """Возвращает все слоты, опционально по cafe_id."""
        stmt = select(Slots)
        if cafe_id is not None:
            stmt = stmt.where(Slots.cafe_id == cafe_id)
        stmt = stmt.order_by(Slots.cafe_id, Slots.start_time)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def list_active(
        self,
        session: AsyncSession,
        *,
        cafe_id: Optional[int] = None,
    ) -> List[Slots]:
        """Возвращает активные слоты, опционально по cafe_id."""
        stmt = select(Slots).where(Slots.is_active.is_(True))
        if cafe_id is not None:
            stmt = stmt.where(Slots.cafe_id == cafe_id)
        stmt = stmt.order_by(Slots.cafe_id, Slots.start_time)
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
        """Проверяет пересечения временных интервалов слотов."""
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
        user_id: Optional[int] = None,
    ) -> Slots:
        """Создаёт слот с валидацией границ и пересечений."""
        if obj_in.start_time >= obj_in.end_time:
            raise SlotOverlapException()
        will_be_active = getattr(obj_in, "is_active", True)
        if will_be_active:
            await self._check_overlap(
                session,
                cafe_id=obj_in.cafe_id,
                start_time=obj_in.start_time,
                end_time=obj_in.end_time,
            )
        db_obj = Slots(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: Slots,
        obj_in: SlotUpdate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> Slots:
        """Обновляет слот с валидацией пересечений."""
        data = obj_in.model_dump(exclude_unset=True)

        new_start = data.get("start_time", db_obj.start_time)
        new_end = data.get("end_time", db_obj.end_time)
        new_cafe_id = data.get("cafe_id", db_obj.cafe_id)
        will_be_active = bool(data.get("is_active", db_obj.is_active))

        if new_start >= new_end:
            raise SlotOverlapException()

        if will_be_active:
            await self._check_overlap(
                session,
                cafe_id=new_cafe_id,
                start_time=new_start,
                end_time=new_end,
                exclude_slot_id=db_obj.id,
            )

        for field, value in data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete_soft(
        self,
        db_obj: Slots,
        session: AsyncSession,
    ) -> None:
        """Мягко отметить слот как неактивный (soft delete)."""
        await session.execute(
            sa_update(Slots)
            .where(Slots.id == db_obj.id)
            .values(is_active=False),
        )
        await session.commit()
