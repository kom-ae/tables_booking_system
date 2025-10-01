from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.table import Table
from src.schemas.table import TableCreate, TableUpdate


class CRUDTable(CRUDBase[Table, TableCreate, TableUpdate]):
    """CRUD для столов."""

    async def get_by_id_and_cafe(
        self,
        table_id: Optional[int] = None,
        cafe_id: Optional[int] = None,
        session: AsyncSession = None,
        only_active: bool = True,
    ) -> Optional[Table] | List[Table]:
        """Получить стол по cafe_id и table_id."""
        query = select(self.model)
        conditions = []
        if table_id is not None:
            conditions.append(self.model.id == table_id)
        if cafe_id is not None:
            conditions.append(self.model.cafe_id == cafe_id)
        if conditions:
            query = query.where(and_(*conditions))
        if only_active:
            query = query.where(self.model.is_active)
        result = await session.scalars(query)
        if table_id is not None:
            return result.first()
        else:
            return result.all()

    async def get_tables_by_cafe_id(
        self,
        cafe_id: int,
        session: AsyncSession,
        only_active: bool = True,
    ) -> List[Table]:
        """Список столов по ID кафе."""
        return await self.get_by_id_and_cafe(
            table_id=None,
            cafe_id=cafe_id,
            session=session,
            only_active=only_active,
        )

    async def create_table(
        self,
        cafe_id: int,
        obj_in: TableCreate,
        session: AsyncSession,
    ) -> Table:
        """Создать стол в кафе."""
        obj_data = obj_in.model_dump()
        db_obj = Table(**obj_data, cafe_id=cafe_id)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update_table(
        self,
        table: Table,
        obj_in: TableUpdate,
        session: AsyncSession,
    ) -> Table:
        """Обновить стол."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(table, field, value)
        session.add(table)
        await session.commit()
        await session.refresh(table)
        return table
