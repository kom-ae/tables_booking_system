from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import SYSTEM_USERNAME, ZERO_DEFAULT_USER_ID
from src.core.logger import log_event
from src.crud.base import CRUDBase
from src.exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services.auth import PasswordService


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для User с проверкой уникальности, хэш-ием пароля + логирование."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[User]:
        """По email или телефону."""
        query = select(User).where(or_(User.email == name, User.phone == name))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_or_404(self, obj_id: int, session: AsyncSession) -> User:
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

    async def _check_unique(
        self,
        session: AsyncSession,
        email: Optional[str],
        phone: Optional[str],
        tg_id: Optional[str] = None,
        current_user: Optional[User] = None,
    ) -> None:
        """Проверка уникальности email, телефона и tg_id с лог-ием попытки."""
        if email:
            existing: Optional[User] = await self.get_by_name(session, email)
            if existing and existing.id != getattr(current_user, 'id', None):
                log_event(
                    'warning',
                    'Попытка создать/обновить пользователя'
                    f'с уже существующим email: {email}',
                    username=getattr(
                        current_user,
                        'username',
                        SYSTEM_USERNAME,
                    ),
                    user_id=getattr(current_user, 'id', ZERO_DEFAULT_USER_ID),
                )
                raise UserAlreadyExistsException(
                    f'Email {email} уже существует',
                )

        if phone:
            existing: Optional[User] = await self.get_by_name(session, phone)
            if existing and existing.id != getattr(current_user, 'id', None):
                log_event(
                    'warning',
                    'Попытка создать/обновить пользователя'
                    f'с уже существующим телефоном: {phone}',
                    username=getattr(
                        current_user,
                        'username',
                        SYSTEM_USERNAME,
                    ),
                    user_id=getattr(current_user, 'id', ZERO_DEFAULT_USER_ID),
                )
                raise UserAlreadyExistsException(
                    f'Телефон {phone} уже существует',
                )

        if tg_id:
            result = await session.execute(
                select(User).where(User.tg_id == tg_id),
            )
            existing: Optional[User] = result.scalars().first()
            if existing and existing.id != getattr(current_user, 'id', None):
                log_event(
                    'warning',
                    'Попытка создать/обновить пользователя'
                    f'с уже существующим tg_id: {tg_id}',
                    username=getattr(
                        current_user,
                        'username',
                        SYSTEM_USERNAME,
                    ),
                    user_id=getattr(current_user, 'id', ZERO_DEFAULT_USER_ID),
                )
                raise UserAlreadyExistsException(
                    f'tg_id {tg_id} уже существует',
                )

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> User:
        """Создаёт нового пользователя с хэш-ем пароля и проверкой unique."""
        await self._check_unique(
            session,
            obj_in.email,
            obj_in.phone,
            obj_in.tg_id,
        )

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
        await self._check_unique(
            session,
            obj_in.email,
            obj_in.phone,
            tg_id=obj_in.tg_id,
            current_user=db_obj,
        )

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
        """Список пользователей с логированием действия."""
        stmt = select(User)
        if not show_all:
            stmt = stmt.where(User.is_active.is_(True))
        result = await session.execute(stmt)
        users = result.scalars().all()

        log_event(
            'info',
            f'Получен список пользователей, show_all={show_all}',
            username=(
                current_user.username if current_user else SYSTEM_USERNAME
            ),
            user_id=current_user.id if current_user else ZERO_DEFAULT_USER_ID,
        )
        return users
