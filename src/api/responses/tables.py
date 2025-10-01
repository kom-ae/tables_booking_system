from fastapi import status
from src.schemas.table import TableDB

TABLE_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {'description': 'Неавторизованный доступ'},
    status.HTTP_403_FORBIDDEN: {'description': 'Доступ запрещён'},
    status.HTTP_404_NOT_FOUND: {'description': 'Объект не найден'},
    status.HTTP_201_CREATED: {'description': 'Стол успешно создан'},
    status.HTTP_200_OK: {'description': 'Успешный ответ'},
}

tables_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Список столов кафе',
        'model': list[TableDB],
    },
    status.HTTP_401_UNAUTHORIZED: TABLE_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_403_FORBIDDEN: TABLE_RESPONSES[status.HTTP_403_FORBIDDEN],
    status.HTTP_404_NOT_FOUND: TABLE_RESPONSES[status.HTTP_404_NOT_FOUND],
}

table_create_responses = {
    status.HTTP_201_CREATED: TABLE_RESPONSES[status.HTTP_201_CREATED],
    status.HTTP_401_UNAUTHORIZED: TABLE_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_403_FORBIDDEN: TABLE_RESPONSES[status.HTTP_403_FORBIDDEN],
    status.HTTP_404_NOT_FOUND: TABLE_RESPONSES[status.HTTP_404_NOT_FOUND],
}

table_get_responses = {
    status.HTTP_200_OK: {'description': 'Данные стола', 'model': TableDB},
    status.HTTP_401_UNAUTHORIZED: TABLE_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_403_FORBIDDEN: TABLE_RESPONSES[status.HTTP_403_FORBIDDEN],
    status.HTTP_404_NOT_FOUND: {'description': 'Стол не найден'},
}

table_update_responses = {
    status.HTTP_200_OK: {
        'description': 'Стол успешно обновлён',
        'model': TableDB,
    },
    status.HTTP_401_UNAUTHORIZED: TABLE_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_403_FORBIDDEN: TABLE_RESPONSES[status.HTTP_403_FORBIDDEN],
    status.HTTP_404_NOT_FOUND: {'description': 'Стол не найден'},
}
