from sqlalchemy import Column, String, Text, URL

from src.models.base import BaseModel


class Cafes(BaseModel):
    """Модель кафе."""

    name = Column(String(256), nullable=False)
    address = Column(String(256), nullable=False)
    phone = Column(String(16), nullable=False)
    description = Column(Text)
    photo = Column(URL)
