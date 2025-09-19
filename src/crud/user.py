from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions.user import (
    InvalidPhoneException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.validators import phone_validator


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для User с проверкой уникальности."""

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
        """Обновить last_used UTC."""
        from datetime import datetime, timezone

        user.last_used = datetime.now(timezone.utc).timestamp()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def _check_unique(
        self,
        session: AsyncSession,
        email: Optional[str],
        phone: Optional[str],
        current_user: Optional[User] = None,
    ) -> None:
        """Проверка уникальности email и телефона."""
        if email:
            existing: Optional[User] = await self.get_by_name(session, email)
            if existing and existing.id != getattr(current_user, 'id', None):
                raise UserAlreadyExistsException(
                    f'Email {email} уже существует',
                )
        if phone:
            existing: Optional[User] = await self.get_by_name(session, phone)
            if existing and existing.id != getattr(current_user, 'id', None):
                raise UserAlreadyExistsException(
                    f'Телефон {phone} уже существует',
                )

    def _validate_phone(self, phone: Optional[str]) -> None:
        """Валидировать телефон."""
        if phone and not phone_validator(phone):
            raise InvalidPhoneException(f'Некорректный телефон: {phone}')

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> User:
        """Создать пользователя."""
        self._validate_phone(obj_in.phone)
        await self._check_unique(session, obj_in.email, obj_in.phone)
        return await super().create(
            obj_in=obj_in,
            session=session,
            user_id=user_id,
        )

    async def update(
        self,
        db_obj: User,
        obj_in: UserUpdate,
        session: AsyncSession,
    ) -> User:
        """Обновить пользователя."""
        update_data = obj_in.model_dump(exclude_unset=True)
        self._validate_phone(update_data.get('phone'))
        await self._check_unique(
            session,
            update_data.get('email'),
            update_data.get('phone'),
            current_user=db_obj,
        )
        return await super().update(
            db_obj=db_obj,
            obj_in=obj_in,
            session=session,
        )

    async def get_users(
        self,
        session: AsyncSession,
        show_all: bool = False,
    ) -> List[User]:
        """Список пользователей."""
        stmt = select(User)
        if not show_all:
            stmt = stmt.where(User.is_active.is_(True))
        result = await session.execute(stmt)
        return result.scalars().all()


user_crud = CRUDUser(User)
