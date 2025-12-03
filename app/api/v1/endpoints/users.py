import os

from fastapi import APIRouter, HTTPException, status
from supabase import Client, create_client

from app.services import user_service

from ....models.user import UserUpdate

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@router.get("/", tags=["Users"])
def get_users():
    """
    Returns all system users except patients.
    Groups users by role: resident, supervisor, admin.
    """
    try:
        residents = user_service.list_residents()
        supervisors = user_service.list_supervisors()
        admins = user_service.list_admins()

        return {"resident": residents, "supervisor": supervisors, "admin": admins}

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
    Delete a user from Supabase Auth and from the public User table.
    """

    if not supabase_admin:
        raise HTTPException(
            status_code=500, detail="Server misconfiguration: No Admin Key"
        )

    try:
        # 1. Delete from Supabase Auth
        supabase_admin.auth.admin.delete_user(user_id)

        # 2. Delete from User table (hard delete)
        user_service.delete_user(user_id)

        return {"success": True, "message": "User deleted successfully"}

    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
