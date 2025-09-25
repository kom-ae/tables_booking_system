from src.core.db import Base  # noqa: F401

# ВАЖНО: импорты-маркеры, чтобы модели попали в Base.metadata
from src.models.user import User  # noqa: F401
from src.models.cafes import Cafes  # noqa: F401
from src.models.slots import Slots  # noqa: F401
from src.models.dish import Dishes  # noqa: F401
# замени на: from src.models.dish import Dish  # noqa: F401
