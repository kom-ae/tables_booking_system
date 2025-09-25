from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.cafes import CafeShortDB


class ActionsCreate(BaseModel):
    """Сехма для создания акций."""

    cafe_id: int = Field(..., description='ID Кафе')
    description: str = Field(..., description='Описание акции')


class ActionsUpdate(ActionsCreate):
    """Схема для изменения акций."""

    cafe_id: int = Field(None, description='ID Кафе')
    description: str = Field(None, description='Описание акции')
    is_active: bool = Field(None, description='Объект активен?')


class ActionsDB(BaseModel):
    """Возвращаемая схема акций."""

    id: int = Field(..., description='ID записи')
    cafe: CafeShortDB = Field(..., description='Кафе')
    description: str = Field(..., description='Описание акции')
    is_active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    class Config:
        """Конфиг класса."""

        from_attributes = True
