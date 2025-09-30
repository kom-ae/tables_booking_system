from datetime import datetime
from typing import Optional

from src.schemas.cafes import CafeShortDB

from pydantic import BaseModel, Field

from src.constants import (
    MAX_DESCRIPTION,
    MIN_SEATS_NUMBER,
    MAX_SEATS_NUMBER,
)


class TableBase(BaseModel):
    """Базовая схема для стола."""

    seats_number: int = Field(
        ...,
        ge=MIN_SEATS_NUMBER,
        le=MAX_SEATS_NUMBER,
        title='Количество мест',
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION,
        title='Описание столика',
    )

    class Config:
        extra = 'forbid'


class TableCreate(TableBase):
    """Схема для создания стола."""

    pass


class TableUpdate(BaseModel):
    """Схема для обновления стола."""

    seats_number: Optional[int] = Field(
        None,
        ge=MIN_SEATS_NUMBER,
        le=MAX_SEATS_NUMBER,
        title='Количество мест'
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION,
        title='Описание столика',
    )
    is_active: Optional[bool] = Field(
        None,
        title='Стол активен?',
    )

    class Config:
        extra = 'forbid'


class TableDB(TableBase):
    """Схема стола из БД."""

    id: int = Field(..., title='ID записи')
    cafe: CafeShortDB = Field(..., title="Кафе")
    is_active: bool = Field(..., title='Стол активен?')
    created_at: datetime = Field(..., title='Дата создания')
    updated_at: datetime = Field(..., title='Дата обновления')

    class Config(TableBase.Config):
        from_attributes = True
