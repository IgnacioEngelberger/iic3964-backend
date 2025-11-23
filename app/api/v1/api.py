from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    clinical_attentions,
    doctors,
    gemini,
    health,
    items,
    patients,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(gemini.router, prefix="/gemini", tags=["gemini"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])
api_router.include_router(
    clinical_attentions.router, prefix="", tags=["Clinical Attentions"]
)
