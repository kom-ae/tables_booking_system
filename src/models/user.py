from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    String,
    func,
    text,
)
from sqlalchemy import (
    Enum as EnumSQL,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import (
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    PHONE_REGEX,
    TG_ID_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_REGEX,
)
from src.core.config import settings
from src.models.base import BaseModel
from src.models.cafe import Cafe


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
        nullable=True,
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
    role: Mapped[UserRole] = mapped_column(
        EnumSQL(UserRole, name='user_role_enum'),
        default=UserRole.USER,
        nullable=False,
    )
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=func.now(),
        nullable=False,
    )
    managed_cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary='cafe_manager',
        back_populates='managers',
        lazy='selectin',
    )

    if settings.db_engine == 'postgres':
        __table_args__ = (
            CheckConstraint(
                f"username ~ '{USERNAME_REGEX.pattern}'",
                name='username_pattern',
            ),
            CheckConstraint(
                f"phone ~ '{PHONE_REGEX.pattern}'",
                name='phone_pattern',
            ),
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
