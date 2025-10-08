from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import (
    cafe_create_responses,
    cafe_get_responses,
    cafe_not_found,
    cafe_update_responses,
    cafes_list_responses,
)
from src.api.validators import check_duplicate_cafe, handler_run_crud_cafe
from src.core.db import get_async_session
from src.core.dependencies import current_admin, current_user
from src.core.logger import log_endpoint, logger
from src.crud.factory import get_cafe_crud
from src.models import User
from src.schemas.cafes import CafeCreate, CafeDB, CafeUpdate

router = APIRouter()
cafe_crud = get_cafe_crud()


@router.get(
    '/',
    response_model=List[CafeDB],
    response_model_exclude_none=True,
    response_description='Список кафе',
    responses=cafes_list_responses,
    summary='Получение списка кафе (только для администратора, '
    'пользователь - только активные)',
)
@log_endpoint
async def get_cafes(
    show_all: bool = Query(
        None,
        description='Показать все кафе (если не задан, '
        'возвращаются только активные кафе)',
    ),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[CafeDB]:
    """Получение списка кафе."""
    log_message = f'{get_cafes.__doc__} show_all: {show_all}.'

    if user.is_admin() and show_all:
        return await handler_run_crud_cafe(
            cafe_crud.get_multi_all,
            crud_args={'session': session},
            msg_log=log_message,
            user=user,
        )
    return await handler_run_crud_cafe(
        cafe_crud.get_multi_active,
        crud_args={'session': session},
        msg_log=log_message,
        user=user,
    )


@router.post(
    '/',
    response_model=CafeDB,
    response_model_exclude_none=True,
    response_description='Данные созданного кафе',
    responses=cafe_create_responses,
    summary='Создание кафе (только для администратора)',
    status_code=status.HTTP_201_CREATED,
)
async def create_cafe(
    cafe: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_admin),
) -> CafeDB:
    """Создание кафе."""
    await check_duplicate_cafe(cafe=cafe, session=session, user=user)

    return await handler_run_crud_cafe(
        cafe_crud.create,
        crud_args={'obj_in': cafe, 'user': user, 'session': session},
        msg_log=f'{create_cafe.__doc__} Данные {cafe.model_dump()}.',
        user=user,
    )


@router.get(
    '/{cafe_id}',
    response_model=CafeDB,
    response_model_exclude_none=True,
    responses=cafe_get_responses,
    summary='Получение кафе по ID (только для администратора, '
    'пользователь - только активные)',
)
@log_endpoint
async def get_cafe(
    cafe_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> CafeDB:
    """Получение кафе по ID."""
    if user.is_admin():
        obj_db = await handler_run_crud_cafe(
            cafe_crud.get,
            crud_args={'obj_id': cafe_id, 'session': session},
            msg_log=f'{get_cafe.__doc__}',
            user=user,
        )
    else:
        obj_db = await handler_run_crud_cafe(
            cafe_crud.get_active,
            crud_args={'obj_id': cafe_id, 'session': session},
            msg_log=f'{get_cafe.__doc__}',
            user=user,
        )
    if not obj_db:
        logger.error(f'Кафе с id={cafe_id} не найдено', user=user)
        raise HTTPException(**cafe_not_found)
    return obj_db


@router.patch(
    '/{cafe_id}',
    response_model=CafeDB,
    response_model_exclude_none=True,
    responses=cafe_update_responses,
    summary='Обновление кафе по ID (только для администратора)',
)
@log_endpoint
async def update_cafe(
    cafe_id: int,
    obj_in: CafeUpdate,
    user: User = Depends(current_admin),
    session: AsyncSession = Depends(get_async_session),
) -> CafeDB:
    """Обновление кафе по ID."""
    if obj_in.address and obj_in.name:
        await check_duplicate_cafe(cafe=obj_in, session=session, user=user)
    cafe = await handler_run_crud_cafe(
        cafe_crud.get,
        crud_args={'obj_id': cafe_id, 'session': session},
        msg_log='Получение кафе для обновления.',
        user=user,
    )
    if not cafe:
        logger.info(
            f'Кафе с id={cafe_id} для обновления не найдено.',
            user=user,
        )
        raise HTTPException(**cafe_not_found)

    return await handler_run_crud_cafe(
        cafe_crud.update,
        crud_args={
            'db_obj': cafe,
            'obj_in': obj_in,
            'user': user,
            'session': session,
        },
        msg_log=f'{update_cafe.__doc__} Данными: '
        f'{obj_in.model_dump(exclude_unset=True)}.',
        user=user,
    )
