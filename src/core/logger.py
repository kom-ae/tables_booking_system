import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Coroutine, Optional

from core.config import settings

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(username)s | %(user_id)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

file_handler = RotatingFileHandler(
    settings.log_file,
    maxBytes=settings.max_bytes,
    backupCount=settings.backup_count,
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
    username: Optional[str] = settings.system_username,
    user_id: Optional[int] = settings.default_user_id,
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
            username = getattr(user, 'username', settings.system_username)
            user_id = getattr(user, 'id', settings.default_user_id)
            log_event(
                level,
                f'Вызов эндпоинта: {func.__name__}',
                username,
                user_id,
            )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
