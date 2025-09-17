from sqlalchemy import Column, String, Text

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.models.base import BaseModel


class Cafes(BaseModel):
    """Модель кафе."""

    name = Column(String(MAX_NAME_CAFE), nullable=False)
    address = Column(String(MAX_ADDRESS), nullable=False)
    phone = Column(String(MAX_TEL), nullable=False)
    description = Column(Text)
    photo = Column(String)
