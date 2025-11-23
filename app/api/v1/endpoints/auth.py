from fastapi import APIRouter, HTTPException, status
from supabase import AuthApiError

from app.core.supabase_client import supabase
from app.services import doctor_service

from ....models.user import UserAuth, UserCreate

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    """
    Register a new user in Supabase Auth AND the public 'User' table.
    """
    # 1. Validar Rol
    if user_in.role not in ["resident", "supervisor"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    try:
        # 2. Crear en Supabase Auth
        user_options = {
            "data": {
                "first_name": user_in.first,
                "last_name": user_in.last,
                "role": user_in.role,
            }
        }
        auth_response = supabase.auth.sign_up(
            {
                "email": user_in.email,
                "password": user_in.password,
                "options": user_options,
            }
        )

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Auth creation failed")

        # 3. Crear en Tabla Pública "User" (Sincronización)
        # Usamos el ID que nos dio Auth
        new_doctor = doctor_service.create_doctor(
            doctor_id=auth_response.user.id,
            email=user_in.email,
            first_name=user_in.first,
            last_name=user_in.last,
            role=user_in.role,
        )

        return {"user": auth_response.user, "doctor": new_doctor}

    except AuthApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        print(f"Register error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/login")
def login_user(user_in: UserAuth):
    """
    Authenticate a user and return a session.
    """
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": user_in.email, "password": user_in.password}
        )
        return {"session": auth_response.session}
    except AuthApiError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
