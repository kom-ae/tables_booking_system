from sqlalchemy import Boolean, Column, DateTime, func

from src.core.db import Base


class BaseModel(Base):
    """Базовая SQLAlchemy модель с общими полями."""

    __abstract__ = True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)
