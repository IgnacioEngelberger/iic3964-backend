from app.core.supabase_client import supabase


def list_resident_doctors() -> list[dict]:
    """
    Fetch all resident doctors from the database.
    Returns a list of doctor records.
    """
    try:
        response = (
            supabase.table("User")
            .select("id, first_name, last_name, email, phone")
            .eq("role", "Resident")
            .eq("is_deleted", False)
            .order("first_name", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error in list_resident_doctors service: {e}")
        raise


def list_supervisor_doctors() -> list[dict]:
    """
    Fetch all supervisor doctors from the database.
    Returns a list of doctor records.
    """
    try:
        response = (
            supabase.table("User")
            .select("id, first_name, last_name, email, phone")
            .eq("role", "Supervisor")
            .eq("is_deleted", False)
            .order("first_name", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error in list_supervisor_doctors service: {e}")
        raise


def create_doctor(
    doctor_id: str, email: str, first_name: str, last_name: str, role: str
) -> dict:
    """
    Creates a new doctor record in the 'User' table.
    Used during the registration process to sync Auth with public data.
    """
    try:
        # Normalizar el rol para que coincida con la BD (resident -> Resident)
        role_mapping = {
            "resident": "Resident",
            "supervisor": "Supervisor",
            "admin": "Admin",
        }
        db_role = role_mapping.get(
            role.lower(), "Resident"
        )  # Default a Resident por seguridad

        payload = {
            "id": doctor_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": db_role,
            "is_deleted": False,
        }

        response = supabase.table("User").insert(payload).execute()

        if not response.data:
            raise Exception("No se pudo insertar el doctor en la tabla User")

        return response.data[0]
    except Exception as e:
        print(f"Error in create_doctor service: {e}")
        raise
