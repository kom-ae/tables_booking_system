from __future__ import annotations

from typing import Any, Callable, List, Optional, Union

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import cafe_check_duplicate_responses
from src.api.responses.dishes import dish_check_duplicate_responses
from src.constants import ID_MIN
from src.core.db import get_async_session
from src.core.dependencies import (
    current_manager,
    current_user,
    get_current_user_or_none,
)
from src.core.logger import logger
from src.crud.action import actions_crud
from src.crud.factory import get_cafe_crud, get_dish_crud, get_slot_crud
from src.exceptions.db import DBException, DBIntegrityException
from src.exceptions.slots import (
    CafeOrSlotNotFoundException,
    SlotNotFoundException,
)
from src.models import Action, Cafe, Dishe, Slot, User
from src.schemas.cafes import CafeCreate, CafeDB
from src.schemas.dish import Dish, DishCreate

cafe_crud = get_cafe_crud()
slot_crud = get_slot_crud()
dish_crud = get_dish_crud()


async def check_duplicate_cafe(
    cafe: CafeCreate,
    session: AsyncSession,
    user: Optional[User] = None,
) -> None:
    """Проверить на существование дубликата кафе."""
    db_obj: Cafe = await handler_run_crud_cafe(
        cafe_crud.get_by_name_address,
        crud_args={
            'name': cafe.name,
            'address': cafe.address,
            'session': session,
        },
        msg_log='Поиск дубликата кафе.',
        user=user,
    )
    if db_obj:
        logger.error(
            'Попытка создать дубликат кафе',
            user,
            info_dict=cafe.model_dump(),
        )
        raise HTTPException(**cafe_check_duplicate_responses)
    logger.info('Дубликат кафе не найден.', user)


async def check_duplicate_dish(
    dish: DishCreate,
    session: AsyncSession,
    user: Optional[User] = None,
) -> None:
    """Проверить на существование дубликата блюда."""
    db_obj: Dishe = await handler_run_crud_dish(
        dish_crud.get_dish_by_name_and_cafe,
        crud_args={
            'name': dish.name,
            'cafe_id': dish.cafe,
            'session': session,
        },
        msg_log='Поиск дубликата блюда.',
        user=user,
    )
    if db_obj:
        logger.error(
            'Попытка создать дубликат блюда',
            user,
            info_dict=dish.model_dump(),
        )
        raise HTTPException(**dish_check_duplicate_responses)
    logger.info('Дубликат блюда не найден.', user)


async def check_action_exist(
    action_id: int,
    session: AsyncSession,
) -> Action:
    """Проверяет на наличие доступа и акции."""
    action = await actions_crud.get(
        obj_id=action_id,
        session=session,
    )
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Акция не найдена',
        )
    return action


async def handler_run_crud_cafe(
    func: Callable[..., Any],
    **kwargs: Any,
) -> Union[CafeDB, List[CafeDB]]:
    """Запуск корутины CRUD и логирование результата через logger.

    Аргументы:
        func: функция CRUD
        crud_args: словарь аргументов для функции
        msg_log: сообщение для логирования
        user: пользователь, инициирующий операцию
    """
    crud_args: dict = kwargs.get('crud_args', {})
    session: AsyncSession = crud_args.get('session')
    msg_log: str = kwargs.get('msg_log', '')
    user: Optional[User] = kwargs.get('user', None)

    logger.info(msg=f'Попытка: "{msg_log}"', user=user)

    try:
        if obj := await func(**crud_args):
            msg_log_full = msg_log
            if not isinstance(obj, list):
                msg_log_full += f' ID={str(obj.id)}.'
            msg_log_full += ' Успешно.'

            logger.info(msg_log_full, user=user)

        return obj
    except (DBIntegrityException, DBException) as err:
        await session.rollback()
        logger.error(
            f'Операция "{msg_log}": '
            f'Ошибка выполнения функции {func.__name__} '
            f'в модуле {func.__module__}: {str(err)}',
            user=user,
        )
        raise HTTPException(
            status_code=err.status_code,
            detail='Внутренняя ошибка сервера.',
        )
    except Exception as err:
        await session.rollback()
        logger.error(
            f'Операция "{msg_log}": '
            f'Ошибка выполнения функции {func.__name__} '
            f'в модуле {func.__module__}: {str(err)}',
            user=user,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка сервера.',
        )


async def _get_cafe_or_none(
    session: AsyncSession,
    cafe_id: int,
) -> Optional[Cafe]:
    """Вернуть объект Cafe или None (без исключений)."""
    res = await session.execute(select(Cafe).where(Cafe.id == cafe_id))
    return res.scalar_one_or_none()


