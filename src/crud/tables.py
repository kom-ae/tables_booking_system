from src.crud.base import CRUDBase
from src.models import Tables
from src.schemas.tables import TableCreate, TableUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select


class CRUDTable(CRUDBase[Tables, TableCreate, TableUpdate]):
    """CRUD для стола."""

    async def get_tables(
            self,
            session: AsyncSession,
            *,
            cafe_id: Optional[int] = None,
    ) -> List[Tables]:
        """Вернуть все столы по cafe_id."""

        stmt = select(Tables)
        if cafe_id is not None:
            stmt = stmt.where(Tables.cafe_id == cafe_id)
        stmt = stmt.order_by(Tables.cafe_id, Tables.seats_number)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    

    async def create_table(
            self,
            obj_in: TableCreate,
            session: AsyncSession,
            cafe_id: Optional[int]
    ):
        pass

    async def update_table(
            self,
    ):
        pass
