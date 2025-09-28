from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.core.db import Base
from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.action import Actions
    from src.models.dish import Dishes
    from src.models.user import User
    from src.models.tables import Tables


# Ассоциативная таблица кафе и менеджеров.
cafe_manager = Table(
    'cafe_manager',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True),
)


class Cafes(BaseModel):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(String(MAX_NAME_CAFE), nullable=False)
    address: Mapped[str] = mapped_column(String(MAX_ADDRESS), nullable=False)
    phone: Mapped[str] = mapped_column(String(MAX_TEL), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    photo: Mapped[str] = mapped_column(Text)
    managers: Mapped[List['User']] = relationship(
        'User',
        secondary='cafe_manager',
        back_populates='managed_cafes',
        lazy='selectin',
    )
    dishes: Mapped[List['Dishes']] = relationship(
        'Dishes',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    actions: Mapped[List['Actions']] = relationship(
        'Actions',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    tables: Mapped[List['Tables']] = relationship(
        'Tables',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
