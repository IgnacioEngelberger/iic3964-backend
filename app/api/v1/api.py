from fastapi import APIRouter

from app.api.v1.endpoints import clinical_attentions, health, items

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(
    clinical_attentions.router, prefix="", tags=["Clinical Attentions"]
)
