import uuid
from uuid import UUID

from app.core.supabase_client import supabase
from app.schemas.patient import PatientCreate, PatientUpdate


def list_patients(
    page: int = 1, page_size: int = 10, search: str | None = None
) -> dict:
    """
    Fetch all patients including insurance company info with pagination and search.
    Returns: {results: list[dict], total: int}
    """
    try:
        # Build base query with count
        query = (
            supabase.table("Patient")
            .select(
                "id, rut, first_name, last_name, mother_last_name, age, sex,"
                " height, weight, insurance_company_id,"
                "insurance_company:"
                "insurance_company(id, nombre_juridico, nombre_comercial, rut)",
                count="exact",
            )
            .eq("is_deleted", False)
        )

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            # Search in first_name, last_name, mother_last_name, or rut
            query = query.or_(
                f"first_name.ilike.%{search_lower}%,"
                f"last_name.ilike.%{search_lower}%,"
                f"mother_last_name.ilike.%{search_lower}%,"
                f"rut.ilike.%{search_lower}%"
            )

        # Get total count before pagination
        count_response = query.execute()
        total = count_response.count if count_response.count is not None else 0

        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size - 1

        # Execute query with pagination
        response = query.order("first_name", desc=False).range(start, end).execute()

        patients = response.data or []

        # Get episodes count for each patient
        for patient in patients:
            try:
                # Count clinical attentions where is_deleted is False OR NULL
                # (NULL means the record was created before is_deleted column was added)
                episodes_response = (
                    supabase.table("ClinicalAttention")
                    .select("id", count="exact")
                    .eq("patient_id", str(patient["id"]))
                    .or_("is_deleted.is.null,is_deleted.eq.false")
                    .execute()
                )
                count = episodes_response.count if episodes_response.count is not None else 0
                patient["episodes_count"] = count
            except Exception as e:
                print(f"Error counting episodes for patient {patient['id']}: {e}")
                import traceback
                traceback.print_exc()
                patient["episodes_count"] = 0

        return {"results": patients, "total": total}
    except Exception as e:
        print(f"Error in list_patients service: {e}")
        raise


def get_patient_by_id(patient_id: UUID) -> dict:
    try:
        response = (
            supabase.table("Patient")
            .select(
                "id, rut, first_name, last_name, mother_last_name, "
                "insurance_company_id,age, sex, height, weight,"
                "insurance_company:"
                "insurance_company(id, nombre_juridico, nombre_comercial, rut)"
            )
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

        data.pop("insurance_company", None)

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
        update_data.pop("insurance_company", None)

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
