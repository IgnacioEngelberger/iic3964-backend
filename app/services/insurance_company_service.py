from fastapi import HTTPException
from app.core.supabase_client import supabase

from app.schemas.insurance_company import (
    InsuranceCompanyDetailResponse,
    InsuranceCompanyListItem,
    InsuranceCompanyListResponse,
    InsuranceCompanyCreateRequest,
    InsuranceCompanyUpdateRequest,
)


def list_companies(page: int, page_size: int, search: str | None, order: str | None):
    offset = (page - 1) * page_size
    to = offset + page_size - 1

    query = supabase.table("insurance_company").select("*")

    # --- SEARCH ---
    if search:
        query = query.filter(
            f"or(nombre_comercial.ilike.%{search}%,"
            f"nombre_juridico.ilike.%{search}%,"
            f"rut.ilike.%{search}%)"
        )

    # --- ORDER ---
    if order:
        fields = order.split(",")
        for f in fields:
            col = f.lstrip("-")
            asc = not f.startswith("-")
            query = query.order(col, desc=not asc)
    else:
        query = query.order("nombre_juridico", desc=False)

    query = query.range(offset, to)
    result = query.execute()
    data = result.data or []

    # Count
    count_query = supabase.table("insurance_company").select("id", count="exact")
    if search:
        count_query = count_query.filter(
            f"or(nombre_comercial.ilike.%{search}%,"
            f"nombre_juridico.ilike.%{search}%,"
            f"rut.ilike.%{search}%)"
        )
    count_result = count_query.execute()

    results_list = [
        InsuranceCompanyListItem(
            id=item["id"],
            nombre_comercial=item.get("nombre_comercial"),
            nombre_juridico=item["nombre_juridico"],
            rut=item.get("rut"),
        )
        for item in data
    ]

    return InsuranceCompanyListResponse(
        count=count_result.count or len(data),
        total=count_result.count or len(data),
        page=page,
        page_size=page_size,
        results=results_list,
    )


def get_company(company_id: int) -> InsuranceCompanyDetailResponse:
    result = (
        supabase.table("insurance_company")
        .select("*")
        .eq("id", company_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")

    item = result.data[0]

    return InsuranceCompanyDetailResponse(
        id=item["id"],
        nombre_comercial=item.get("nombre_comercial"),
        nombre_juridico=item["nombre_juridico"],
        rut=item.get("rut"),
    )


def create_company(payload: InsuranceCompanyCreateRequest):
    insert_result = (
        supabase.table("insurance_company")
        .insert(
            {
                "nombre_comercial": payload.nombre_comercial,
                "nombre_juridico": payload.nombre_juridico,
                "rut": payload.rut,
            }
        )
        .execute()
    )

    if not insert_result.data:
        raise HTTPException(status_code=400, detail="Error al crear la compañía")

    new_id = insert_result.data[0]["id"]
    return get_company(new_id)


def update_company(company_id: int, payload: InsuranceCompanyUpdateRequest):
    update_data = {
        k: v for k, v in payload.model_dump(exclude_unset=True).items()
    }

    if not update_data:
        return get_company(company_id)

    result = (
        supabase.table("insurance_company")
        .update(update_data)
        .eq("id", company_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=400, detail="No se pudo actualizar")

    return get_company(company_id)


def delete_company(company_id: int):
    result = (
        supabase.table("insurance_company")
        .delete()
        .eq("id", company_id)
        .execute()
    )

    if result.data is None:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")

    return None
