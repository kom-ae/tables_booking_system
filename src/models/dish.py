from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    LargeBinary,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel
from models.cafes import Cafes

from src.constants import (
    DISH_PRICE_PRECISSION,
    MAX_DISH_LENGTH_DESC,
    MAX_DISH_LENGTH_NAME,
)


class Dishes(BaseModel):
    """Модель блюд для кафе."""

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafes.id'),
        cascade='all, delete-orphan',
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(MAX_DISH_LENGTH_NAME),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text(MAX_DISH_LENGTH_DESC),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(*DISH_PRICE_PRECISSION),
        CheckConstraint('price >= 0'),
        nullable=False,
    )
    photo: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary(),
        nullable=True,
    )
    cafe: Mapped['Cafes'] = relationship('Cafes', back_populates='dishes')
