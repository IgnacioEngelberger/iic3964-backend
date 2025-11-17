from fastapi import APIRouter, HTTPException, status
from supabase import AuthApiError

from ....models.user import (UserAuth, UserCreate)

from app.core.supabase_client import supabase

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    """
    Register a new user in Supabase.
    User metadata (first, last) is included in the options.
    """
    try:
        user_options = {
            "data": {
                "first_name": user_in.first,
                "last_name": user_in.last
            }
        }
        auth_response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
            "options": user_options
        })
        return {"user": auth_response.user}
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login")
def login_user(user_in: UserAuth):
    """
    Authenticate a user and return a session.
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_in.email,
            "password": user_in.password
        })
        return {"session": auth_response.session}
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
