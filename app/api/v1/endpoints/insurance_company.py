from fastapi import APIRouter, Query

from app.schemas.insurance_company import (
    InsuranceCompanyCreateRequest,
    InsuranceCompanyDetailResponse,
    InsuranceCompanyListResponse,
    InsuranceCompanyUpdateRequest,
)
from app.services import insurance_company_service

router = APIRouter()


@router.get(
    "",
    response_model=InsuranceCompanyListResponse,
    tags=["Insurance Companies"],
)
def list_insurance_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    search: str | None = Query(None),
    order: str | None = Query(None),
):
    return insurance_company_service.list_companies(
        page=page, page_size=page_size, search=search, order=order
    )


@router.get(
    "/{company_id}",
    response_model=InsuranceCompanyDetailResponse,
    tags=["Insurance Companies"],
)
def get_insurance_company(company_id: int):
    return insurance_company_service.get_company(company_id)


@router.post(
    "",
    response_model=InsuranceCompanyDetailResponse,
    tags=["Insurance Companies"],
)
def create_insurance_company(payload: InsuranceCompanyCreateRequest):
    return insurance_company_service.create_company(payload)


@router.patch(
    "/{company_id}",
    response_model=InsuranceCompanyDetailResponse,
    tags=["Insurance Companies"],
)
def update_insurance_company(
    company_id: int,
    payload: InsuranceCompanyUpdateRequest,
):
    return insurance_company_service.update_company(company_id, payload)


@router.delete(
    "/{company_id}",
    status_code=204,
    tags=["Insurance Companies"],
)
def delete_insurance_company(company_id: int):
    insurance_company_service.delete_company(company_id)
    return None
