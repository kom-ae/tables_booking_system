from sqlalchemy import String, Text
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.models.base import BaseModel


class Cafes(BaseModel):
    """Модель кафе."""

    __tablename__ = "cafes"

    name: Mapped[str] = mapped_column(String(MAX_NAME_CAFE), nullable=False)
    address: Mapped[str] = mapped_column(String(MAX_ADDRESS), nullable=False)
    phone: Mapped[str] = mapped_column(String(MAX_TEL), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    photo: Mapped[str] = mapped_column(String)
    slots = relationship(
        "Slots", back_populates="cafe", cascade="all, delete-orphan"
    )
