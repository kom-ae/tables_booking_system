from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.cafes import CafeShortDB


class DishBase(BaseModel):
    """Базовая схема для блюд."""

    cafe: int = Field(..., description='ID записи')
    name: str = Field(..., description='Название блюда')
    description: str = Field(..., description='Описание акции')
    price: Decimal | None = Field(None, description='Цена')
    photo: bytes | None = Field(
        None,
        description='Фото блюда в формате base64',
    )


class DishCreate(DishBase):
    """Схема для создания блюд."""

    price: Decimal = Field(
        ...,
        ge=Decimal('0'),
        description='Цена',
    )


class DishUpdate(DishBase):
    """Схема для обновления блюд."""

    cafe: int | None = Field(None, description='ID записи')
    name: str | None = Field(None, description='Название блюда')
    description: str | None = Field(None, description='Описание акции')
    is_active: bool | None = Field(None, description='Объект активен?')


class Dish(DishBase):
    """Схема блюд со всеми полями и полной информацией о кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='ID записи')
    cafe: CafeShortDB = Field(..., description='Кафе')
    is_active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')
