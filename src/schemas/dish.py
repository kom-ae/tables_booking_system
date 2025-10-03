from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base import BaseSchema
from src.schemas.cafes import CafeShortDB


class DishBase(BaseSchema):
    """Базовая схема для блюд."""

    cafe: int = Field(..., description='ID Кафе')
    name: str = Field(..., max_length=100, description='Название блюда')
    description: str = Field(..., description='Описание блюда')
    price: Decimal | None = Field(None, description='Цена')
    photo: str | None = Field(
        None,
        description='Фото блюда в формате base64',
    )


class DishCreate(BaseModel):
    """Схема для создания блюд."""

    cafe: int = Field(..., description='ID Кафе')
    name: str = Field(..., max_length=100, description='Название блюда')
    description: str = Field(..., description='Описание блюда')
    price: Decimal = Field(
        ...,
        ge=Decimal('0'),
        description='Цена',
    )
    photo: str | None = Field(
        None,
        description='Фото блюда в формате base64',
    )


class DishUpdate(BaseModel):
    """Схема для обновления блюд."""

    cafe: int | None = Field(None, description='Кафе')
    name: str | None = Field(None, description='Название блюда')
    description: str | None = Field(None, description='Описание акции')
    price: Decimal | None = Field(None, ge=0, description='Цена')
    photo: str | None = Field(
        None,
        description='Фото блюда в формате base64',
    )
    is_active: bool | None = Field(None, description='Объект активен?')


class Dish(DishBase):
    """Схема блюд со всеми полями."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='ID записи')
    cafe: CafeShortDB = Field(..., description='Кафе')
    is_active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')
