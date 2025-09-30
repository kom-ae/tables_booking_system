from datetime import time
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.slot import Slot


async def ensure_no_overlap(
    session: AsyncSession,
    *,
    cafe_id: int,
    start_time: time,
    end_time: time,
    exclude_slot_id: Optional[int] = None,
) -> None:
    """Проверяет, что в рамках одного кафе нет пересечения интервалов."""
    if end_time <= start_time:
        raise ValueError('Время окончания должно быть позже времени начала')
    stmt = select(func.count(Slot.id)).where(
        and_(
            Slot.cafe_id == cafe_id,
            Slot.start_time < end_time,
            start_time < Slot.end_time,
            Slot.is_active.is_(True),
        ),
    )
    if exclude_slot_id is not None:
        stmt = stmt.where(Slot.id != exclude_slot_id)

    conflicts = await session.scalar(stmt)
    if conflicts and conflicts > 0:
        raise ValueError(
            'Интервал времени слота пересекается '
            'с существующим активным слотом',
        )
