import re
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions.user import (
    InvalidPhoneException,
    UserAlreadyExistsException,
)
from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate

PHONE_REGEX = r'^\+?\d{9,15}$'  # валидный формат телефона


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для модели User с проверками уникальности и формата."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[User]:
        """Возвращает пользователя по email или телефону."""
        query = select(User).where(or_(User.email == name, User.phone == name))
        result = await db.execute(query)
        return result.scalars().first()

    async def update_last_used(self, db: AsyncSession, user: User) -> User:
        """Обновляет поле last_used пользователя на текущее время UTC."""
        from datetime import datetime, timezone

        user.last_used = datetime.now(timezone.utc).timestamp()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> User:
        """Создает пользователя с проверкой уникальности и валидности тел."""
        if obj_in.phone and not re.match(PHONE_REGEX, obj_in.phone):
            raise InvalidPhoneException(
                f'Некорректный номер телефона: {obj_in.phone}',
            )

        # Проверка уникальности email и телефона
        existing_user = (
            await self.get_by_name(session, obj_in.email)
            if obj_in.email
            else None
        )
        if existing_user:
            raise UserAlreadyExistsException(
                f'Пользователь с email {obj_in.email} уже существует',
            )
        if obj_in.phone:
            existing_user = await self.get_by_name(session, obj_in.phone)
            if existing_user:
                raise UserAlreadyExistsException(
                    f'Пользователь с телефоном {obj_in.phone} уже существует',
                )

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
        """Обновляет пользователя с проверкой уникальности и валидности тел."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Валидация телефона
        phone = update_data.get('phone')
        if phone and not re.match(PHONE_REGEX, phone):
            raise InvalidPhoneException(
                f'Некорректный номер телефона: {phone}',
            )

        # Проверка уникальности email
        email = update_data.get('email')
        if email and email != db_obj.email:
            existing_user = await self.get_by_name(session, email)
            if existing_user:
                raise UserAlreadyExistsException(
                    f'Пользователь с email {email} уже существует',
                )

        # Проверка уникальности телефона
        if phone and phone != db_obj.phone:
            existing_user = await self.get_by_name(session, phone)
            if existing_user:
                raise UserAlreadyExistsException(
                    f'Пользователь с телефоном {phone} уже существует',
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
        """Возвращает список пользователей (с фильтром по активности)."""
        stmt = select(User)
        if not show_all:
            stmt = stmt.where(User.is_active)
        result = await session.execute(stmt)
        return result.scalars().all()


user_crud = CRUDUser(User)
