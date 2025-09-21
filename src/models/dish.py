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

from src.models.base import BaseModel
from src.models.cafes import Cafes

from src.constants import (
    DISH_PRICE_PRECISION,
    MAX_DISH_LENGTH_DESC,
    MAX_DISH_LENGTH_NAME,
)


class Dishes(BaseModel):
    """Модель блюд для кафе."""

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(MAX_DISH_LENGTH_NAME),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text(MAX_DISH_LENGTH_DESC),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(*DISH_PRICE_PRECISION),
        CheckConstraint('price >= 0'),
        nullable=False,
    )
    photo: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary(),
        nullable=True,
    )
    cafe: Mapped['Cafes'] = relationship('Cafes', back_populates='dishes')
