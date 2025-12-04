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

        if email:
            payload["email"] = email
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if role:
            payload["role"] = _normalize_role(role)

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
    Soft deletes a user (is_deleted = True).
    Used to be a hard delete, now deactivates.
    """
    try:
        # Changed from .delete() to .update()
        response = (
            supabase.table("User")
            .update({"is_deleted": True})
            .eq("id", user_id)
            .execute()
        )

        if not response.data:
            raise Exception(f"User with ID {user_id} not found or delete failed")

        return True

    except Exception as e:
        print(f"Error in delete_user (soft) service: {e}")
        raise


def reactivate_user(user_id: str) -> bool:
    """
    Reactivates a user (is_deleted = False).
    """
    try:
        response = (
            supabase.table("User")
            .update({"is_deleted": False})
            .eq("id", user_id)
            .execute()
        )

        if not response.data:
            raise Exception(f"User with ID {user_id} not found or reactivation failed")

        return True

    except Exception as e:
        print(f"Error in reactivate_user service: {e}")
        raise


def list_users_by_role(role: str) -> list[dict]:
    """
    Generic function to list users of a specific role.
    Now includes deleted users, sorted by active status first.
    """
    try:
        response = (
            supabase.table("User")
            .select("id, first_name, last_name, email, phone, role, is_deleted")
            .eq("role", role)
            # Removed .eq("is_deleted", False) to show all
            .order(
                "is_deleted", desc=False
            )  # False (Active) first, True (Deleted) last
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
