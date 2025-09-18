from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.schemas.cafes import CafeBase, CafeUpdate


class ActionsBase(BaseModel):
    """Базовая схема для акций."""

    cafe: CafeBase = Field(..., title='Кафе')
    description: str = Field(..., title='Описание акции')


class ActionsCreate(ActionsBase):
    """Схема для создания акций"""
    pass


class ActionsUpdate(ActionsBase):
    """Схема для изменения акций"""
    cafe: Optional[CafeUpdate] = Field(None, title='Кафе')
    description: Optional[str] = Field(None, title='Описание акции')


class ActionsDB(ActionsBase, BaseSchema):
    """Возвращаемая схема акций."""
    pass

    class Config:
        """Конфиг класса."""

        orm_mode = True
