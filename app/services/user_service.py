from typing import Any, Dict, Optional

from app.core.supabase_client import supabase


def _normalize_role(role: str) -> str:
    """Map frontend roles to DB enum values."""
    role_mapping = {
        "resident": "Resident",
        "supervisor": "Supervisor",
        "admin": "Admin",
    }
    return role_mapping.get(role.lower(), role)


def update_user(
    user_id: str,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Updates a user in the User table.
    """
    try:
        payload = {}

        # Same behavior as update_doctor
        if email:
            payload["email"] = email
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if role:
            payload["role"] = _normalize_role(role)

        # If nothing to update, return empty
        if not payload:
            return {}

        response = supabase.table("User").update(payload).eq("id", user_id).execute()

        if not response.data:
            raise Exception(f"User with ID {user_id} not found or update failed")

        return response.data[0]

    except Exception as e:
        print(f"Error in update_user service: {e}")
        raise


def delete_user(user_id: str) -> bool:
    """
    Permanently deletes a user from the 'User' table.
    (Not a soft delete)
    """
    try:
        response = supabase.table("User").delete().eq("id", user_id).execute()

        if not response.data:
            raise Exception(f"User with ID {user_id} not found or delete failed")

        return True

    except Exception as e:
        print(f"Error in delete_user service: {e}")
        raise


def list_users_by_role(role: str) -> list[dict]:
    """
    Generic function to list users of a specific role.
    """
    try:
        response = (
            supabase.table("User")
            .select("id, first_name, last_name, email, phone, role")
            .eq("role", role)
            .eq("is_deleted", False)
            .order("first_name", desc=False)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error in list_users_by_role service: {e}")
        raise


def list_residents() -> list[dict]:
    return list_users_by_role("Resident")


def list_supervisors() -> list[dict]:
    return list_users_by_role("Supervisor")


def list_admins() -> list[dict]:
    return list_users_by_role("Admin")
