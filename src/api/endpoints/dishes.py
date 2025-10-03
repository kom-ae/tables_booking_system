from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.dishes import (
    dish_create_responses,
    dish_get_responses,
    dish_not_found,
    dish_update_responses,
    dishes_list_responses,
)
from src.api.validators import (
    cafe_existence,
    check_duplicate_dish,
    handler_run_crud_dish,
)
from src.core.db import get_async_session
from src.core.dependencies import current_manager, current_user
from src.core.logger import log_endpoint, logger
from src.crud.factory import get_dish_crud
from src.models.user import User
from src.schemas.dish import Dish, DishCreate, DishUpdate

router = APIRouter()
dish_crud = get_dish_crud()


@router.get(
    '',
    response_model=List[Dish],
    response_model_exclude_none=True,
    response_description='Список блюд',
    responses=dishes_list_responses,
    summary='Получение списка блюд (только для администратора и менеджера, '
    'пользователь - только активные)',
)
@log_endpoint
async def get_dishes(
    show_all: bool = Query(
        None,
        description='Показать все блюда (если не задан, '
        'возвращаются только блюда с активным статусом)',
    ),
    cafe_id: Optional[int] = Query(
        None,
        description='Показать все блюда в кафе',
    ),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[Dish]:
    """Получение списка блюд."""
    log_message = (
        f'{get_dishes.__doc__} show_all: {show_all}, cafe_id: {cafe_id}.'
    )

    if cafe_id:
        if user.is_admin() or user.is_manager():
            only_active = not show_all if show_all is not None else True
        else:
            only_active = True

        return await handler_run_crud_dish(
            dish_crud.get_dishes_by_cafe_id,
            crud_args={
                'cafe_id': cafe_id,
                'session': session,
                'only_active': only_active,
            },
            msg_log=log_message,
            user=user,
        )
    if user.is_admin() or user.is_manager():
        only_active = not show_all if show_all is not None else True
    else:
        only_active = True
    return await handler_run_crud_dish(
        dish_crud.get_all_dishes,
        crud_args={
            'session': session,
            'only_active': only_active,
        },
        msg_log=log_message,
        user=user,
    )


@router.post(
    '',
    response_model=Dish,
    response_model_exclude_none=True,
    response_description='Данные созданного блюда',
    responses=dish_create_responses,
    summary='Создание блюда (только для администратора и менеджера)',
    status_code=status.HTTP_201_CREATED,
)
@log_endpoint
async def create_dish(
    dish: DishCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_manager),
) -> Dish:
    """Создание блюда."""
    await check_duplicate_dish(dish=dish, session=session, user=user)
    await cafe_existence(cafe_id=dish.cafe, session=session)
    return await handler_run_crud_dish(
        dish_crud.create_dish,
        crud_args={
            'obj_in': dish,
            'session': session,
        },
        msg_log=f'{create_dish.__doc__} Данные {dish.model_dump()}.',
        user=user,
    )


@router.get(
    '/{dish_id}',
    response_model=Dish,
    response_model_exclude_none=True,
    responses=dish_get_responses,
    summary='Получение блюда по ID (только для администратора и менеджера, '
    'пользователь - только активные)',
)
@log_endpoint
async def get_dish(
    dish_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> Dish:
    """Получение блюда по ID."""
    if user.is_admin() or user.is_manager():
        obj_db = await handler_run_crud_dish(
            dish_crud.get,
            crud_args={'obj_id': dish_id, 'session': session},
            msg_log=f'{get_dish.__doc__}',
            user=user,
        )
    else:
        obj_db = await handler_run_crud_dish(
            dish_crud.get_active,
            crud_args={'obj_id': dish_id, 'session': session},
            msg_log=f'{get_dish.__doc__}',
            user=user,
        )
    if not obj_db:
        logger.error(f'Блюдо с id={dish_id} не найдено', user=user)
        raise HTTPException(**dish_not_found)
    return obj_db


@router.patch(
    '/{dish_id}',
    response_model=Dish,
    response_model_exclude_none=True,
    responses=dish_update_responses,
    summary='Обновление блюда по ID (только для администратора и менеджера)',
)
@log_endpoint
async def update_dish(
    dish_id: int,
    obj_in: DishUpdate,
    user: User = Depends(current_manager),
    session: AsyncSession = Depends(get_async_session),
) -> Dish:
    """Обновление блюда по ID."""
    dish = await handler_run_crud_dish(
        dish_crud.get,
        crud_args={'obj_id': dish_id, 'session': session},
        msg_log='Получение блюда для обновления.',
        user=user,
    )
    if not dish:
        logger.info(
            f'Блюдо с id={dish_id} для обновления не найдено.',
            user=user,
        )
        raise HTTPException(**dish_not_found)

    return await handler_run_crud_dish(
        dish_crud.update_dish,
        crud_args={
            'dish_obj': dish,
            'obj_in': obj_in,
            'session': session,
        },
        msg_log=f'{update_dish.__doc__} Данными: '
        f'{obj_in.model_dump(exclude_unset=True)}.',
        user=user,
    )
