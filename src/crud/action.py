from typing import Optional

from sqlalchemy import select, and_

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase

from src.models import User, Actions


class ActionsCRUD(CRUDBase):

    async def get_all_actions(
            self,
            session: AsyncSession,
            cafe_id: Optional[int] = None,
            show_all: bool = False,
            current_user: Optional[User] = None
    ) -> list[Actions]:
        conditions = []

        if cafe_id:
            conditions.append(Actions.cafe_id == cafe_id)

        is_admin_or_manager = current_user and (current_user.is_superuser or
                                                current_user.is_manager)

        if not is_admin_or_manager or not show_all:
            conditions.append(Actions.is_active)

        query = select(Actions).where(and_(*conditions))

        result = await session.execute(query)
        return result.scalars().all()


actions_crud = ActionsCRUD(Actions)
