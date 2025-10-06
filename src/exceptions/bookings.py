from fastapi import status
from src.exceptions.base import AppException


class BookingNotFoundException(AppException):
    """Бронирование не найдено."""

    error_code: str = 'BookingNotFound'

    def __init__(self, message: str = 'Бронирование не найдено') -> None:
        """Исключение 404 при отсутствии бронирования."""
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BookingDateException(AppException):
    """Исключение 400: бронирование на прошедшую дату."""

    error_code: str = 'BookingDateError'

    def __init__(
            self,
            message: str = 'Нельзя бронировать на прошедшую дату') -> None:
        """Исключение 400 при бронировании на прошедшую дату."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class BookingOverlapException(AppException):
    """Исключение 400: пересечение по слотам."""

    error_code: str = 'BookingOverlap'

    def __init__(self, message: str = 'Выбранные слоты уже заняты') -> None:
        """Исключение 400 при пересечении слотов."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class BookingUpdateForbiddenException(AppException):
    """Исключение 400: нельзя обновить активное или прошедшее бронирование."""

    error_code: str = 'BookingUpdateForbidden'

    def __init__(
        self,
        message: str = 'Нельзя изменить активное или прошедшее бронирование',
    ) -> None:
        """Исключение 400 при запрете изменения брони."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class BookingResourceNotFoundException(AppException):
    """Исключение 400: ресурсы не найдены."""

    error_code: str = 'BookingResourceNotFound'

    def __init__(
            self, message: str = 'ННеверные идентификаторы ресурсов') -> None:
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
