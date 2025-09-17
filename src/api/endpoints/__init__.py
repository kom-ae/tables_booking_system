from src.api.endpoints.user import router as user_router  # noqa
from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router()
