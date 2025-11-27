import uuid
from uuid import UUID

from app.core.supabase_client import supabase
from app.schemas.patient import PatientCreate, PatientUpdate


def list_patients() -> list[dict]:
    """
    Fetch all patients from the database.
    Returns a list of patient records.
    """
    try:
        response = (
            supabase.table("Patient")
            .select(
                "id, rut, first_name, last_name,"
                "mother_last_name, aseguradora, age, sex, height, weight"
            )
            .eq("is_deleted", False)
            .order("first_name", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error in list_patients service: {e}")
        raise


def get_patient_by_id(patient_id: UUID) -> dict:
    try:
        response = (
            supabase.table("Patient")
            .select("*")
            .eq("id", str(patient_id))
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error fetching patient: {e}")
        raise


def create_patient(payload: PatientCreate) -> dict:
    """
    Creates a new patient in the database.
    """
    try:
        patient_id = str(uuid.uuid4())
        data = payload.model_dump()
        data["id"] = patient_id
        data["is_deleted"] = False

        response = supabase.table("Patient").insert(data).execute()
        if not response.data:
            raise Exception("No se pudo crear el paciente")

        return response.data[0]
    except Exception as e:
        print(f"Error creating patient: {e}")
        raise


def update_patient(patient_id: UUID, payload: PatientUpdate) -> dict:
    """
    Updates an existing patient.
    """
    try:
        # Filtramos los valores que no sean None para actualizar solo lo enviado
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return get_patient_by_id(patient_id)

        response = (
            supabase.table("Patient")
            .update(update_data)
            .eq("id", str(patient_id))
            .execute()
        )
        if not response.data:
            raise Exception("No se pudo actualizar el paciente")

        return response.data[0]
    except Exception as e:
        print(f"Error updating patient: {e}")
        raise
