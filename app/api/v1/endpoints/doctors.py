# app/api/v1/endpoints/doctors.py
from fastapi import APIRouter, HTTPException

from app.services import doctor_service

router = APIRouter()


@router.get("/resident-doctors", tags=["Doctors"])
def get_resident_doctors():
    """
    Get all resident doctors for form selection.
    Returns a list of doctors with id, first_name, last_name, email, phone.
    """
    try:
        doctors = doctor_service.list_resident_doctors()
        return {"doctors": doctors}
    except Exception as e:
        print(f"Error fetching resident doctors: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener médicos residentes",
        )


@router.get("/supervisor-doctors", tags=["Doctors"])
def get_supervisor_doctors():
    """
    Get all supervisor doctors for form selection.
    Returns a list of doctors with id, first_name, last_name, email, phone.
    """
    try:
        doctors = doctor_service.list_supervisor_doctors()
        return {"doctors": doctors}
    except Exception as e:
        print(f"Error fetching supervisor doctors: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener médicos supervisores",
        )


@router.get("/get-doctors", tags=["Doctors"])
def get_doctors():
    """
    Get all doctors for form selection.
    Returns a list of doctors with id, first_name, last_name, email, phone.
    """
    try:
        resident_doctors = doctor_service.list_resident_doctors()
        supervisor_doctors = doctor_service.list_supervisor_doctors()
        return {"resident": resident_doctors, "supervisor": supervisor_doctors}
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener médicos",
        )
