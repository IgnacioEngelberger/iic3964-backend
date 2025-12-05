from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .insurance_company import InsuranceCompanyBase


class PatientBase(BaseModel):
    rut: str
    first_name: str = Field(..., description="Nombre")
    last_name: str = Field(..., description="Apellido Paterno")
    mother_last_name: Optional[str] = Field(None, description="Apellido Materno")
    age: Optional[int] = None
    sex: Optional[str] = Field(None, description="M, F, u Otro")
    height: Optional[float] = Field(None, description="Altura en cm o metros")
    weight: Optional[float] = Field(None, description="Peso en kg")
    insurance_company_id: Optional[int] = Field(
        None, description="ID de la aseguradora"
    )
    insurance_company: Optional[InsuranceCompanyBase] = None


class PatientCreate(PatientBase):
    rut: str
    first_name: str = Field(..., description="Nombre")
    last_name: str = Field(..., description="Apellido Paterno")
    mother_last_name: Optional[str] = Field(None, description="Apellido Materno")
    age: Optional[int] = None
    sex: Optional[str] = Field(None, description="M, F, u Otro")
    height: Optional[float] = Field(None, description="Altura en cm o metros")
    weight: Optional[float] = Field(None, description="Peso en kg")
    insurance_company_id: Optional[int] = Field(
        None, description="ID de la aseguradora"
    )


class PatientUpdate(BaseModel):
    rut: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mother_last_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    insurance_company_id: Optional[int] = None


class PatientResponse(PatientBase):
    id: UUID
    insurance_company_id: int | None = None
    insurance_company: InsuranceCompanyBase | None = None
    is_deleted: bool = False

    model_config = ConfigDict(from_attributes=True)
