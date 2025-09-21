from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.auth import login_responses, logout_responses
from src.api.utils.auth import create_access_token, verify_password
from src.constants import SYSTEM_USERNAME, ZERO_DEFAULT_USER_ID
from src.core.db import get_async_session
from src.core.logger import log_endpoint, log_event
from src.core.user import get_user_by_name
from src.exceptions.auth import InvalidCredentialsException
from src.schemas.auth import Auth, TokenResponse

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenResponse,
    responses=login_responses,
    status_code=status.HTTP_200_OK,
    summary='Аутентификация пользователя',
)
@log_endpoint('info')
async def login(
    auth: Auth,
    db: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Авторизация пользователя и выдача JWT по email или телефону."""
    user = await get_user_by_name(auth.name, db)
    if not user or not verify_password(auth.password, user.password):
        raise InvalidCredentialsException()

    log_event(
        'info',
        'Успешный вход в систему',
        username=user.username,
        user_id=user.id,
    )

    token: str = create_access_token(data={'sub': str(user.id)})
    return {'token': token}


@router.post(
    '/logout',
    responses=logout_responses,
    summary='Выход из аккаунта',
)
@log_endpoint('info')
async def logout() -> dict[str, str]:
    """Выход пользователя (информативно, JWT статический)."""
    log_event(
        'info',
        'Пользователь вышел из системы',
        username=SYSTEM_USERNAME,
        user_id=ZERO_DEFAULT_USER_ID,
    )
    return {'message': 'Вы вышли из системы.'}
