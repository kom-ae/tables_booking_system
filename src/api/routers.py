from fastapi import APIRouter

from src.api.endpoints.users import router as users_router

main_router = APIRouter()
main_router.include_router(users_router)
