from fastapi import Body, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.constants import KNOWN_DX, URGENT_RULE

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API para proyecto universitario IIC3964",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict:
    return {"message": "IIC3964 Backend API", "version": settings.VERSION}


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}


# Endpoints Sprint 1 hardcodeados


@app.get("/api/v1/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort: str = Query("createdAt"),
    order: str = Query("desc", regex="^(asc|desc)$"),
):
    all_users = [
        {"id": i, "name": f"Usuario {i}", "email": f"usuario{i}@test.com"}
        for i in range(1, 106)
    ]

    start = (page - 1) * limit
    end = start + limit
    users_page = all_users[start:end]

    total_items = len(all_users)
    total_pages = (total_items + limit - 1) // limit

    response_data = {
        "data": users_page,
        "meta": {
            "totalItems": total_items,
            "totalPages": total_pages,
            "currentPage": page,
            "itemsPerPage": limit,
            "sort": sort,
            "order": order,
        },
    }

    response = JSONResponse(
        content=response_data,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

    return response


@app.post("/api/v1/check-urgency")
async def check_urgency(dx: str = Body(..., embed=True)):
    if dx not in KNOWN_DX:
        return JSONResponse(
            content={"error": "Diagnóstico no reconocido"},
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    aply = URGENT_RULE.get(dx, False)

    response = JSONResponse(
        content={"dx": dx, "aplicaLeyUrgencia": aply},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )
    return response
