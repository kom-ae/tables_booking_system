from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.base import BaseSchema, UserBase
from src.schemas.validators import password_validator, phone_validator


class UserCreate(UserBase):
    """Создание нового пользователя."""

    password: str = Field(..., description='Пароль')
    _validate_password = field_validator('password', mode='before')(
        password_validator,
    )


class UserRead(UserBase, BaseSchema):
    """Полная информация о пользователе (для ответа API)."""

    id: int = Field(..., description='ID')
    phone: str = Field(..., description='Телефон')
    email: EmailStr = Field(..., description='Email пользователя')
    is_active: bool = Field(..., description='Активен ли пользователь')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')


class UserUpdate(BaseModel):
    """Обновление пользователя."""

    username: Optional[str] = Field(None, description='Имя пользователя')
    email: Optional[EmailStr] = Field(None, description='Email пользователя')
    phone: Optional[str] = Field(None, description='Телефон')
    tg_id: Optional[str] = Field(None, description='Telegram ID')
    password: Optional[str] = Field(None, description='Пароль')
    is_active: Optional[bool] = Field(
        None,
        description='Активен ли пользователь',
    )

    _validate_phone = field_validator('phone', mode='before')(phone_validator)
    _validate_password = field_validator('password', mode='before')(
        password_validator,
    )


class UserShort(BaseModel):
    """Краткая информация о пользователе."""

    id: int
    username: str
    email: EmailStr
    phone: Optional[str] = None
    is_active: bool

    class Config:
        """Конфигурация Pydantic."""

        from_attributes = True
