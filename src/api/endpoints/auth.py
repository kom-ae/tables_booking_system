from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.auth import login_responses, logout_responses
from src.constants import DEFAULT_USER_ID, SYSTEM_USERNAME
from src.core.db import get_async_session
from src.core.logger import log_endpoint, logger
from src.core.user import get_user_by_name
from src.crud.factory import CRUDUser, get_user_crud
from src.exceptions.auth import InvalidCredentialsException
from src.schemas.auth import Auth, TokenResponse
from src.services.auth import PasswordService, TokenService

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenResponse,
    responses=login_responses,
    status_code=status.HTTP_200_OK,
    summary='Аутентификация пользователя',
)
@log_endpoint
async def login(
    auth: Auth,
    db: AsyncSession = Depends(get_async_session),
    user_crud: CRUDUser = Depends(get_user_crud),
) -> TokenResponse:
    """Авторизация пользователя и выдача JWT по email или телефону."""
    user = await get_user_by_name(auth.name, db, user_crud=user_crud)

    if not user:
        PasswordService.dummy_verify()
        raise InvalidCredentialsException()

    if not PasswordService.verify_password(auth.password, user.password):
        raise InvalidCredentialsException()

    await user_crud.update_last_used(db, user)
    logger.info(f'{login.__doc__} USER_NAME: {auth.name}')

    token: str = TokenService.create_access_token(data={'sub': str(user.id)})
    return {'token': token}


@router.post(
    '/logout',
    responses=logout_responses,
    summary='Выход из аккаунта',
)
@log_endpoint
async def logout() -> dict[str, str]:
    """Выход пользователя (информативно, JWT статический)."""

    class SystemUser:
        id = DEFAULT_USER_ID
        username = SYSTEM_USERNAME

    logger.info('Пользователь вышел из системы', user=SystemUser())
    return {'message': 'Вы вышли из системы.'}
