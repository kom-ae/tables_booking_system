from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import (
    BaseModel,
)  # наследуем BaseModel с id, created_at, updated_at, active


class User(BaseModel):
    """Кастомный класс пользователя."""

    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )
    tg_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50),
        default='user',
        nullable=False,
    )
    # cafe_id: Mapped[Optional[int]] = mapped_column(
    # Integer, ForeignKey("cafe.id"), nullable=True)
