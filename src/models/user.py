from enum import Enum
from typing import Optional

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.constants import (
    DEFAULT_LAST_USED,
    DEFAULT_ROLE,
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    TG_ID_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from src.models.base import BaseModel


class UserRole(str, Enum):
    """Роли пользователей."""

    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


class User(BaseModel):
    """Кастомный класс пользователя."""

    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH),
        unique=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(PASSWORD_MAX_LENGTH),
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(
        String(PHONE_MAX_LENGTH),
        unique=True,
        nullable=False,
    )
    tg_id: Mapped[Optional[str]] = mapped_column(
        String(TG_ID_MAX_LENGTH),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(
        String(ROLE_MAX_LENGTH),
        default=DEFAULT_ROLE,
        nullable=False,
    )
    last_used: Mapped[float] = mapped_column(Float, default=DEFAULT_LAST_USED)
    # cafe_id: Mapped[Optional[int]] = mapped_column(
    #    Integer, ForeignKey('cafe.id'), nullable=True)

    # -------------------
    # Методы проверки ролей
    # -------------------
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь администратором."""
        return self.role == UserRole.ADMIN.value

    def is_manager(self) -> bool:
        """Проверка, является ли пользователь менеджером или админином."""
        return self.role in (UserRole.MANAGER.value, UserRole.ADMIN.value)
