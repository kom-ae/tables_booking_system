from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base import DishBase


class DishCreate(DishBase):
    """Схема для создания блюд."""

    price: Decimal = Field(
        ...,
        ge=Decimal('0'),
        description='Цена',
    )


class DishUpdate(BaseModel):
    """Схема для обновления блюд."""

    cafe_id: int | None = Field(None, description='Кафе')
    name: str | None = Field(None, description='Название блюда')
    description: str | None = Field(None, description='Описание акции')
    price: Decimal | None = Field(None, description='Цена')
    photo: str | None = Field(
        None,
        description='Фото блюда в формате base64',
    )
    is_active: bool | None = Field(None, description='Объект активен?')


class Dish(DishBase):
    """Схема блюд со всеми полями."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='ID записи')
    is_active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')
