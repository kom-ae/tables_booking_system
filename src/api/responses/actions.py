from fastapi import status

from src.api.responses.constants import ACTIONS_RESPONSES
from src.schemas.action import ActionDB

actions_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Список акций',
        'model': list[ActionDB],
    },
    status.HTTP_401_UNAUTHORIZED: ACTIONS_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
}

action_create_responses = {
    status.HTTP_201_CREATED: ACTIONS_RESPONSES[status.HTTP_201_CREATED],
    status.HTTP_400_BAD_REQUEST: ACTIONS_RESPONSES[
        status.HTTP_400_BAD_REQUEST
    ],
    status.HTTP_401_UNAUTHORIZED: ACTIONS_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
}

action_get_responses = {
    status.HTTP_200_OK: ACTIONS_RESPONSES[status.HTTP_200_OK],
    status.HTTP_401_UNAUTHORIZED: ACTIONS_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_404_NOT_FOUND: ACTIONS_RESPONSES[status.HTTP_404_NOT_FOUND],
}

action_update_responses = {
    status.HTTP_200_OK: ACTIONS_RESPONSES[status.HTTP_200_OK],
    status.HTTP_400_BAD_REQUEST: ACTIONS_RESPONSES[
        status.HTTP_400_BAD_REQUEST
    ],
    status.HTTP_401_UNAUTHORIZED: ACTIONS_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_404_NOT_FOUND: ACTIONS_RESPONSES[status.HTTP_404_NOT_FOUND],
}

action_not_found = {
    'status_code': status.HTTP_404_NOT_FOUND,
    'detail': 'Кафе не найдено.',
}
