from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr


class PatientInfo(BaseModel):
    rut: str | None
    first_name: str | None
    last_name: str | None


class DoctorInfo(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ClinicalAttentionListItem(BaseModel):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    patient: PatientInfo
    resident_doctor: DoctorInfo
    supervisor_doctor: DoctorInfo
    applies_urgency_law: bool | None
    ai_result: bool | None
    is_overwritten: bool
    ai_confidence: Optional[float] = None

    class Config:
        from_attributes = True


class ClinicalAttentionsListResponse(BaseModel):
    count: int
    total: int
    page: int
    page_size: int
    results: list[ClinicalAttentionListItem]


class _PersonBase(BaseModel):
    id: UUID
    first_name: str
    last_name: str


class DeletedBy(BaseModel):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]


class OverwrittenBy(BaseModel):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]


class PatientDetail(BaseModel):
    id: UUID
    rut: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]


class DoctorDetail(BaseModel):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]


class ClinicalAttentionDetailResponse(BaseModel):
    id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]
    is_deleted: Optional[bool]
    deleted_at: Optional[str]
    deleted_by: Optional[DeletedBy]
    overwritten_by: Optional[OverwrittenBy]
    patient: Optional[PatientDetail]
    resident_doctor: Optional[DoctorDetail]
    supervisor_doctor: Optional[DoctorDetail]
    overwritten_reason: Optional[str]
    ai_result: Optional[bool]
    ai_reason: Optional[str]
    applies_urgency_law: Optional[bool]
    diagnostic: Optional[str]
    ai_confidence: Optional[float]


class NestedPatient(BaseModel):
    rut: str
    first_name: str
    last_name: str
    email: EmailStr


class CreateClinicalAttentionRequest(BaseModel):
    patient_id: Union[UUID, NestedPatient]
    resident_doctor_id: UUID
    supervisor_doctor_id: Optional[UUID] = None
    diagnostic: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "6a6263f1-b13d-4143-84a8-9a74ded10174",
                "resident_doctor_id": "392c3fe1-ee87-4bbb-ae46-d2733a84bf8f",
                "supervisor_doctor_id": ("392c3fe1-ee87-4bbb-ae46-d2733a84bf8f"),
                "diagnostic": (
                    "Paciente consulta por dolor torácico opresivo irradiado a brazo "
                    "izquierdo, acompañado de diaforesis y náuseas de inicio súbito "
                    "hace 25 minutos. Antecedentes de hipertensión."
                ),
            }
        }
    }


class UpdateClinicalAttentionRequest(BaseModel):
    patient: Optional[Union[UUID, NestedPatient]] = None
    resident_doctor_id: Optional[UUID] = None
    supervisor_doctor_id: Optional[UUID] = None
    diagnostic: Optional[str] = None
    is_deleted: Optional[bool] = None


class DeleteClinicalAttentionRequest(BaseModel):
    deleted_by_id: UUID
