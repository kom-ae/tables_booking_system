from sqlalchemy import Column, Text, Integer, ForeignKey

from src.models.base import BaseModel


class Actions(BaseModel):
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    cafe_id = Column(Integer, ForeignKey('cafe.id'))
