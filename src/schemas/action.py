from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema
from src.schemas.cafes import CafeBase, CafeUpdate, CafeDB, CafeCreate


class ActionsBase(BaseModel):
    """Базовая схема для акций."""
    id: int = Field(...)
    cafe: CafeDB = Field(..., description='Кафе')
    description: str = Field(..., description='Описание акции')
    active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')


class ActionsCreate(BaseModel):

    cafe: CafeCreate = Field(..., description='Кафе')
    description: str = Field(..., description='Описание акции')


class ActionsUpdate(ActionsCreate):
    """Схема для изменения акций."""

    cafe: CafeBase = Field(None, description='Кафе')
    description: str = Field(None, description='Описание акции')
    is_active: bool = Field(None, description='Объект активен?')


class Actions(ActionsBase):
    """Возвращаемая схема акций."""

    pass

    class Config:
        """Конфиг класса."""

        orm_mode = True
