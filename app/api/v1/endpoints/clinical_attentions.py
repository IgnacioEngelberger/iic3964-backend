# app/api/v1/endpoints/clinical_attentions.py
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query

from app.schemas.clinical_attention import (
    ClinicalAttentionDetailResponse,
    ClinicalAttentionsListResponse,
    CreateClinicalAttentionRequest,
    DeleteClinicalAttentionRequest,
    UpdateClinicalAttentionRequest,
)
from app.services import clinical_attention_service

router = APIRouter()


@router.get(
    "/clinical_attentions",
    response_model=ClinicalAttentionsListResponse,
    tags=["Clinical Attentions"],
)
def get_clinical_attentions(
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(10, description="Tamaño de página", ge=1, le=200),
    search: str
    | None = Query(None, description="Buscar en paciente (RUT, nombre) o diagnóstico"),
    order: str
    | None = Query(None, description="Ordenamiento (ej. -created_at,diagnostic)"),
):
    try:
        attentions_data = clinical_attention_service.list_attentions(
            page=page, page_size=page_size, search=search, order=order
        )
        return attentions_data

    except Exception as e:
        print(f"Error en el endpoint: {e}")
        raise HTTPException(
            status_code=500, detail="Ocurrió un error interno al procesar la solicitud."
        )


@router.get(
    "/clinical_attentions/{attention_id}",
    response_model=ClinicalAttentionDetailResponse,
)
def get_clinical_attention_detail(
    attention_id: UUID,
) -> ClinicalAttentionDetailResponse:
    try:
        detail = clinical_attention_service.get_attention_detail(attention_id)
        return detail
    except LookupError:
        raise HTTPException(status_code=404, detail="Atención clínica no encontrada")
    except Exception as e:
        print(f"Error en el endpoint (detalle): {e}")
        raise HTTPException(status_code=500, detail="Ocurrió un error interno")


@router.post(
    "/clinical_attentions",
    response_model=ClinicalAttentionDetailResponse,
    tags=["Clinical Attentions"],
)
def create_clinical_attention(
    payload: CreateClinicalAttentionRequest,
) -> ClinicalAttentionDetailResponse:
    try:
        created_attention = clinical_attention_service.create_attention(payload)
        return created_attention
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error en el endpoint (create): {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error interno al crear la atención clínica.",
        )


@router.patch(
    "/clinical_attentions/{attention_id}",
    response_model=ClinicalAttentionDetailResponse,
    tags=["Clinical Attentions"],
)
def patch_clinical_attention(
    attention_id: UUID = Path(..., description="ID de la atención clínica"),
    payload: Optional[UpdateClinicalAttentionRequest] = None,
) -> ClinicalAttentionDetailResponse:
    try:
        updated_attention = clinical_attention_service.update_attention(
            attention_id, payload
        )
        return updated_attention
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error en el endpoint (update): {e}")
        raise HTTPException(
            status_code=500, detail="Error interno al actualizar la atención clínica"
        )


@router.delete(
    "/clinical_attentions/{attention_id}", status_code=204, tags=["Clinical Attentions"]
)
def delete_clinical_attention(
    attention_id: UUID, payload: DeleteClinicalAttentionRequest
) -> None:
    try:
        clinical_attention_service.delete_attention(attention_id, payload.deleted_by_id)
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error en el endpoint delete: {e}")
        raise HTTPException(
            status_code=500, detail="Ocurrió un error interno al eliminar"
        )
