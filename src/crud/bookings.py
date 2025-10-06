from datetime import datetime
from typing import List, Optional

import asyncio
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.logger import logger
from src.crud.base import CRUDBase
from src.exceptions.bookings import (
    BookingNotFoundException,
    BookingDateException,
    BookingOverlapException,
    BookingResourceNotFoundException,
    BookingUpdateForbiddenException,
)
from src.exceptions.db import AppException, DBException, DBIntegrityException
from src.models import Booking, Cafe, Slot, Table, Dishe, User
from src.models.booking import booking_slot
from src.schemas.bookings import BookingCreate, BookingUpdate, BookingStatus


class CRUDBooking(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    """CRUD для бронирований."""

    async def get_booking_id_or_404(
        self,
        booking_id: int,
        session: AsyncSession,
    ) -> Booking:
        """Получение бронирования по ID или ошибка 404."""
        booking = await self.get(booking_id, session)
        if not booking:
            logger.warning(f'Бронирование id={booking_id} не найдено')
            raise BookingNotFoundException()
        return booking

    async def get_bookings(
        self,
        session: AsyncSession,
        *,
        show_all: bool = False,
        cafe_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> List[Booking]:
        """Получение списка бронирований."""
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.cafe),
                selectinload(Booking.tables),
                selectinload(Booking.slots),
                selectinload(Booking.menu),
            )
            .order_by(Booking.created_at.desc())
        )
        filter_conditions = [
            Booking.cafe_id == cafe_id if cafe_id is not None else None,
            Booking.user_id == user_id if user_id is not None else None,
            Booking.is_active.is_(True) if not show_all else None,
        ]
        active_filters = [f for f in filter_conditions if f is not None]
        if active_filters:
            stmt = stmt.where(and_(*active_filters))
        result = await session.execute(stmt)
        bookings = result.scalars().all()
        logger.info(
            f'Получен список бронирований: {len(bookings)} записей '
            f'(show_all={show_all}, cafe_id={cafe_id}, user_id={user_id})'
        )
        return bookings

    async def _fetch_related_objects(
        self,
        session: AsyncSession,
        model,
        ids: Optional[List[int]],
    ) -> list:
        """Загружает связанные объекты по списку ID."""
        if not ids:
            return []
        result = await session.scalars(select(model).where(model.id.in_(ids)))
        return list(result)

    async def _check_booking_overlap(
        self,
        session: AsyncSession,
        *,
        cafe_id: int,
        slot_ids: List[int],
        table_ids: List[int],
        exclude_booking_id: Optional[int] = None,
    ) -> None:
        """
        Проверяет, заняты ли выбранные слоты или столы в кафе.

        Параметр exclude_booking_id нужен, чтобы при обновлении
        не вызывать пересечение с самим собой.
        """
        checks = [
            (Booking.slots, Slot.id, slot_ids,
             'Выбранные слоты уже заняты.'),
            (Booking.tables, Table.id, table_ids,
             'Выбранные столы уже забронированы.'),
        ]
        for relation, model_id, ids, error_msg in checks:
            if not ids:
                continue
            conditions = [
                Booking.cafe_id == cafe_id,
                model_id.in_(ids),
                Booking.status != BookingStatus.CANCELED,
            ]
            if exclude_booking_id is not None:
                conditions.append(Booking.id != exclude_booking_id)
            stmt = select(Booking).join(relation).where(and_(*conditions))
            result = await session.execute(stmt)
            if result.scalars().first():
                raise BookingOverlapException(error_msg)

    async def _validate_booking_date(
        self,
        session: AsyncSession,
        slot_ids: List[int],
    ) -> None:
        """Проверка даты брони на предшествующую текущей."""
        slots = await self._fetch_related_objects(session, Slot, slot_ids)
        now = datetime.now().date()
        for slot in slots:
            if slot.date < now:
                raise BookingDateException()

    async def _validate_related_resources(
        self,
        session: AsyncSession,
        obj_in: BookingCreate,
    ) -> tuple[list[Table], list[Slot], list[Dishe]]:
        """Проверяет существование кафе, столов, слотов и блюд."""
        cafe = await session.get(Cafe, obj_in.cafe_id)
        if cafe is None:
            raise BookingResourceNotFoundException('Указанное кафе не найдено')
        db_tables, db_slots, db_menu = await asyncio.gather(
            self._fetch_related_objects(session, Table, obj_in.tables),
            self._fetch_related_objects(session, Slot, obj_in.slots),
            self._fetch_related_objects(session, Dishe, obj_in.menu),
        )
        checks = [
            (db_tables, obj_in.tables, 'Некоторые столы не найдены'),
            (db_slots, obj_in.slots, 'Некоторые временные слоты не найдены'),
            (db_menu, obj_in.menu, 'Некоторые блюда не найдены'),
        ]
        for db_objs, input_ids, error_msg in checks:
            if input_ids and len(db_objs) != len(input_ids):
                raise BookingResourceNotFoundException(error_msg)
        return db_tables, db_slots, db_menu

    async def create_booking(
        self,
        obj_in: BookingCreate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> Booking:
        """Создание нового бронирования с проверками существования ресурсов."""
        try:
            (
                db_tables,
                db_slots,
                db_menu,
            ) = await self._validate_related_resources(
                session,
                obj_in,
            )
            await self._validate_booking_date(session, obj_in.slots)
            await self._check_booking_overlap(
                session,
                cafe_id=obj_in.cafe_id,
                slot_ids=obj_in.slots,
                table_ids=obj_in.tables,
            )
            db_obj = Booking(
                user_id=obj_in.user_id,
                cafe_id=obj_in.cafe_id,
                guests_number=obj_in.guests_number,
                note=obj_in.note,
                status=BookingStatus.BOOKING,
            )
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            db_obj.tables = db_tables
            db_obj.menu = db_menu
            db_obj.slots = db_slots
            await self._commit(session, user)
            await session.refresh(db_obj)
            logger.info(f'Создано бронирование ID={db_obj.id}', user=user)
            return db_obj
        except AppException:
            await session.rollback()
            raise
        except Exception as error:
            await session.rollback()
            logger.error(f'Ошибка при создании бронирования: {error}',
                         user=user)
            raise DBException('Ошибка при создании бронирования')

    async def update_booking(
        self,
        db_obj: Booking,
        obj_in: BookingUpdate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> Booking:
        """Обновление бронирования с запретом изменять активные/прошедшие."""
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            if db_obj.status == BookingStatus.ACTIVE:
                raise BookingUpdateForbiddenException(
                    'Нельзя изменить активное бронирование')
            slots = db_obj.slots
            if slots and any(
                slot.date < datetime.now().date() for slot in slots
            ):
                raise BookingUpdateForbiddenException(
                    'Нельзя изменить прошедшее бронирование')
            if 'slots' in update_data and update_data['slots']:
                await self._validate_booking_date(
                    session, update_data['slots'])
                await self._check_booking_overlap(
                    session,
                    cafe_id=db_obj.cafe_id,
                    slot_ids=update_data['slots'],
                    table_ids=update_data.get('tables', []),
                    exclude_booking_id=db_obj.id,
                )
                db_obj.slots = await self._fetch_related_objects(
                    session, Slot, update_data['slots'])
            related_fields = {
                'tables': Table,
                'menu': Dishe,
            }
            for field, model in related_fields.items():
                if field in update_data and update_data[field]:
                    setattr(
                        db_obj,
                        field,
                        await self._fetch_related_objects(
                            session, model, update_data[field]),
                    )
            for field, value in update_data.items():
                if field not in {'slots', 'tables', 'menu'}:
                    setattr(db_obj, field, value)
            session.add(db_obj)
            await self._commit(session, user)
            await session.refresh(db_obj)
            logger.info(f'Обновлено бронирование ID={db_obj.id}', user=user)
            return db_obj
        except (DBIntegrityException, DBException):
            await session.rollback()
            raise
        except Exception as error:
            await session.rollback()
            logger.error(f'Ошибка при обновлении бронирования: {error}',
                         user=user)
            raise DBException('Ошибка при обновлении бронирования')
