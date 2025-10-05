import logging
from functools import wraps
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

from src.constants import (
    BACKUP_COUNT_TEMP_LOGER,
    DEFAULT_USER_ID,
    LOG_FILE_APP_LOGGER,
    MAX_BYTES_TEMP_LOGER,
    SYSTEM_USERNAME,
)


class FastAPILogger(Logger):
    """Логгер с поддержкой пользователя."""

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        """Инициализация логгера."""
        super().__init__(name, level)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Настройка обработчиков логов."""
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S',
        )

        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            log_dir / LOG_FILE_APP_LOGGER,
            maxBytes=MAX_BYTES_TEMP_LOGER,
            backupCount=BACKUP_COUNT_TEMP_LOGER,
            encoding='utf-8',
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.addHandler(file_handler)
        self.addHandler(console_handler)

        self.propagate = False

    def _format_user(self, user: Any) -> str:
        """Форматирование информации о пользователе."""
        if not user:
            return f'{SYSTEM_USERNAME} | {DEFAULT_USER_ID}'

        if isinstance(user, dict):
            return (
                f'{user.get("username", SYSTEM_USERNAME)} '
                f'| {user.get("id", DEFAULT_USER_ID)}'
            )

        try:
            username = getattr(user, 'username', SYSTEM_USERNAME)
            user_id = getattr(user, 'id', DEFAULT_USER_ID)
            return f'{username} | {user_id}'
        except Exception:
            return f'{SYSTEM_USERNAME} | {DEFAULT_USER_ID}'

    def get_message(
        self,
        msg: str,
        user: Any = None,
        info_dict: Optional[dict] = None,
    ) -> str:
        """Формирование сообщения с пользователем."""
        try:
            base_msg = f'{self._format_user(user)} | {msg}'
            if info_dict:
                base_msg += f': {info_dict}'
            return base_msg
        except Exception:
            return f'{SYSTEM_USERNAME} | {msg}'

    def _log_with_user(
        self,
        level: int,
        msg: str,
        user: Any = None,
        info_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        """Логирование с информацией о пользователе."""
        try:
            message = self.get_message(msg, user, info_dict)
            super().log(level, message, **kwargs)
        except Exception:
            super().log(level, f'{SYSTEM_USERNAME} | {msg}', **kwargs)

    def info(
        self,
        msg: str,
        user: Any = None,
        info_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        """Лог INFO."""
        self._log_with_user(logging.INFO, msg, user, info_dict, **kwargs)

    def warning(
        self,
        msg: str,
        user: Any = None,
        info_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        """Лог WARNING."""
        self._log_with_user(logging.WARNING, msg, user, info_dict, **kwargs)

    def error(
        self,
        msg: str,
        user: Any = None,
        info_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        """Лог ERROR."""
        self._log_with_user(logging.ERROR, msg, user, info_dict, **kwargs)

    def debug(
        self,
        msg: str,
        user: Any = None,
        info_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        """Лог DEBUG."""
        self._log_with_user(logging.DEBUG, msg, user, info_dict, **kwargs)


logger: FastAPILogger = FastAPILogger(__name__)


def log_endpoint(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Декоратор логирования вызова эндпоинта."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        user = kwargs.get('user')
        logger.info(f'Вызов эндпоинта: {func.__name__}', user=user)
        try:
            return await func(*args, **kwargs)
        except Exception as error:
            logger.error(
                f'Ошибка в эндпоинте {func.__name__}: {error}',
                user=user,
            )
            raise

    return wrapper
