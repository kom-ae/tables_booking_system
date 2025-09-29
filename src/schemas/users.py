from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.validators import (
    email_validator,
    password_validator,
    phone_validator,
    telegram_id_validator,
    username_validator,
)


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    username: str = Field(..., description='Имя пользователя.')
    email: Optional[EmailStr] = Field(None, description='Email пользователя.')
    phone: Optional[str] = Field(None, description='Телефон.')
    tg_id: Optional[str] = Field(None, description='Telegram ID.')


class UserCreate(UserBase):
    """Создание нового пользователя."""

    phone: str = Field(..., description='Телефон')
    password: str = Field(..., description='Пароль')

    _validate_password = field_validator('password', mode='before')(
        password_validator,
    )
    _validate_password = field_validator('password', mode='before')(
        password_validator,
    )
    _validate_phone = field_validator('phone', mode='before')(phone_validator)
    _validate_username = field_validator('username', mode='before')(
        username_validator,
    )
    _validate_email = field_validator('email', mode='before')(
        email_validator,
    )

    _validate_tg_id = field_validator('tg_id', mode='before')(
        telegram_id_validator,
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
    _validate_phone = field_validator('phone', mode='before')(phone_validator)
    _validate_username = field_validator('username', mode='before')(
        username_validator,
    )
    _validate_email = field_validator('email', mode='before')(
        email_validator,
    )

    _validate_tg_id = field_validator('tg_id', mode='before')(
        telegram_id_validator,
    )


class UserShort(BaseModel):
    """Краткая информация о пользователе."""

    id: int = Field(..., description='ID')
    username: str = Field(..., description='Имя пользователя')
    email: Optional[EmailStr] = Field(None, description='Email пользователя')
    phone: str = Field(..., description='Телефон')
    is_active: bool = Field(..., description='Активен ли пользователь')
