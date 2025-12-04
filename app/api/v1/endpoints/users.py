import os

from fastapi import APIRouter, HTTPException, Query, status
from supabase import Client, create_client

from app.schemas.user import UserListResponse
from app.services import user_service

from ....models.user import UserUpdate

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@router.get("/", response_model=UserListResponse, tags=["Users"])
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    search: str | None = Query(None),
):
    """
    Returns all system users with pagination and optional search.
    Users are sorted by active status first, then by role, then by first name.
    Search filters by name (first_name + last_name) or email.
    """
    try:
        return user_service.list_all_users(page=page, page_size=page_size, search=search)

    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener usuarios",
        )


@router.patch("/{user_id}", tags=["Users"])
def update_user_endpoint(user_id: str, user_in: UserUpdate):
    try:
        # 1. Update Supabase Auth metadata + email/pass
        auth_attributes = {}

        if user_in.email:
            auth_attributes["email"] = user_in.email
        if user_in.password and user_in.password.strip():
            auth_attributes["password"] = user_in.password

        if any([user_in.first_name, user_in.last_name, user_in.role]):
            auth_attributes["data"] = {
                "first_name": user_in.first_name,
                "last_name": user_in.last_name,
                "role": user_in.role,
            }

        if auth_attributes:
            supabase_admin.auth.admin.update_user_by_id(user_id, auth_attributes)

        # 2. Update public User table
        updated_user = user_service.update_user(
            user_id=user_id,
            email=user_in.email,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            role=user_in.role,
        )

        return {"success": True, "data": updated_user}

    except Exception as e:
        print(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", tags=["Users"])
def delete_user(user_id: str):
    """
    Deactivates (Soft Delete) a user.
    Prevents login by banning the user in Auth and setting is_deleted=True in DB.
    """
    if not supabase_admin:
        raise HTTPException(
            status_code=500, detail="Server misconfiguration: No Admin Key"
        )

    try:
        # 1. Ban user in Supabase Auth
        # This prevents login instantly.
        supabase_admin.auth.admin.update_user_by_id(
            user_id, {"ban_duration": "876600h"}  # ~100 years
        )

        # 2. Soft Delete in Public Table
        user_service.delete_user(user_id)

        return {"success": True, "message": "User deactivated successfully"}

    except Exception as e:
        print(f"Deactivation error: {e}")
        # If user not found in Auth (already gone), ensures DB is updated at least
        if "User not found" in str(e):
            user_service.delete_user(user_id)
            return {"success": True, "message": "User deactivated (DB only)"}

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/{user_id}/reactivate", tags=["Users"])
def reactivate_user(user_id: str):
    """
    Reactivates a user.
    Removes the Auth Ban and sets is_deleted=False in DB.
    """
    if not supabase_admin:
        raise HTTPException(
            status_code=500, detail="Server misconfiguration: No Admin Key"
        )

    try:
        # 1. Unban user in Supabase Auth
        supabase_admin.auth.admin.update_user_by_id(user_id, {"ban_duration": "0"})

        # 2. Reactivate in Public Table
        user_service.reactivate_user(user_id)

        return {"success": True, "message": "User reactivated successfully"}

    except Exception as e:
        print(f"Reactivation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
