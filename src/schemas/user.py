from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.schemas.base import BaseSchema, UserBase


class UserCreate(UserBase):
    """Схема для создания нового пользователя."""

    password: str = Field(..., description='Пароль пользователя')
    username: str = Field(
        ...,
        description='Имя пользователя',
        min_length=1,
        max_length=40,
    )


class UserRead(UserBase, BaseSchema):
    """Схема для чтения данных пользователя."""

    username: str = Field(
        ...,
        description='Имя пользователя',
        min_length=1,
        max_length=40,
    )


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""

    email: Optional[EmailStr] = Field(
        None,
        description='Новый email пользователя',
    )
    phone: Optional[str] = Field(None, description='Новый номер телефона')
    tg_id: Optional[str] = Field(None, description='Новый Telegram ID')
    role: Optional[str] = Field(None, description='Новая роль пользователя')
    password: Optional[str] = Field(
        None,
        description='Новый пароль пользователя',
    )
    is_active: Optional[bool] = Field(
        True,
        description='Статус активности пользователя',
    )
