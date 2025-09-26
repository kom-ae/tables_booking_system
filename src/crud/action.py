from typing import Optional
from http import HTTPStatus

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from src.crud.base import CRUDBase
from src.models import Actions, User
from src.schemas.action import ActionsCreate, ActionsDB, ActionsUpdate


class ActionsCRUD(CRUDBase):
    """CRUD-логика для Акций."""

    async def get_all_actions(
            self,
            session: AsyncSession,
            current_user: User,
            cafe_id: Optional[int] = None,
            show_all: bool | None = None,
    ) -> list[Actions]:
        """Получает все акции."""
        query = select(Actions)

        is_admin_is_manager = (current_user.is_admin() or
                               current_user.is_manager())

        if not is_admin_is_manager:
            query = query.where(Actions.is_active)

        if cafe_id is not None:
            query = query.where(Actions.cafe_id == cafe_id)

        if show_all is False:
            query = query.where(Actions.is_active)

        response = await session.execute(query)
        return response.scalars().all()

    async def get_action(
            self,
            session: AsyncSession,
            action_id: int,
            current_user: User
    ) -> Optional[Actions]:
        """Возвращает акция по его ID."""
        db_obj = select(Actions)

        is_admin_is_manager = (current_user.is_admin() or
                               current_user.is_manager())

        if not is_admin_is_manager:
            db_obj = db_obj.where(and_(
                Actions.id == action_id,
                Actions.is_active
            ))
        else:
            db_obj = db_obj.where(
                Actions.id == action_id
            )
        response = await session.execute(db_obj)

        return response.scalars().first()

    async def create_action(
        self,
        obj_in: ActionsCreate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ActionsDB:
        """Создает акцию."""
        obj_in_data = obj_in.model_dump()
        if user_id is not None:
            obj_in_data['user_id'] = user_id
        db_obj = self.model(**obj_in_data)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        result = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.cafe),
            )
            .where(self.model.id == db_obj.id),
        )
        db_obj_fully_loaded = result.scalar_one()
        return ActionsDB.model_validate(db_obj_fully_loaded)

    async def update_action(
            self,
            db_obj: Actions,
            obj_in: ActionsUpdate,
            session: AsyncSession,
    ) -> ActionsDB:
        """Обновляет акцию."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        result = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.cafe),
            )
            .where(self.model.id == db_obj.id),
        )
        db_obj_fully_loaded = result.scalar_one()
        return ActionsDB.model_validate(db_obj_fully_loaded)


actions_crud = ActionsCRUD(Actions)
