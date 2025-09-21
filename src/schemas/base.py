from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.constants import MAX_LENGTH_USERNAME, MIN_LENGTH_USERNAME
from src.schemas.validators import phone_validator


class BaseSchema(BaseModel):
    """Базовая схема с общими полями для всех моделей."""

    created_at: Optional[datetime] = Field(None, description='Дата создания')
    updated_at: Optional[datetime] = Field(None, description='Дата обновления')
    is_active: bool = Field(True, description='Активен ли пользователь.')

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    username: str = Field(
        ...,
        description='Имя пользователя.',
        min_length=MIN_LENGTH_USERNAME,
        max_length=MAX_LENGTH_USERNAME,
    )
    email: Optional[EmailStr] = Field(None, description='Email пользователя.')
    phone: Optional[str] = Field(None, description='Телефон.')
    tg_id: Optional[str] = Field(None, description='Telegram ID.')

    _validate_phone = field_validator('phone', mode='before')(phone_validator)


class Error(BaseModel):
    """Схема ошибки."""

    message: str
