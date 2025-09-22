from datetime import time
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.slots import Slots


async def ensure_no_overlap(
    session: AsyncSession,
    *,
    cafe_id: int,
    start_time: time,
    end_time: time,
    exclude_slot_id: Optional[int] = None,
) -> None:
    """
    Проверяет, что в рамках одного кафе нет пересечения интервалов.
    """
    stmt = (
        select(func.count(Slots.id))
        .where(
            and_(
                Slots.cafe_id == cafe_id,
                Slots.start_time < end_time,
                start_time < Slots.end_time,
                Slots.is_active.is_(True),
            )
        )
    )
    if exclude_slot_id:
        stmt = stmt.where(Slots.id != exclude_slot_id)

    conflicts = await session.scalar(stmt)
    if conflicts and conflicts > 0:
        raise ValueError(
            "Интервал времени слота пересекается "
            "с существующим активным слотом"
            )
