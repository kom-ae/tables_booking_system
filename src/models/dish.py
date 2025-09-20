from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel
from models.cafes import Cafes


class Dishes(BaseModel):
    """Модель блюд для кафе."""

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafes.id'),
        cascade='all, delete-orphan',
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        CheckConstraint('price >= 0'),
        nullable=False,
    )
    photo: Mapped[str] = mapped_column(String(500), nullable=True)
    cafe: Mapped['Cafes'] = relationship('Cafes', back_populates='dishes')
