from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import project_log
from src.crud.base import CRUDBase
from src.exceptions.user import UserNotFoundException
from src.models.user import User
from src.schemas.users import UserCreate, UserUpdate
from src.services.auth import PasswordService


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для User с человекочитаемыми ошибками."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[User]:
        """Получение пользователя по имени или телефону."""
        result = await db.execute(
            select(User).where(or_(User.email == name, User.phone == name)),
        )
        return result.scalars().first()

    async def get_user_id_or_404(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> User:
        """Получение пользователя по ID или 404."""
        user = await self.get(obj_id, session)
        if not user:
            project_log(
                'warning',
                f'Попытка получить несуществующего пользователя {obj_id}',
                user=None,
            )
            raise UserNotFoundException()
        return user

    async def update_last_used(self, db: AsyncSession, user: User) -> User:
        """Обновление времени последнего использования пользователя."""
        user.last_used = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        return user

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> User:
        """Создание нового пользователя."""
        hashed_password = PasswordService.hash_password(obj_in.password)
        obj_in_data = obj_in.model_copy(update={'password': hashed_password})
        try:
            return await super().create(
                obj_in=obj_in_data,
                session=session,
                user=user,
            )
        except Exception as error:
            project_log(
                'error',
                f'Ошибка при создании пользователя: {error}',
                user=user,
            )
            raise

    async def update(
        self,
        db_obj: User,
        obj_in: UserUpdate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> User:
        """Обновление данных пользователя."""
        update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get('password'):
            update_data['password'] = PasswordService.hash_password(
                update_data['password'],
            )
        try:
            return await super().update(
                db_obj=db_obj,
                obj_in=obj_in.model_copy(update=update_data),
                session=session,
                user=user,
            )
        except Exception as error:
            project_log(
                'error',
                f'Ошибка при обновлении пользователя {db_obj.id}: {error}',
                user=user,
            )
            raise

    async def get_users(
        self,
        session: AsyncSession,
        show_all: bool = False,
        user: Optional[User] = None,
    ) -> list[User]:
        """Возвращает список пользователей через базовый CRUD."""
        users: list[User]
        if show_all:
            users = await self.get_multi_all(session)
        else:
            users = await self.get_multi_active(session)

        project_log(
            'info',
            f'Получен список пользователей, show_all={show_all}',
            user=user,
        )
        return users
