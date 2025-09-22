from fastapi import HTTPException, status


class SlotNotFoundException(HTTPException):
    """Исключение 404: слот не найден."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден",
        )


class CafeOrSlotNotFoundException(HTTPException):
    """Исключение 404: кафе или слот не найдены."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кафе или слот не найдены",
        )


class SlotOverlapException(HTTPException):
    """Исключение 400: интервал слота пересекается."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Интервал времени слота пересекается с "
                "существующим активным слотом"
            ),
        )
