from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.cafes import CafeShort


class ActionsBase(BaseModel):
    """Базовая схема для акций."""
    id: int = Field(..., description='ID записи')
    cafe: CafeShort = Field(..., description='Кафе')
    description: str = Field(..., description='Описание акции')
    active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')


class ActionsCreate(BaseModel):
    """Сехма для создания акций."""

    cafe: CafeShort = Field(..., description='Кафе')
    description: str = Field(..., description='Описание акции')


class ActionsUpdate(ActionsCreate):
    """Схема для изменения акций."""

    cafe: CafeShort = Field(None, description='Кафе')
    description: str = Field(None, description='Описание акции')
    is_active: bool = Field(None, description='Объект активен?')


class Actions(ActionsBase):
    """Возвращаемая схема акций."""

    pass

    class Config:
        """Конфиг класса."""

        orm_mode = True
