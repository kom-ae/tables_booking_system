from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.core.db import Base
from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.action import Actions
    from src.models.dish import Dishe
    from src.models.user import User


cafe_manager = Table(
    'cafe_manager',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafe.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True),
)


class Cafe(BaseModel):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(String(MAX_NAME_CAFE), nullable=False)
    address: Mapped[str] = mapped_column(String(MAX_ADDRESS), nullable=False)
    phone: Mapped[str] = mapped_column(String(MAX_TEL), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    photo: Mapped[str] = mapped_column(Text)
    managers: Mapped[list['User']] = relationship(
        'User',
        secondary='cafe_manager',
        back_populates='managed_cafes',
        lazy='selectin',
    )
    dishes: Mapped[list['Dishe']] = relationship(
        'Dishe',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    actions: Mapped[list['Actions']] = relationship(
        'Actions',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    actions: Mapped[List['Actions']] = relationship(back_populates='cafe')
