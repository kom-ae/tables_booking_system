from fastapi import APIRouter

from src.api.endpoints import users

main_router = APIRouter()
main_router.include_router(users)
