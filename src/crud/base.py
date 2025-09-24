from typing import Any, Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import Base
from src.core.logger import log_event

ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD с логированием успешных и неуспешных операций."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализация CRUD с указанием модели."""
        self.model = model

    async def _check_unique(
        self,
        session: AsyncSession,
        model: Type[ModelType],
        current_obj: Optional[ModelType] = None,
        **fields: Any,
    ) -> None:
        """Проверка уникальности полей для любой модели через **kwargs."""
        for field_name, value in fields.items():
            if value is None:
                continue

            stmt = select(model).where(getattr(model, field_name) == value)
            result = await session.execute(stmt)
            existing = result.scalars().first()

            if existing and getattr(existing, 'id', None) != getattr(
                current_obj,
                'id',
                None,
            ):
                log_event(
                    'warning',
                    f'Попытка создать/обновить {model.__name__} '
                    f'с уже существующим {field_name}: {value}',
                    username=getattr(
                        current_obj,
                        'username',
                        settings.system_username,
                    ),
                    user_id=getattr(
                        current_obj,
                        'id',
                        settings.default_user_id,
                    ),
                )
                raise Exception(f'{field_name} {value} уже существует')

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

    async def get_active(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получение активных объектов по ID."""
        db_obj = await session.execute(
            select(self.model).where(
                and_(
                    self.model.id == obj_id,
                    self.model.is_active
                )
            ),
        )
        return db_obj.scalars().first()

    async def get_multi_all(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """Получение всех объектов."""
        db_objects = (await session.scalars(select(self.model))).all()
        log_event('info', 'Получено {} {}'.
                  format(len(db_objects), self.model.__name__))
        return db_objects

    async def get_multi_active(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """Получение только активных объектов."""
        db_objects = (await session.scalars(
            select(self.model).where(self.model.is_active),
        )).all()
        log_event('info', 'Получено {} активных {}'.
                  format(len(db_objects), self.model.__name__))
        return db_objects

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ModelType:
        """Создание объекта с логированием успешных и неуспешных попыток."""
        obj_in_data = obj_in.model_dump()
        if user_id is not None:
            obj_in_data['user_id'] = user_id

        try:
            db_obj = self.model(**obj_in_data)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)

            log_event(
                'info',
                f'Создан объект {self.model.__name__} id={db_obj.id} '
                f'с данными {obj_in_data}',
                username=(
                    settings.system_username
                    if not user_id
                    else f'user_{user_id}'
                ),
                user_id=user_id or settings.default_user_id,
            )
            return db_obj
        except Exception as error:
            log_event(
                'warning',
                'Не удалось создать объект'
                f'{self.model.__name__}: {str(error)}',
                username=(
                    settings.system_username
                    if not user_id
                    else f'user_{user_id}'
                ),
                user_id=user_id or settings.default_user_id,
            )
            raise

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ModelType:
        """Обновление объекта с логированием успешных и неуспешных попыток."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        try:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)

            log_event(
                'info',
                f'Обновлен объект {self.model.__name__} id={db_obj.id} '
                f'с данными {update_data}',
                username=(
                    settings.system_username
                    if not user_id
                    else f'user_{user_id}'
                ),
                user_id=user_id or settings.default_user_id,
            )
            return db_obj
        except Exception as error:
            log_event(
                'warning',
                'Не удалось обновить объект '
                f'{self.model.__name__} '
                f'id={getattr(db_obj, "id", None)}: {str(error)}',
                username=(
                    settings.system_username
                    if not user_id
                    else f'user_{user_id}'
                ),
                user_id=user_id or settings.default_user_id,
            )
            raise
