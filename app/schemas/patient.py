from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PatientBase(BaseModel):
    rut: str
    first_name: str = Field(..., description="Nombre")
    last_name: str = Field(..., description="Apellido Paterno")
    mother_last_name: Optional[str] = Field(None, description="Apellido Materno")
    age: Optional[int] = None
    sex: Optional[str] = Field(None, description="M, F, u Otro")
    height: Optional[float] = Field(None, description="Altura en cm o metros")
    weight: Optional[float] = Field(None, description="Peso en kg")
    aseguradora: Optional[str] = Field(
        None, description="Aseguradora (Fonasa, Isapre, etc)"
    )
    email: Optional[EmailStr] = None


class arPatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    rut: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mother_last_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    aseguradora: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientResponse(PatientBase):
    id: UUID
    is_deleted: bool = False

    class Config:
        from_attributes = True
