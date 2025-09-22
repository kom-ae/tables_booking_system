from fastapi import APIRouter
from src.api.endpoints.slots import router as slots_router

main_router = APIRouter(prefix="/api")
main_router.include_router(slots_router)
