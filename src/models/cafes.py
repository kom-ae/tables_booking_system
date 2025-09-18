from typing import List

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import User
from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.core.db import Base
from src.models.base import BaseModel

# Ассоциативная таблица кафе и менеджеров.
cafe_manager = Table(
    'cafe_manager',
    Base.metadata,
    Column('case_id', ForeignKey('cafes.id')),
    Column('user_id', ForeignKey('user.id')),
)


class Cafes(BaseModel):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(String(MAX_NAME_CAFE), nullable=False)
    address: Mapped[str] = mapped_column(String(MAX_ADDRESS), nullable=False)
    phone: Mapped[str] = mapped_column(String(MAX_TEL), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    photo: Mapped[str] = mapped_column(String)
    users: Mapped[List[User]] = relationship(
        secondary='cafe_manager',
        # back_populates='cafes',
    )
