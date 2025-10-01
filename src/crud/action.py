from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Action, User
from src.schemas.action import ActionCreate, ActionDB, ActionUpdate


class ActionsCRUD(CRUDBase):
    """CRUD-логика для Акций."""

    async def get_all_actions(
            self,
            session: AsyncSession,
            current_user: User,
            cafe_id: Optional[int] = None,
            show_all: bool | None = None,
    ) -> list[Action]:
        """Получает все акции."""
        query = select(Action)

        is_admin_is_manager = (current_user.is_admin() or
                               current_user.is_manager())

        if cafe_id is not None:
            query = query.where(Action.cafe_id == cafe_id)

        if not (is_admin_is_manager and show_all):
            query = query.where(Action.is_active)

        response = await session.execute(query)
        return response.scalars().all()

    async def get_action(
            self,
            session: AsyncSession,
            action_id: int,
            current_user: User,
    ) -> Optional[Action]:
        """Возвращает акция по его ID."""
        db_obj = select(Action)

        is_admin_is_manager = (current_user.is_admin() or
                               current_user.is_manager())

        if not is_admin_is_manager:
            db_obj = db_obj.where(and_(
                Action.id == action_id,
                Action.is_active,
            ))
        else:
            db_obj = db_obj.where(
                Action.id == action_id,
            )
        response = await session.execute(db_obj)

        return response.scalars().first()

    async def create_action(
        self,
        obj_in: ActionCreate,
        session: AsyncSession,
        user_id: Optional[int] = None,
    ) -> ActionDB:
        """Создает акцию."""
        obj_in_data = obj_in.model_dump()
        cafe_id = obj_in.cafe

        if user_id is not None:
            obj_in_data['user_id'] = user_id

        if 'cafe' in obj_in_data:
            del obj_in_data['cafe']

        obj_in_data['cafe_id'] = cafe_id

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
        return ActionDB.model_validate(db_obj_fully_loaded)

    async def update_action(
            self,
            db_obj: Action,
            obj_in: ActionUpdate,
            session: AsyncSession,
    ) -> ActionDB:
        """Обновляет акцию."""
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'cafe' in update_data:
            cafe_id = update_data['cafe']

            del update_data['cafe']
            update_data['cafe_id'] = cafe_id

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
        return ActionDB.model_validate(db_obj_fully_loaded)


actions_crud = ActionsCRUD(Action)
