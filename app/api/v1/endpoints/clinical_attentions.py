# app/api/v1/endpoints/clinical_attentions.py
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
)

from app.schemas.clinical_attention import (
    ClinicalAttentionDetailResponse,
    ClinicalAttentionsListResponse,
    CreateClinicalAttentionRequest,
    DeleteClinicalAttentionRequest,
    MedicApprovalRequest,
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
def get_clinical_attention_detail(attention_id: UUID):
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
    background_tasks: BackgroundTasks,
) -> ClinicalAttentionDetailResponse:
    try:
        created_attention = clinical_attention_service.create_attention(
            payload, background_tasks
        )
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
    background_tasks: BackgroundTasks,
    attention_id: UUID = Path(..., description="ID de la atención clínica"),
    payload: UpdateClinicalAttentionRequest = None,
):
    try:
        FAKE_EDITOR_ID = "392c3fe1-ee87-4bbb-ae46-d2733a84bf8f"
        updated_attention = clinical_attention_service.update_attention(
            attention_id, payload, background_tasks, editor_id=FAKE_EDITOR_ID
        )
        return updated_attention
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error en el endpoint (update): {e}")
        raise HTTPException(
            status_code=500, detail="Error interno al actualizar la atención clínica"
        )


@router.patch(
    "/clinical_attentions/{attention_id}/medic_approval",
    response_model=ClinicalAttentionDetailResponse,
    tags=["Clinical Attentions"],
)
def medic_approval(
    attention_id: UUID,
    payload: MedicApprovalRequest,
):
    try:
        updated = clinical_attention_service.medic_approval(
            attention_id=attention_id,
            medic_id=payload.medic_id,
            approved=payload.approved,
            reason=payload.reason,
        )
        return updated

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error medic_approval endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.delete(
    "/clinical_attentions/{attention_id}", status_code=204, tags=["Clinical Attentions"]
)
def delete_clinical_attention(
    attention_id: UUID, payload: DeleteClinicalAttentionRequest
):
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


# app/api/v1/endpoints/clinical_attentions.py


@router.post(
    "/clinical_attentions/import_insurance_excel", tags=["Clinical Attentions"]
)
def import_insurance_excel(
    insurance_company_id: int = Query(
        ..., description="ID de la aseguradora dueña del archivo"
    ),
    file: UploadFile = File(...),
):
    try:
        updated = clinical_attention_service.import_insurance_excel(
            insurance_company_id=insurance_company_id, file=file
        )
        return {"updated": updated, "message": "Archivo procesado correctamente"}
    except Exception as e:
        print(f"Error import_insurance_excel: {e}")
        raise HTTPException(status_code=500, detail="Error procesando archivo")
