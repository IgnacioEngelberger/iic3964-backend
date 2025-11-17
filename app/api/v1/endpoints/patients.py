# app/api/v1/endpoints/patients.py
from fastapi import APIRouter, HTTPException

from app.services import patient_service

router = APIRouter()


@router.get("/patients", tags=["Patients"])
def get_patients():
    """
    Get all patients for form selection.
    Returns a list of patients with id, rut, first_name, last_name, email.
    """
    try:
        patients = patient_service.list_patients()
        return {"patients": patients}
    except Exception as e:
        print(f"Error fetching patients: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener pacientes",
        )