async def _ensure_cafe_exists(
    session: AsyncSession,
    cafe_id: int,
    *,
    not_found_status: int,
) -> Cafe:
    """Вернуть Cafe или кинуть HTTPException с нужным статусом."""
    cafe = await _get_cafe_or_none(session, cafe_id)
    if cafe is None:
        raise HTTPException(
            status_code=not_found_status,
            detail=f'Кафе с ID {cafe_id} не найдено.',
        )
    return cafe


async def handler_run_crud_dish(
    func: Callable[..., Any],
    **kwargs: Any,
) -> Union[Dish, List[Dish]]:
    """Запуск корутины CRUD для блюд и логирование результата через logger.

    Аргументы:
        func: функция CRUD
        crud_args: словарь аргументов для функции
        msg_log: сообщение для логирования
        user: пользователь, инициирующий операцию
    """
    crud_args: dict = kwargs.get('crud_args', {})
    session: AsyncSession = crud_args.get('session')
    msg_log: str = kwargs.get('msg_log', '')
    user: Optional[User] = kwargs.get('user', None)

    logger.info(msg=f'Попытка: "{msg_log}"', user=user)

    try:
        if obj := await func(**crud_args):
            msg_log_full = msg_log
            if not isinstance(obj, list):
                msg_log_full += f' ID={str(obj.id)}.'
            msg_log_full += ' Успешно.'

            logger.info(msg_log_full, user=user)

        return obj
    except (DBIntegrityException, DBException) as err:
        await session.rollback()
        logger.error(
            f'Операция "{msg_log}": '
            f'Ошибка выполнения функции {func.__name__} '
            f'в модуле {func.__module__}: {str(err)}',
            user=user,
        )
        raise HTTPException(
            status_code=err.status_code,
            detail='Внутренняя ошибка сервера.',
        )
    except Exception as err:
        await session.rollback()
        logger.error(
            f'Операция "{msg_log}": '
            f'Ошибка выполнения функции {func.__name__} '
            f'в модуле {func.__module__}: {str(err)}',
            user=user,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка сервера.',
        )


async def cafe_existence(
    session: AsyncSession,
    cafe_id: Optional[int],
) -> None:
    """Проверяет наличие кафе по его ID (контракт для actions: 400)."""
    if cafe_id is None:
        # Этот кейс обычно не встречается для path-параметров,
        # оставим как было.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого кафе',
        )
    # Для actions тесты ожидают 400 при отсутствии кафе.
    await _ensure_cafe_exists(
        session=session,
        cafe_id=cafe_id,
        not_found_status=status.HTTP_400_BAD_REQUEST,
    )


current_user_dep = Depends(current_user)
current_manager_dep = Depends(current_manager)
current_user_or_none_dep = Depends(get_current_user_or_none)


async def slot_in_cafe_exists(
    cafe_id: int = Path(..., ge=ID_MIN, description='ID кафе'),
    time_slot_id: int = Path(..., ge=ID_MIN, description='ID слота'),
    session: AsyncSession = Depends(get_async_session),
) -> Slot:
    """Слот существует и относится к указанному кафе, иначе 404."""
    slot = await slot_crud.get(obj_id=time_slot_id, session=session)
    if not slot or slot.cafe_id != cafe_id:
        raise CafeOrSlotNotFoundException()
    return slot


async def visible_slot_for_user(
    cafe_id: int = Path(..., ge=ID_MIN, description='ID кафе'),
    time_slot_id: int = Path(..., ge=ID_MIN, description='ID слота'),
    session: AsyncSession = Depends(get_async_session),
    user: Optional[User] = current_user_or_none_dep,
) -> Slot:
    """Определить видимость слота для запрашивающего пользователя.

    Правила:
    - superuser/admin/manager видят любой слот;
    - остальные — только активный (иначе 404).
    """
    slot = await slot_in_cafe_exists(cafe_id, time_slot_id, session)
    if user and user.is_manager():
        return slot
    if not bool(slot.is_active):
        raise SlotNotFoundException()
    return slot


async def cafe_exists_404_for_slots(
    cafe_id: int = Path(..., ge=ID_MIN, description='ID кафе'),
    session: AsyncSession = Depends(get_async_session),
) -> Cafe:
    """Вернуть кафе или 404 (контракт для эндпоинтов слотов)."""
    return await _ensure_cafe_exists(
        session=session,
        cafe_id=cafe_id,
        not_found_status=status.HTTP_404_NOT_FOUND,
    )
