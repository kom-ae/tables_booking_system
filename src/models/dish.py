from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import (
    DISH_PRICE_PRECISION,
    MAX_DISH_LENGTH_DESC,
    MAX_DISH_LENGTH_NAME,
)
from src.models.base import BaseModel
from src.models.cafe import Cafe


class Dishe(BaseModel):
    """Модель блюд для кафе."""

    name: Mapped[str] = mapped_column(
        String(MAX_DISH_LENGTH_NAME),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        String(MAX_DISH_LENGTH_DESC),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(*DISH_PRICE_PRECISION),
        CheckConstraint('price >= 0'),
        nullable=False,
    )
    photo: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='dishes',
        lazy='selectin',
    )
