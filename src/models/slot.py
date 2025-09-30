from datetime import time
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import SLOT_DESCRIPTION_MAX_LENGTH
from src.models.base import BaseModel


class Slot(BaseModel):
    """Интервал бронирования в рамках конкретного кафе."""

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
    )
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        String(SLOT_DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    cafe = relationship('Cafe', back_populates='slots')

    __table_args__ = (
        UniqueConstraint(
            'cafe_id',
            'start_time',
            'end_time',
            name='uq_cafe_time_window',
        ),
        CheckConstraint(
            'start_time < end_time',
            name='ck_slot_start_before_end',
        ),
    )
