from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.crud.base import CRUDBase
from src.exceptions.user import UserNotFoundException
from src.models.user import User
from src.schemas.users import UserCreate, UserUpdate
from src.services.auth import PasswordService


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для работы с пользователями."""

    async def get_by_name(
        self,
        session: AsyncSession,
        name: str,
    ) -> Optional[User]:
        """Получение пользователя по email или телефону."""
        result = await session.execute(
            select(User).where(or_(User.email == name, User.phone == name)),
        )
        return result.scalars().first()

    async def get_user_id_or_404(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> User:
        """Получение пользователя по ID или ошибка 404."""
        user = await self.get(obj_id, session)
        if not user:
            logger.warning(
                f'Попытка получить несуществующего пользователя {obj_id}',
                user=None,
            )
            raise UserNotFoundException()
        return user

    async def update_last_used(
        self,
        session: AsyncSession,
        user: User,
    ) -> User:
        """Обновление времени последнего использования пользователя."""
        user.last_used = datetime.now(timezone.utc)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> User:
        """Создание нового пользователя с хэшированием пароля."""
        hashed_password: str = PasswordService.hash_password(obj_in.password)
        obj_in_data: UserCreate = obj_in.model_copy(
            update={'password': hashed_password},
        )

        db_user: User = await super().create(
            obj_in=obj_in_data,
            session=session,
            user=user,
        )

        logger.info(
            f'Создан новый пользователь id={db_user.id}, '
            f'username={db_user.username}',
            user=user,
        )

        return db_user

    async def _update_impl(
        self,
        db_obj: User,
        obj_in: UserUpdate,
        session: AsyncSession,
        user: Optional[Any] = None,
    ) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'password' in update_data:
            update_data['password'] = PasswordService.hash_password(
                update_data['password'],
            )

        return await super()._update_impl(
            db_obj,
            obj_in.__class__(**update_data),
            session,
            user,
        )

    async def get_users(
        self,
        session: AsyncSession,
        show_all: bool = False,
        user: Optional[User] = None,
    ) -> List[User]:
        """Получение списка пользователей (активные или все)."""
        users: List[User]
        if show_all:
            users = await self.get_multi_all(session)
        else:
            users = await self.get_multi_active(session)

        logger.info(
            f'Получен список пользователей, show_all={show_all}',
            user=user,
        )
        return users
