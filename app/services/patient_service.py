from app.core.supabase_client import supabase


def list_patients() -> list[dict]:
    """
    Fetch all patients from the database.
    Returns a list of patient records.
    """
    try:
        response = (
            supabase.table("Patient")
            .select("id, rut, first_name, last_name, email")
            .eq("is_deleted", False)
            .order("first_name", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error in list_patients service: {e}")
        raise
