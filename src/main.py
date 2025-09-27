from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.api import main_router
from src.constants import TAGS_METADATA
from src.core.config import settings
from src.core.init_db import init_db_and_superuser
from src.core.logger import init_logger
from src.exceptions.auth import (
    ExpiredTokenException,
    InvalidCredentialsException,
    InvalidTokenException,
    PermissionDeniedException,
)
from src.exceptions.base import AppException
from src.exceptions.db import DBIntegrityException
from src.exceptions.handlers import (
    base_api_exception_handler,
    db_integrity_exception_handler,
    expired_token_exception_handler,
    invalid_credentials_exception_handler,
    invalid_password_exception_handler,
    invalid_phone_exception_handler,
    invalid_token_exception_handler,
    permission_denied_exception_handler,
    user_not_found_exception_handler,
    validation_exception_handler,
)
from src.exceptions.user import (
    InvalidPasswordException,
    InvalidPhoneException,
    UserNotFoundException,
)

init_logger(settings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация БД и создание суперпользователя при старте приложения."""
    await init_db_and_superuser()
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
)

app.include_router(main_router)

app.add_exception_handler(
    InvalidPhoneException,
    invalid_phone_exception_handler,
)
app.add_exception_handler(
    InvalidPasswordException,
    invalid_password_exception_handler,
)
app.add_exception_handler(AppException, base_api_exception_handler)
app.add_exception_handler(
    InvalidTokenException,
    invalid_token_exception_handler,
)
app.add_exception_handler(
    ExpiredTokenException,
    expired_token_exception_handler,
)
app.add_exception_handler(
    InvalidCredentialsException,
    invalid_credentials_exception_handler,
)
app.add_exception_handler(
    PermissionDeniedException,
    permission_denied_exception_handler,
)
app.add_exception_handler(
    UserNotFoundException,
    user_not_found_exception_handler,
)
app.add_exception_handler(DBIntegrityException, db_integrity_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
