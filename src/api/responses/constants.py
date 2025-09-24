from src.schemas.base import Error

# Описания кодов ответа для эндпоинта кафе.
CAFE_RESPONSES = {
    400: {
        'description': 'Неверный формат запроса',
        'model': Error,
    },
    401: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    404: {
        'description': 'Кафе не найдено',
        'model': Error,
    },
}
