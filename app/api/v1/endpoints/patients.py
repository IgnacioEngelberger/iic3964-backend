# app/api/v1/endpoints/patients.py
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.schemas.patient import PatientCreate, PatientUpdate
from app.services import patient_service

router = APIRouter()


@router.get("/patients", tags=["Patients"])
def get_patients(
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(10, description="Tamaño de página", ge=1),
    search: str | None = Query(None, description="Buscar en nombre o RUT"),
):
    """
    Get patients with pagination and search.
    Returns paginated list of patients with insurance company info and episodes count.
    """
    try:
        patients_data = patient_service.list_patients(
            page=page, page_size=page_size, search=search
        )
        return patients_data
    except Exception as e:
        print(f"Error fetching patients: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener pacientes",
        )


@router.get("/patients/{patient_id}", tags=["Patients"])
def get_patient(patient_id: UUID):
    """
    Get a specific patient by ID.
    """
    try:
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patients", tags=["Patients"])
def create_patient(patient: PatientCreate):
    """
    Create a new patient.
    """
    try:
        new_patient = patient_service.create_patient(patient)
        return new_patient
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al crear paciente: {str(e)}"
        )


@router.patch("/patients/{patient_id}", tags=["Patients"])
def update_patient(patient_id: UUID, patient_update: PatientUpdate):
    """
    Update patient details.
    """
    try:
        updated_patient = patient_service.update_patient(patient_id, patient_update)
        return updated_patient
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar paciente: {str(e)}"
        )
