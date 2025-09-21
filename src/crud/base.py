from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import SYSTEM_USERNAME, ZERO_DEFAULT_USER_ID
from src.core.db import Base
from src.core.logger import log_event

ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс CRUD моделей с логированием и автообновлением дат."""

    def __init__(self, model: ModelType) -> None:
        """Инициализация CRUD с указанием модели."""
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получение объекта по ID."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id),
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """Получение всех объектов."""
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ModelType:
        """Создание объекта с автоустановкой created_at/updated_at и лог-ем."""
        obj_in_data = obj_in.model_dump()
        if user_id is not None:
            obj_in_data['user_id'] = user_id

        now = datetime.now(timezone.utc)
        if (
            hasattr(self.model, 'created_at')
            and 'created_at' not in obj_in_data
        ):
            obj_in_data['created_at'] = now
        if (
            hasattr(self.model, 'updated_at')
            and 'updated_at' not in obj_in_data
        ):
            obj_in_data['updated_at'] = now

        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        log_event(
            'info',
            f'Создан объект {self.model.__name__}'
            f'id={db_obj.id} с данными {obj_in_data}',
            username=SYSTEM_USERNAME if not user_id else f'user_{user_id}',
            user_id=user_id or ZERO_DEFAULT_USER_ID,
        )
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ModelType:
        """Обновление объекта с автообновлением updated_at и логированием."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        if hasattr(db_obj, 'updated_at'):
            setattr(db_obj, 'updated_at', datetime.now(timezone.utc))

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        log_event(
            'info',
            f'Обновлен объект {self.model.__name__}'
            f'id={db_obj.id} с данными {update_data}',
            username=SYSTEM_USERNAME if not user_id else f'user_{user_id}',
            user_id=user_id or ZERO_DEFAULT_USER_ID,
        )
        return db_obj
