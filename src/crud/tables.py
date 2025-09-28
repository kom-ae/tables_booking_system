from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.tables import Tables
from src.schemas.tables import TableCreate, TableUpdate


class CRUDTable(CRUDBase[Tables, TableCreate, TableUpdate]):
    """CRUD для столов."""

    async def get_tables_by_cafe_id(
        self,
        cafe_id: int,
        session: AsyncSession,
        only_active: bool = True,
    ) -> List[Tables]:
        """Список столов по ID кафе."""
        query = select(self.model).where(self.model.cafe_id == cafe_id)
        if only_active:
            query = query.where(self.model.is_active)
        result = await session.scalars(query)
        return list(result.all())

    async def create_table(
        self,
        cafe_id: int,
        obj_in: TableCreate,
        session: AsyncSession,
    ) -> Tables:
        """Создать стол в кафе."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(cafe_id=cafe_id, **obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_by_id_and_cafe(
        self,
        table_id: int,
        cafe_id: int,
        session: AsyncSession,
        only_active: bool = True,
    ) -> Optional[Tables]:
        """Получить стол по cafe_id и table_id."""
        query = select(self.model).where(
            and_(self.model.id == table_id, self.model.cafe_id == cafe_id)
        )
        if only_active:
            query = query.where(self.model.is_active)
        result = await session.scalars(query)
        return result.first()
