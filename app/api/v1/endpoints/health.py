from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> dict:
    return {"status": "healthy", "service": "IIC3964 Backend"}


@router.get("/detailed")
async def detailed_health_check() -> dict:
    return {
        "status": "healthy",
        "service": "IIC3964 Backend",
        "version": "1.0.0",
        "environment": "development",
    }
