from typing import Any, Callable, List, Optional, Union

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import cafe_check_duplicate_responses
from src.core.logger import logger
from src.crud.action import actions_crud
from src.crud.factory import get_cafe_crud
from src.models import Action, Cafe, User
from src.schemas.cafes import CafeCreate, CafeDB

cafe_crud = get_cafe_crud()


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


async def cafe_existence(
        session: AsyncSession,
        cafe_id: Optional[int],
) -> None:
    """Проверяет наличе кафе по его ID."""
    if cafe_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого кафе',
        )

    cafe = await session.execute(
        select(Cafe).where(Cafe.id == cafe_id),
    )
    cafe_obj = cafe.scalar_one_or_none()

    if cafe_obj is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Кафе с ID {cafe_id} не найдено.',
        )
