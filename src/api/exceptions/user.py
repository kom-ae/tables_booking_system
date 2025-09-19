class UserException(Exception):
    """Базовое исключение для пользователя."""

    def __init__(self, message: str) -> None:
        """Инициализирует исключение с заданным сообщением."""
        self.message = message
        super().__init__(message)


class UserAlreadyExistsException(UserException):
    """Исключение, если email/phone уже занят."""


class InvalidPhoneException(UserException):
    """Исключение при некорректном номере телефона."""


class UserNotFoundException(UserException):
    """Исключение, если пользователь не найден."""
