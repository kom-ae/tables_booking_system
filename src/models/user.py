from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import (
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    TG_ID_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from src.models import Cafes
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
    phone: Mapped[str] = mapped_column(
        String(PHONE_MAX_LENGTH),
        unique=True,
        nullable=False,
    )
    tg_id: Mapped[Optional[str]] = mapped_column(
        String(TG_ID_MAX_LENGTH),
        nullable=True,
        unique=True,
    )
    role: Mapped[str] = mapped_column(
        String(ROLE_MAX_LENGTH),
        default=UserRole.USER,
        nullable=False,
    )
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    managed_cafes: Mapped[List['Cafes']] = relationship(
        'Cafes',
        secondary='cafe_manager',
        back_populates='managers',
        lazy='selectin',
    )

    # -------------------
    # Методы проверки ролей
    # -------------------
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь администратором."""
        return self.role == UserRole.ADMIN.value

    def is_manager(self) -> bool:
        """Проверка, является ли пользователь менеджером или админином."""
        return self.role in (UserRole.MANAGER.value, UserRole.ADMIN.value)
