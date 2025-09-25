from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.core.db import Base
from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.dish import Dishes
    from src.models.user import User


# Ассоциативная таблица кафе и менеджеров.
cafe_manager = Table(
    'cafe_manager',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True),
)


class Cafes(BaseModel):
    """Модель кафе."""

    __tablename__ = 'cafes'  # <-- ВАЖНО

    name: Mapped[str] = mapped_column(String(MAX_NAME_CAFE), nullable=False)
    address: Mapped[str] = mapped_column(String(MAX_ADDRESS), nullable=False)
    phone: Mapped[str] = mapped_column(String(MAX_TEL), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # менеджеры (многие-ко-многим c User)
    managers: Mapped[List['User']] = relationship(
        'User',
        secondary='cafe_manager',
        back_populates='managed_cafes',
        lazy='selectin',
    )

    # блюда (один-ко-многим)
    dishes: Mapped[List['Dishes']] = relationship(
        'Dishes',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    # слоты бронирования (один-ко-многим)
    slots = relationship(
        'Slots',
        back_populates='cafe',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
