import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import SLOT_DESCRIPTION_MAX_LENGTH
from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.cafe import Cafe


class Slot(BaseModel):
    """Интервал бронирования в рамках конкретного кафе."""

    __tablename__ = 'time_slot'

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
    )
    date: Mapped[datetime.date] = mapped_column(index=True, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        String(SLOT_DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='slots',
        lazy='selectin',
    )

    __table_args__ = (
        UniqueConstraint(
            'cafe_id', 'date', 'start_time', 'end_time',
            name='uq_cafe_date_time_window',
        ),
        CheckConstraint(
            'start_time < end_time',
            name='ck_slot_start_before_end',
        ),
        Index('ix_slot_cafe_date_start', 'cafe_id', 'date', 'start_time'),
    )
