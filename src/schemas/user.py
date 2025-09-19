from typing import Optional

from pydantic import EmailStr, Field, field_validator

from src.constants import MAX_LENGTH_USERNAME, MIN_LENGTH_USERNAME
from src.schemas.base import BaseSchema, UserBase
from src.schemas.validators import phone_validator


class UserCreate(UserBase):
    """Схема для создания нового пользователя."""

    password: str = Field(..., description='Пароль пользователя')
    username: str = Field(
        ...,
        description='Имя пользователя',
        min_length=MIN_LENGTH_USERNAME,
        max_length=MAX_LENGTH_USERNAME,
    )

    _validate_phone = field_validator('phone', mode='before')(phone_validator)


class UserRead(UserBase, BaseSchema):
    """Схема для чтения данных пользователя."""

    username: str = Field(
        ...,
        description='Имя пользователя',
        min_length=MIN_LENGTH_USERNAME,
        max_length=MAX_LENGTH_USERNAME,
    )


class UserUpdate(UserBase):
    """Схема для обновления данных пользователя."""

    username: Optional[str] = Field(
        None,
        description='Имя пользователя',
        min_length=MIN_LENGTH_USERNAME,
        max_length=MAX_LENGTH_USERNAME,
    )
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    _validate_phone = field_validator('phone', mode='before')(phone_validator)
