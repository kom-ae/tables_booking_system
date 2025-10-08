import asyncio
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
)

from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import Base
from src.core.logger import logger
from src.exceptions.db import DBException, DBIntegrityException

ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
OperationType = Callable[..., Awaitable[Any]]


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD с поддержкой retry и проверкой уникальности."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализация CRUD с моделью."""
        self.model: Type[ModelType] = model
        self._max_retries: int = settings.db_retry_max_attempts
        self._retry_delay: float = settings.db_retry_delay_seconds

    async def _execute_with_retry(
        self,
        operation: OperationType,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Выполнить операцию с retry при ошибках БД."""
        last_error: Optional[Exception] = None
        for attempt in range(self._max_retries):
            try:
                return await operation(*args, **kwargs)
            except (DBAPIError, SQLAlchemyError) as error:
                last_error = error
                if attempt == self._max_retries - 1:
                    break
                if (
                    'connection' in str(error).lower()
                    or 'timeout' in str(error).lower()
                ):
                    await asyncio.sleep(self._retry_delay * (2**attempt))
                    continue
                break
        raise last_error

    async def _commit(
        self,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> None:
        """Закоммитить сессию и обработать ошибки БД."""
        try:
            await session.commit()
        except IntegrityError as error:
            await session.rollback()
            msg: str = str(error.orig)
            logger.warning(f'Ошибка БД: {msg}', user=user)
            raise DBIntegrityException(msg)
        except SQLAlchemyError as error:
            await session.rollback()
            logger.error(f'Ошибка БД: {error}', user=user)
            raise DBException('Ошибка базы данных')
        except Exception as error:
            await session.rollback()
            logger.error(f'Неизвестная ошибка БД: {error}', user=user)
            raise DBException('Внутренняя ошибка базы данных')

    async def _check_unique(
        self,
        session: AsyncSession,
        current_obj: ModelType,
        user: Optional[Any] = None,
        model: Optional[Type[ModelType]] = None,
    ) -> None:
        """Проверка уникальности полей модели."""
        model = model or self.model

        for col in model.__table__.columns:
            if not col.unique:
                continue
            value: Any = getattr(current_obj, col.name, None)
            if value is None:
                continue

            stmt = (
                select(model).where(getattr(model, col.name) == value).limit(1)
            )
            result = await session.execute(stmt)
            exists: Optional[ModelType] = result.scalar_one_or_none()

            current_id: Optional[int] = getattr(current_obj, 'id', None)
            exists_id: Optional[int] = (
                getattr(exists, 'id', None) if exists else None
            )

            if exists and exists_id != current_id:
                logger.warning(
                    f'Дубликат {model.__name__}: {col.name}={value}',
                    user=user,
                )
                raise DBIntegrityException(
                    f"{col.name} '{value}' уже существует",
                )

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получить объект по ID."""
        return await self._execute_with_retry(self._get_impl, obj_id, session)

    async def _get_impl(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Внутренняя реализация получения объекта по ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id),
        )
        return result.scalars().first()

    async def get_multi_all(self, session: AsyncSession) -> List[ModelType]:
        """Получить все объекты."""
        return await self._execute_with_retry(
            self._get_multi_all_impl,
            session,
        )

    async def _get_multi_all_impl(
        self,
        session: AsyncSession,
    ) -> List[ModelType]:
        """Внутренняя реализация получения всех объектов."""
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def get_multi_active(self, session: AsyncSession) -> List[ModelType]:
        """Получить все активные объекты."""
        return await self._execute_with_retry(
            self._get_multi_active_impl,
            session,
        )

    async def _get_multi_active_impl(
        self,
        session: AsyncSession,
    ) -> List[ModelType]:
        """Внутренняя реализация получения активных объектов."""
        result = await session.execute(
            select(self.model).where(getattr(self.model, 'is_active', True)),
        )
        return result.scalars().all()

    async def get_active(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получить активный объект по ID."""
        return await self._execute_with_retry(
            self._get_active_impl,
            obj_id,
            session,
        )

    async def _get_active_impl(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Внутренняя реализация получения активного объекта по ID."""
        result = await session.execute(
            select(self.model).where(
                and_(
                    self.model.id == obj_id,
                    getattr(self.model, 'is_active', True),
                ),
            ),
        )
        return result.scalars().one_or_none()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> ModelType:
        """Создать новый объект."""
        return await self._execute_with_retry(
            self._create_impl,
            obj_in,
            session,
            user,
        )

    async def _create_impl(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> ModelType:
        """Внутренняя реализация создания объекта."""
        obj_in_data: Dict[str, Any] = obj_in.model_dump()
        logger.info(f'Создание {self.model.__name__}', user=user)
        try:
            db_obj: ModelType = self.model(**obj_in_data)

            await self._check_unique(session, db_obj, user)
            session.add(db_obj)

            await self._commit(session, user)
            await session.refresh(db_obj)
            return db_obj
        except (DBIntegrityException, DBException):
            await session.rollback()
            raise
        except Exception as error:
            await session.rollback()
            logger.error(
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
        return await self._execute_with_retry(
            self._update_impl,
            db_obj,
            obj_in,
            session,
            user,
        )

    async def _update_impl(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> ModelType:
        """Внутренняя реализация обновления объекта."""
        update_data: Dict[str, Any] = obj_in.model_dump(exclude_unset=True)
        obj_id: Optional[int] = getattr(db_obj, 'id', None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        try:
            session.add(db_obj)

            await self._check_unique(session, db_obj, user)

            await self._commit(session, user)
            await session.refresh(db_obj)

            logger.info(
                f'Обновлен {self.model.__name__} c id:{obj_id}',
                user=user,
            )
            return db_obj
        except (DBIntegrityException, DBException):
            await session.rollback()
            raise
        except Exception as error:
            await session.rollback()
            logger.error(
                f'Ошибка при обновлении {self.model.__name__} '
                f'id:{obj_id}: {error}',
                user=user,
            )
            raise DBException('Ошибка при обновлении объекта')
