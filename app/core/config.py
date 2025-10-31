from typing import List, Union, Optional

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "IIC3964 Backend"
    VERSION: str = "1.0.0"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Environment
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Gemini / Google GenAI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
