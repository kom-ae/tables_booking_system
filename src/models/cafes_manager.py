from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class CafeManager(BaseModel):
    """Связь пользователя-менеджера с кафе."""

    __tablename__ = "cafe_managers"

    cafe_id: Mapped[int] = mapped_column(ForeignKey(
        "cafes.id",
        ondelete="CASCADE"),
        index=True,
        nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False)

    __table_args__ = (UniqueConstraint(
        "cafe_id",
        "user_id",
        name="uq_cafe_manager_pair"),)
