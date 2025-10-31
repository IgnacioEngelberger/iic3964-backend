from fastapi import APIRouter

from app.api.v1.endpoints import health, items, gemini

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(gemini.router, prefix="/gemini", tags=["gemini"])
