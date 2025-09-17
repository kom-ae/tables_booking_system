from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class Actions(BaseModel):
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cafe_id: Mapped[int] = mapped_column(Integer, ForeignKey('cafes.id'))
