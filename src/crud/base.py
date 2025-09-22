from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import Base
from src.core.logger import log_event

ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD с логированием и корректным временем."""

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
        """Создание объекта с логированием и refresh для полей БД."""
        obj_in_data = obj_in.model_dump()
        if user_id is not None:
            obj_in_data['user_id'] = user_id

        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        log_event(
            'info',
            f'Создан объект {self.model.__name__} id={db_obj.id} '
            f'с данными {obj_in_data}',
            username=(
                settings.system_username if not user_id else f'user_{user_id}'
            ),
            user_id=user_id or settings.default_user_id,
        )
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ModelType:
        """Обновление объекта с логированием и refresh для полей БД."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        log_event(
            'info',
            f'Обновлен объект {self.model.__name__} id={db_obj.id} '
            f'с данными {update_data}',
            username=(
                settings.system_username if not user_id else f'user_{user_id}'
            ),
            user_id=user_id or settings.default_user_id,
        )
        return db_obj
