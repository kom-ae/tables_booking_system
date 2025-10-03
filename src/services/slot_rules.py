from datetime import date, time
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.slot import Slot


async def ensure_no_overlap(
    session: AsyncSession,
    *,
    cafe_id: int,
    date_: date,
    start_time: time,
    end_time: time,
    exclude_slot_id: Optional[int] = None,
) -> None:
    """Проверяет, что в рамках одного кафе нет пересечения интервалов."""
    if end_time <= start_time:
        raise ValueError('Время окончания должно быть позже времени начала')
    stmt = select(Slot).where(
        Slot.cafe_id == cafe_id,
        Slot.date == date_,
        Slot.is_active.is_(True),
        ~((Slot.end_time <= start_time) | (Slot.start_time >= end_time)),
    )

    res = await session.execute(stmt)
    if res.scalars().first() is not None:
        raise ValueError('overlap')
