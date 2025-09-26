import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Coroutine, Optional

from src.constants import BACKUP_COUNT_TEMP_LOGER, MAX_BYTES_TEMP_LOGER

logger: logging.Logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)

file_handler: Optional[RotatingFileHandler] = None
console_handler: Optional[logging.StreamHandler] = None


def init_logger(settings: Any) -> None:
    """Инициализация логгера после создания Settings."""
    global file_handler, console_handler

    formatter: logging.Formatter = logging.Formatter(
        (
            '%(asctime)s | %(levelname)s | %(username)s | '
            '%(user_id)s | %(message)s'
        ),
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    file_handler = RotatingFileHandler(
        settings.log_file,  # type: ignore
        maxBytes=settings.max_bytes,  # type: ignore
        backupCount=settings.backup_count,  # type: ignore
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(
        logging.DEBUG if getattr(settings, 'debug', False) else logging.INFO,
    )


def log_event(
    level: str,
    message: str,
    username: Optional[str] = None,
    user_id: Optional[int] = None,
) -> None:
    """Централизованная функция логирования."""
    extra: dict[str, Optional[Any]] = {
        'username': username,
        'user_id': user_id,
    }
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
            user: Any = kwargs.get('user', None)
            username: Optional[str] = getattr(user, 'username', None)
            user_id: Optional[int] = getattr(user, 'id', None)
            log_event(
                level,
                f'Вызов эндпоинта: {func.__name__}',
                username,
                user_id,
            )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def temp_logger(log_file: Optional[str] = 'app_temp.log') -> logging.Logger:
    """Временный логгер для ошибок до инициализации Settings."""
    logger_temp: logging.Logger = logging.getLogger('temp_logger')
    if logger_temp.handlers:
        return logger_temp

    logger_temp.setLevel(logging.DEBUG)
    formatter: logging.Formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    file_handler_temp: RotatingFileHandler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES_TEMP_LOGER,
        backupCount=BACKUP_COUNT_TEMP_LOGER,
    )
    file_handler_temp.setFormatter(formatter)

    console_handler_temp: logging.StreamHandler = logging.StreamHandler()
    console_handler_temp.setFormatter(formatter)

    logger_temp.addHandler(file_handler_temp)
    logger_temp.addHandler(console_handler_temp)

    return logger_temp
