from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.base import UserBase
from src.schemas.validators import password_validator


class UserCreate(UserBase):
    """Создание нового пользователя."""

    phone: str = Field(..., description='Телефон')
    password: str = Field(..., description='Пароль')
    _validate_password = field_validator('password', mode='before')(
        password_validator,
    )


class UserRead(UserBase):
    """Полная информация о пользователе (для ответа API)."""

    id: int = Field(..., description='ID')
    phone: str = Field(..., description='Телефон')
    is_active: bool = Field(..., description='Активен ли пользователь')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')


class UserUpdate(UserBase):
    """Обновление пользователя."""

    username: Optional[str] = Field(None, description='Имя пользователя')
    password: Optional[str] = Field(None, description='Пароль')
    is_active: Optional[bool] = Field(
        None,
        description='Активен ли пользователь',
    )
    _validate_password = field_validator('password', mode='before')(
        password_validator,
    )


class UserShort(BaseModel):
    """Краткая информация о пользователе."""

    id: int = Field(..., description='ID')
    username: str = Field(..., description='Имя пользователя')
    email: Optional[EmailStr] = Field(None, description='Email пользователя')
    phone: str = Field(..., description='Телефон')
    is_active: bool = Field(
        ...,
        description='Активен ли пользователь',
    )

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True
