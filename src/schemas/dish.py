from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.constants import (
    MAX_DISH_LENGTH_DESC,
    MAX_DISH_LENGTH_NAME,
    MIN_PRICE_DISH,
)
from src.schemas.base import BaseSchema
from src.schemas.cafes import CafeShortDB


class DishBase(BaseSchema):
    """Базовая схема для блюд."""

    cafe: int = Field(..., description='ID Кафе')
    name: str = Field(
        ...,
        max_length=MAX_DISH_LENGTH_NAME,
        description='Название блюда',
    )
    description: str = Field(
        ...,
        max_length=MAX_DISH_LENGTH_DESC,
        description='Описание блюда',
    )
    price: Decimal | None = Field(None, description='Цена')
    photo: str | None = Field(
        None,
        description='Фото блюда в формате base64',
    )


class DishCreate(BaseModel):
    """Схема для создания блюд."""

    cafe: int = Field(..., description='ID Кафе')
    name: str = Field(
        ...,
        max_length=MAX_DISH_LENGTH_NAME,
        description='Название блюда',
    )
    description: str = Field(
        ...,
        max_length=MAX_DISH_LENGTH_DESC,
        description='Описание блюда',
    )
    price: Decimal = Field(
        ...,
        ge=Decimal(MIN_PRICE_DISH),
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
    description: str | None = Field(
        None,
        max_length=MAX_DISH_LENGTH_DESC,
        description='Описание блюда',
    )
    price: Decimal | None = Field(None, ge=MIN_PRICE_DISH, description='Цена')
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
