from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Query, HTTPException

from app.schemas.metric import MetricStats
from app.services import metric_service

router = APIRouter()

@router.get("/users", response_model=List[MetricStats], tags=["Metrics"])
def get_users_metrics(
    start_date: Optional[str] = Query(None, description="Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format YYYY-MM-DD")
):
    """
    Obtiene métricas de todos los usuarios (médicos residentes) que han tenido actividad.
    """
    try:
        return metric_service.get_all_users_metrics(start_date, end_date)
    except Exception as e:
        print(f"Error fetching users metrics: {e}")
        raise HTTPException(status_code=500, detail="Error calculando métricas de usuarios")

@router.get("/users/{user_id}", response_model=MetricStats, tags=["Metrics"])
def get_user_metrics(
    user_id: UUID,
    start_date: Optional[str] = Query(None, description="Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format YYYY-MM-DD")
):
    """
    Obtiene métricas para un usuario específico.
    """
    try:
        return metric_service.get_single_user_metrics(str(user_id), start_date, end_date)
    except Exception as e:
        print(f"Error fetching user metrics: {e}")
        raise HTTPException(status_code=500, detail="Error calculando métricas del usuario")

@router.get("/insurance_companies/{company_id}", response_model=MetricStats, tags=["Metrics"])
def get_insurance_metrics(
    company_id: int,
    start_date: Optional[str] = Query(None, description="Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format YYYY-MM-DD")
):
    """
    Obtiene métricas para una aseguradora específica.
    """
    try:
        return metric_service.get_insurance_metrics(company_id, start_date, end_date)
    except Exception as e:
        print(f"Error fetching insurance metrics: {e}")
        raise HTTPException(status_code=500, detail="Error calculando métricas de aseguradora")
