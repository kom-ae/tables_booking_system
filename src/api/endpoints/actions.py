from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.actions import (
    action_create_responses,
    action_get_responses,
    action_not_found,
    action_update_responses,
    actions_list_responses,
)
from src.api.validators import check_action_exist
from src.core.db import get_async_session
from src.core.dependencies import current_admin, current_manager, current_user
from src.core.logger import log_endpoint, logger
from src.crud.action import actions_crud
from src.models import User
from src.schemas.action import ActionCreate, ActionDB, ActionUpdate

router = APIRouter()


@router.get(
    '',
    response_model=list[ActionDB],
    response_model_exclude_none=True,
    response_description='Список акций',
    responses=actions_list_responses,
    summary='Получение списка акций'
    ' (только для администратора, пользователь - только активные).',
)
@log_endpoint
async def get_actions(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user),
    cafe_id: Optional[int] = Query(
        None,
        description='Показать акции только в указанном кафе',
    ),
    show_all: bool = Query(
        False,
        description='Показать все акции (только для админа/менеджера)',
    ),
) -> list[ActionDB]:
    """Получение списка акций."""
    logger.info(
        f'{get_actions.__doc__} show_all: {show_all} | cafe_id: {cafe_id}',
        user=current_user,
    )
    return await actions_crud.get_all_actions(
        session=session,
        current_user=current_user,
        cafe_id=cafe_id,
        show_all=show_all,
    )


@router.post(
    '',
    response_model=ActionDB,
    response_model_exclude_none=True,
    response_description='Данные созданной акции',
    responses=action_create_responses,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_manager)],
    summary='Создание акций (только для администратора и менеджера).',
)
@log_endpoint
async def create_action(
    action: ActionCreate,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_manager),
) -> ActionDB:
    """Создание акции."""
    logger.info(
        f'{create_action.__doc__} Данные:',
        user=admin,
        info_dict=action,
    )

    new_action = await actions_crud.create_action(
        obj_in=action,
        session=session,
    )

    logger.info(f'Создана акция с ID: {new_action.id}', user=admin)

    return new_action


@router.get(
    '/{action_id}',
    response_model=ActionDB,
    response_model_exclude_none=True,
    responses=action_get_responses,
    summary='Получение акции по ID'
    ' (только для администратора и менеджера, пользователь - только активные)',
    dependencies=[Depends(current_user)],
)
@log_endpoint
async def get_action_by_id(
    action_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user),
) -> ActionDB:
    """Получение акции по ID."""
    logger.info(
        f'{get_action_by_id.__doc__} ID: {action_id}',
        user=current_user,
    )
    action = await actions_crud.get_action(
        session,
        action_id,
        current_user,
    )

    if action is None:
        raise HTTPException(**action_not_found)

    return action


@router.patch(
    '/{action_id}',
    response_model=ActionDB,
    response_model_exclude_none=True,
    responses=action_update_responses,
    summary='Обновление акции по ID (только для администратора и менеджера)',
    dependencies=[Depends(current_manager)],
)
@log_endpoint
async def update_action_by_id(
    action_id: int,
    update_data: ActionUpdate,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> ActionDB:
    """Обновление акции по ID."""
    logger.info(
        f'{update_action_by_id.__doc__} ID: {action_id}. Данные',
        user=admin,
        info_dict=update_data,
    )

    action = await check_action_exist(
        action_id=action_id,
        session=session,
    )

    action = await actions_crud.update_action(
        db_obj=action,
        obj_in=update_data,
        session=session,
    )

    logger.info(f'Обновлена акция с ID: {action.id}', user=admin)

    return action
