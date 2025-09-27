from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base
from src.core.logger import project_log
from src.exceptions.user import DBException, DBIntegrityException

ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD с логированием."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализация CRUD."""
        self.model = model

    async def _commit(
        self,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> None:
        """Коммит с обработкой ошибок."""
        try:
            await session.commit()
        except IntegrityError as error:
            await session.rollback()
            msg = str(error.orig)
            project_log('warning', f'Ошибка БД: {msg}', user=user)
            raise DBIntegrityException(msg)
        except SQLAlchemyError as error:
            await session.rollback()
            project_log('error', f'Ошибка БД: {error}', user=user)
            raise DBException('Ошибка базы данных')
        except Exception as error:
            await session.rollback()
            project_log('error', f'Неизвестная ошибка БД: {error}', user=user)
            raise DBException('Внутренняя ошибка базы данных')

    async def _check_unique(
        self,
        session: AsyncSession,
        model: Type[ModelType],
        current_obj: Optional[ModelType] = None,
        user: Optional[Any] = None,
        **fields: Any,
    ) -> None:
        """Проверка уникальности полей."""
        for field_name, value in fields.items():
            if value is None:
                continue
            exists = await session.scalar(
                model.__table__.select()
                .where(getattr(model, field_name) == value)
                .limit(1),
            )
            if exists and getattr(exists, 'id', None) != getattr(
                current_obj,
                'id',
                None,
            ):
                project_log(
                    'warning',
                    f'Дубликат {model.__name__}: {field_name}={value}',
                    user=user,
                )
                raise DBIntegrityException(
                    f"{field_name} '{value}' уже существует",
                )

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получить объект по id."""
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id),
        )
        return result.scalars().first()

    async def get_multi_all(self, session: AsyncSession) -> List[ModelType]:
        """Получить все объекты."""
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def get_multi_active(self, session: AsyncSession) -> List[ModelType]:
        """Получить все активные объекты."""
        result = await session.execute(
            select(self.model).where(getattr(self.model, 'is_active', True)),
        )
        return result.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> ModelType:
        """Создать объект."""
        obj_in_data = obj_in.model_dump()
        project_log('info', f'Создание {self.model.__name__}', user=user)
        try:
            db_obj = self.model(**obj_in_data)
            session.add(db_obj)
            await self._commit(session, user)
            await session.refresh(db_obj)
            project_log(
                'info',
                f'Создан {self.model.__name__} id={db_obj.id}',
                user=user,
            )
            return db_obj
        except DBIntegrityException:
            raise
        except Exception as error:
            project_log(
                'error',
                f'Ошибка при создании {self.model.__name__}: {error}',
                user=user,
            )
            raise DBException('Ошибка при создании объекта')

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> ModelType:
        """Обновить объект."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        try:
            session.add(db_obj)
            await self._commit(session, user)
            await session.refresh(db_obj)
            project_log(
                'info',
                f'Обновлён {self.model.__name__} id={db_obj.id}',
                user=user,
            )
            return db_obj
        except DBIntegrityException:
            raise
        except Exception as error:
            project_log(
                'error',
                f'Ошибка при обновлении {self.model.__name__} '
                f'id={getattr(db_obj, "id", None)}: {error}',
                user=user,
            )
            raise DBException('Ошибка при обновлении объекта')
