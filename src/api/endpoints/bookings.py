from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.bookings import (
    booking_create_responses,
    booking_get_responses,
    booking_list_responses,
    booking_update_responses,
)
from src.api.validators import visible_booking_for_user
from src.core.db import get_async_session
from src.core.dependencies import current_user
from src.core.logger import log_endpoint, logger
from src.crud.factory import get_booking_crud
from src.exceptions.bookings import BookingNotFoundException
from src.models import Booking, User
from src.schemas.bookings import (
    Booking as BookingDB,
    BookingCreate,
    BookingUpdate
)

router = APIRouter()
booking_crud = get_booking_crud()


@router.get(
    '',
    response_model=list[BookingDB],
    response_description='Список бронирований',
    responses=booking_list_responses,
    summary='Получение списка бронирований',
)
@log_endpoint
async def get_bookings(
    show_all: Optional[bool] = Query(
        None,
        description=(
            'Показать все '
            '(для администратора и менеджера (только в своем кафе)) '
            'бронирования (если не задан, возвращаются только бронирования '
            'с активным статусом)'
        ),
    ),
    cafe_id: Optional[int] = Query(
        None,
        description='Показать все бронирования в кафе',
    ),
    user_id: Optional[int] = Query(
        None,
        description='Показать все бронирования пользователя',
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> list[BookingDB]:
    """Получение списка бронирований с учётом роли пользователя."""
    logger.info(f'{get_bookings.__doc__}', user=user)
    if user.is_admin():
        return await booking_crud.get_bookings(
            session=session,
            show_all=show_all,
            cafe_id=cafe_id,
            user_id=user_id,
        )
    if user.is_manager():
        cafes = getattr(user, 'cafes', [])
        cafe_ids = [c.id for c in cafes] if cafes else []
        return await booking_crud.get_bookings(
            session=session,
            show_all=show_all,
            cafe_id=cafe_id or (cafe_ids[0] if cafe_ids else None),
            user_id=user_id,
        )
    return await booking_crud.get_bookings(
        session=session,
        show_all=False,
        user_id=user.id,
    )


@router.post(
    '',
    response_model=BookingDB,
    status_code=status.HTTP_201_CREATED,
    response_description='Данные созданного бронирования',
    responses=booking_create_responses,
    summary='Создание бронирования',
)
@log_endpoint
async def create_booking(
    booking_in: BookingCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> BookingDB:
    """Создание бронирования (для администратора, менеджера и пользователя)."""
    logger.info(
        f'{create_booking.__doc__}',
        user=user,
        info_dict=booking_in.model_dump(),
    )
    if (
        not (user.is_manager() or user.is_admin())
        and booking_in.user_id != user.id
    ):
        raise BookingNotFoundException(
            'Недостаточно прав для создания бронирования',)
    return await booking_crud.create_booking(
        obj_in=booking_in,
        session=session,
        user=user,
    )


@router.get(
    '/{booking_id}',
    response_model=BookingDB,
    response_description='Данные бронирования',
    responses=booking_get_responses,
    summary=('Получение бронирования по ID '
             '(только для администратора и менеджера, '
             'пользователь — только активные и свои)'),
)
@log_endpoint
async def get_booking_by_id(
    booking: Booking = Depends(visible_booking_for_user),
    user: User = Depends(current_user),
) -> BookingDB:
    """Получение бронирования по ID с учётом прав доступа."""
    logger.info(f'{get_booking_by_id.__doc__} ID={booking.id}', user=user)
    return booking


@router.patch(
    '/{booking_id}',
    response_model=BookingDB,
    responses=booking_update_responses,
    summary=('Обновление бронирования по ID '
             '(для администратора и менеджера, пользователь — только свои)'),
)
@log_endpoint
async def update_booking(
    *,
    booking_id: int = Path(..., description='ID бронирования'),
    booking_update: BookingUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> BookingDB:
    """Обновление бронирования по ID."""
    logger.info(
        f'{update_booking.__doc__} ID={booking_id}',
        user=user,
        info_dict=booking_update.model_dump(exclude_unset=True),
    )
    booking = await booking_crud.get_booking_id_or_404(booking_id, session)
    if not (user.is_admin() or user.is_manager()):
        if booking.user_id != user.id:
            raise BookingNotFoundException('Бронирование не найдено')
    return await booking_crud.update_booking(
        db_obj=booking,
        obj_in=booking_update,
        session=session,
        user=user,
    )
