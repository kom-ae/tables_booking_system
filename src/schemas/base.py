import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class BaseSchema(BaseModel):
    """Базовая схема с общими полями для всех моделей."""

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        """Настройки Pydantic для ORM совместимости."""

        orm_mode = True


class UserBase(BaseModel):
    """Базовая схема пользователя с email, телефоном и Telegram ID."""

    email: EmailStr = Field(..., description='Email пользователя')
    tg_id: Optional[str] = Field(None, description='Telegram ID пользователя')
    phone: Optional[str] = Field(
        None,
        description='Телефон пользователя в формате +7XXXXXXXXXX',
    )

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Валидатор телефона, проверяет формат номера."""
        if v is None:
            return v
        pattern = r'^(\+7|8)\d{10}$'
        if not re.fullmatch(pattern, v):
            raise ValueError('Некорректный номер телефона')
        return v
