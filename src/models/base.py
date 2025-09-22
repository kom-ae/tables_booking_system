from sqlalchemy import Boolean, Column, DateTime, func

from src.core.db import Base


class BaseModel(Base):
    """Базовая абстрактная модель."""

    __abstract__ = True
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
