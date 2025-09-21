import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Coroutine, Optional

from src.constants import (
    BACKUP_COUNT,
    LOG_FILE,
    MAX_BYTES,
    SYSTEM_USERNAME,
    ZERO_DEFAULT_USER_ID,
)

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(username)s | %(user_id)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_event(
    level: str,
    message: str,
    username: Optional[str] = SYSTEM_USERNAME,
    user_id: Optional[int] = ZERO_DEFAULT_USER_ID,
) -> None:
    """Централизованная функция логирования."""
    extra = {'username': username, 'user_id': user_id}
    logger.log(getattr(logging, level.upper()), message, extra=extra)


def log_endpoint(
    level: str = 'info',
) -> Callable[
    [Callable[..., Coroutine[Any, Any, Any]]],
    Callable[..., Coroutine[Any, Any, Any]],
]:
    """Декоратор для эндпоинтов FastAPI."""

    def decorator(
        func: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            user = kwargs.get('user', None)
            username = getattr(user, 'username', SYSTEM_USERNAME)
            user_id = getattr(user, 'id', ZERO_DEFAULT_USER_ID)
            log_event(
                level,
                f'Вызов эндпоинта: {func.__name__}',
                username,
                user_id,
            )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
