import json
from typing import List, Optional, Union

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "IIC3964 Backend"
    VERSION: str = "1.0.0"

    # CORS (important: Union[str, List[AnyHttpUrl]])
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ""

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if not v:
            return []

        # JSON-style list e.g. ["http://localhost:3000"]
        if isinstance(v, str) and v.strip().startswith("["):
            try:
                return json.loads(v)
            except Exception as e:
                raise ValueError(f"Invalid JSON for BACKEND_CORS_ORIGINS: {v}") from e

        # Comma-separated string
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]

        # Already a list
        if isinstance(v, list):
            return v

        raise ValueError(v)

    DATABASE_URL: str = "sqlite:///./app.db"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    ENVIRONMENT: str = "development"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
