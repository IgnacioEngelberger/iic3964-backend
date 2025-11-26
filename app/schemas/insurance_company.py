from typing import List, Optional

from pydantic import BaseModel


class InsuranceCompanyBase(BaseModel):
    nombre_comercial: Optional[str] = None
    nombre_juridico: str
    rut: Optional[str] = None


class InsuranceCompanyCreateRequest(InsuranceCompanyBase):
    pass


class InsuranceCompanyUpdateRequest(BaseModel):
    nombre_comercial: Optional[str] = None
    nombre_juridico: Optional[str] = None
    rut: Optional[str] = None


class InsuranceCompanyListItem(BaseModel):
    id: int
    nombre_comercial: Optional[str]
    nombre_juridico: str
    rut: Optional[str]


class InsuranceCompanyListResponse(BaseModel):
    count: int
    total: int
    page: int
    page_size: int
    results: List[InsuranceCompanyListItem]


class InsuranceCompanyDetailResponse(BaseModel):
    id: int
    nombre_comercial: Optional[str]
    nombre_juridico: str
    rut: Optional[str]
