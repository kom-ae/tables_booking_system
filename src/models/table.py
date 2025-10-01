from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MAX_DESCRIPTION, MAX_SEATS_NUMBER, MIN_SEATS_NUMBER
from src.models.base import BaseModel
from src.models.cafe import Cafe


class Table(BaseModel):
    """Модель столов."""

    __table_args__ = (
        CheckConstraint(
            f'seats_number >= {MIN_SEATS_NUMBER}',
            name='check_min_seats'),
        CheckConstraint(
            f'seats_number <= {MAX_SEATS_NUMBER}',
            name='check_max_seats'),
    )

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    seats_number: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        index=True,

    )
    description: Mapped[Optional[str]] = mapped_column(
        String(MAX_DESCRIPTION),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='tables',
        lazy='selectin',
    )

    def is_available(self) -> bool:
        """Проверка доступности стола."""
        return self.is_active

    def full_description(self) -> str:
        """Формирование описания стола."""
        parts = [
            f'Стол №{self.id}',
            f'({self.seats_number} мест)',
            self.description or 'Без описания',
        ]
        return ' - '.join(parts)
