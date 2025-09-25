from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logger import log_event
from src.crud.base import CRUDBase
from src.exceptions.user import (
    UserAlreadyExistsException,
    UserException,
    UserNotFoundException,
)
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services.auth import PasswordService


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для User с проверкой уникальности, хэш-ем пароля + логирование."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[User]:
        """По email или телефону."""
        query = select(User).where(or_(User.email == name, User.phone == name))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_id_or_404(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> User:
        """По ID или UserNotFoundException."""
        obj = await self.get(obj_id, session)
        if not obj:
            raise UserNotFoundException()
        return obj

    async def update_last_used(self, db: AsyncSession, user: User) -> User:
        """Обновляет поле last_used для пользователя."""
        user.last_used = func.now()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        log_event(
            'info',
            f'Обновлено поле last_used для пользователя {user.id}',
            username=user.username,
            user_id=user.id,
        )
        return user

    async def touch_last_used(self, db: AsyncSession, user: User) -> None:
        """Обновляет поле last_used при активности пользователя."""
        user.last_used = func.now()
        db.add(user)
        await db.commit()

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> User:
        """Создает нового юзера с проверкой уникальности и хэш-ем пароля."""
        try:
            await self._check_unique(
                session,
                model=User,
                email=obj_in.email,
                phone=obj_in.phone,
                tg_id=obj_in.tg_id,
                current_obj=None,
            )
        except Exception as error:
            log_event(
                'warning',
                f'Неудачная попытка создать пользователя: {str(error)}',
                username=getattr(obj_in, 'username', 'system'),
                user_id=getattr(obj_in, 'id', settings.default_user_id),
            )
            raise UserAlreadyExistsException(str(error))

        hashed_password = PasswordService.hash_password(obj_in.password)
        obj_in_data = obj_in.model_copy(update={'password': hashed_password})

        return await super().create(
            obj_in=obj_in_data,
            session=session,
            user_id=user_id,
        )

    async def update(
        self,
        db_obj: User,
        obj_in: UserUpdate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> User:
        """Обновляет пользователя с проверкой уникальности и хэш-ем пароля."""
        try:
            await self._check_unique(
                session,
                model=User,
                email=obj_in.email,
                phone=obj_in.phone,
                tg_id=obj_in.tg_id,
                current_obj=db_obj,
            )
        except Exception as error:
            log_event(
                'warning',
                'Неудачная попытка обновить пользователя '
                f'{db_obj.id}: {str(error)}',
                username=getattr(db_obj, 'username', 'system'),
                user_id=getattr(db_obj, 'id', settings.default_user_id),
            )
            raise UserAlreadyExistsException(str(error))

        update_data = obj_in.model_dump(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['password'] = PasswordService.hash_password(
                update_data['password'],
            )

        return await super().update(
            db_obj=db_obj,
            obj_in=obj_in.model_copy(update=update_data),
            session=session,
            user_id=user_id,
        )

    async def get_users(
        self,
        session: AsyncSession,
        show_all: bool = False,
        current_user: Optional[User] = None,
    ) -> list[User]:
        """Возвращает список пользователей."""
        try:
            stmt = select(User)
            if not show_all:
                stmt = stmt.where(User.is_active.is_(True))

            result = await session.execute(stmt)
            users = result.scalars().all()

            log_event(
                'info',
                f'Получен список пользователей, show_all={show_all}',
                username=getattr(
                    current_user,
                    'username',
                    settings.system_username,
                ),
                user_id=getattr(current_user, 'id', settings.default_user_id),
            )
            return users

        except Exception as error:
            log_event(
                'error',
                f'Ошибка при получении списка пользователей: {str(error)}',
                username=getattr(
                    current_user,
                    'username',
                    settings.system_username,
                ),
                user_id=getattr(current_user, 'id', settings.default_user_id),
            )
            raise UserException('Не удалось получить список пользователей')
