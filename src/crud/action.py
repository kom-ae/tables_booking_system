from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Actions
from src.schemas.action import ActionsCreate, ActionsDB, ActionsUpdate


class ActionsCRUD(CRUDBase):
    """CRUD-логика для Акций."""

    async def get_all_actions(
            self,
            session: AsyncSession,
            cafe_id: Optional[int] = None,
            show_all: bool | None = None,
    ) -> list[Actions]:
        """Получает все акции."""
        query = select(Actions)

        if cafe_id is not None:
            query = query.where(Actions.cafe_id == cafe_id)

        if show_all is False:
            query = query.where(Actions.is_active)

        response = await session.execute(query)
        return response.scalars().all()

    async def get_all_active_actions(
        self,
        session: AsyncSession,
        cafe_id: Optional[int] = None,
    ) -> list[Actions]:
        """Получет акции для всех обычных пользователей."""
        query = select(Actions).where(Actions.is_active)
        if cafe_id is not None:
            query = query.where(Actions.cafe_id == cafe_id)

        response = await session.execute(query)
        return response.scalars().all()

    async def get_action(
            self,
            session: AsyncSession,
            action_id: int,
    ) -> Optional[Actions]:
        """Возвращает акция по его ID."""
        db_obj = await session.execute(
            select(Actions).where(Actions.id == action_id),
        )
        return db_obj.scalars().first()

    async def get_acive_action(
            self,
            session: AsyncSession,
            action_id: int,
    ) -> Optional[Actions]:
        """Возвращает только активне акции по ID."""
        db_obj = await session.execute(
            select(Actions).where(and_(
                Actions.id == action_id,
                Actions.is_active,
            )),
        )
        return db_obj.scalars().first()

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
