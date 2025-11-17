"""
Service layer for doctor-related operations.
"""
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
