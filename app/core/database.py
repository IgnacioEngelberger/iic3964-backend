from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Create database engine
if settings.ENVIRONMENT == "production" and settings.SUPABASE_URL:
    # Use Supabase for production
    engine = create_engine(settings.SUPABASE_URL)
else:
    # Use local database for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
        if "sqlite" in settings.DATABASE_URL
        else {},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
