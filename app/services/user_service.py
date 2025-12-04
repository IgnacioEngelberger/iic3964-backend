from typing import Any, Dict, Optional

from app.core.supabase_client import supabase
from app.schemas.user import UserListItem, UserListResponse


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


def _denormalize_role(role: str) -> str:
    """Map DB enum values to frontend roles (lowercase)."""
    role_mapping = {
        "Resident": "resident",
        "Supervisor": "supervisor",
        "Admin": "admin",
    }
    return role_mapping.get(role, role.lower())


def list_all_users(page: int, page_size: int, search: str | None = None) -> UserListResponse:
    """
    List all users (all roles) with pagination and optional search.
    Returns users sorted by:
    1. Active status (active first)
    2. Role (Admin, Supervisor, Resident)
    3. First name

    Search filters by name (first_name + last_name) or email.
    """
    try:
        # Fetch all users sorted by is_deleted and first_name
        # We'll do role sorting in Python since PostgREST doesn't support CASE in ORDER BY
        all_users_query = (
            supabase.table("User")
            .select("id, first_name, last_name, email, phone, role, is_deleted")
            .order("is_deleted", desc=False)  # Active users first
            .order("first_name", desc=False)  # Then by name
            .execute()
        )
        all_data = all_users_query.data or []

        # Apply search filter if provided
        if search:
            search_lower = search.lower().strip()
            all_data = [
                u for u in all_data
                if (
                    search_lower in f"{u['first_name']} {u['last_name']}".lower()
                    or (u.get('email') and search_lower in u['email'].lower())
                )
            ]

        # Define role priority for sorting
        role_priority = {"Admin": 1, "Supervisor": 2, "Resident": 3}

        # Sort with role priority
        sorted_data = sorted(
            all_data,
            key=lambda u: (
                u.get("is_deleted", False),  # Active first (False < True)
                role_priority.get(u["role"], 999),  # Admin, Supervisor, Resident
                u["first_name"].lower(),  # Then by name
            ),
        )

        # Apply pagination
        offset = (page - 1) * page_size
        data = sorted_data[offset : offset + page_size]
        total_count = len(sorted_data)

        # Map results to schema with normalized roles
        results_list = [
            UserListItem(
                id=item["id"],
                first_name=item["first_name"],
                last_name=item["last_name"],
                email=item.get("email"),
                phone=item.get("phone"),
                role=_denormalize_role(item["role"]),
                is_deleted=item.get("is_deleted", False),
            )
            for item in data
        ]

        return UserListResponse(
            count=total_count,
            total=total_count,
            page=page,
            page_size=page_size,
            results=results_list,
        )

    except Exception as e:
        print(f"Error in list_all_users service: {e}")
        raise
