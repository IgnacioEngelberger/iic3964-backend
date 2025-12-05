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
    CloseEpisodeRequest,
    CreateClinicalAttentionRequest,
    DeleteClinicalAttentionRequest,
    MedicApprovalRequest,
    ReopenEpisodeRequest,
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
    patient_search: str
    | None = Query(None, description="Buscar por paciente (nombre o RUT)"),
    doctor_search: str | None = Query(None, description="Buscar por médico (nombre)"),
    medic_approved: str
    | None = Query(
        None, description="Estado validación residente: pending, approved, rejected"
    ),
    supervisor_approved: str
    | None = Query(
        None, description="Estado validación supervisor: pending, approved, rejected"
    ),
    current_user_id: str
    | None = Query(None, description="ID del usuario actual para filtrar por rol"),
):
    try:
        attentions_data = clinical_attention_service.list_attentions(
            page=page,
            page_size=page_size,
            search=search,
            order=order,
            patient_search=patient_search,
            doctor_search=doctor_search,
            medic_approved=medic_approved,
            supervisor_approved=supervisor_approved,
            current_user_id=current_user_id,
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
        import traceback

        error_traceback = traceback.format_exc()
        print(f"Error import_insurance_excel: {str(e)}")
        print(f"Traceback: {error_traceback}")
        error_msg = str(e) if str(e) else "Error desconocido"
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando archivo: {error_msg}",
        )


@router.post("/clinical_attentions/history", tags=["Clinical Attentions"])
def get_clinical_attention_history(payload: dict):
    """
    Get clinical attention history for given patient IDs.
    Expects: {"patient_ids": ["uuid1", "uuid2", ...]}
    Returns: {"patients": [{"patient_id": "uuid", "attentions": [...]}]}
    """
    try:
        from app.core.supabase_client import supabase

        patient_ids = payload.get("patient_ids", [])
        if not patient_ids:
            return {"patients": []}

        def _compute_urgency_law(ai_result, medic_approved, supervisor_approved):
            """Compute urgency law based on AI result and approvals."""
            if ai_result is None:
                return None

            does_urgency_law_apply = ai_result

            if medic_approved is None:
                does_urgency_law_apply = None
            else:
                does_urgency_law_apply = ai_result if medic_approved else not ai_result

                if supervisor_approved is False:
                    does_urgency_law_apply = not does_urgency_law_apply

            return does_urgency_law_apply

        result_patients = []

        for patient_id in patient_ids:
            # Get clinical attentions for this patient
            response = (
                supabase.table("ClinicalAttention")
                .select(
                    "id, id_episodio, created_at, diagnostic, "
                    "ai_result, medic_approved, "
                    "supervisor_approved, pertinencia, is_closed, closed_at, "
                    "resident_doctor:resident_doctor_id(first_name, last_name), "
                    "supervisor_doctor:supervisor_doctor_id(first_name, last_name), "
                    "closed_by:closed_by_id(first_name, last_name)"
                )
                .eq("patient_id", str(patient_id))
                .or_("is_deleted.is.null,is_deleted.eq.false")
                .order("created_at", desc=True)
                .execute()
            )

            attentions = response.data or []

            # Format the response
            formatted_attentions = []
            for attention in attentions:
                # Compute urgency law for this attention
                computed_urgency_law = _compute_urgency_law(
                    ai_result=attention.get("ai_result"),
                    medic_approved=attention.get("medic_approved"),
                    supervisor_approved=attention.get("supervisor_approved"),
                )

                formatted_attentions.append(
                    {
                        "id": attention["id"],
                        "id_episodio": attention.get("id_episodio"),
                        "created_at": attention.get("created_at"),
                        "diagnostic": attention.get("diagnostic"),
                        "applies_urgency_law": computed_urgency_law,
                        "ai_result": attention.get("ai_result"),
                        "medic_approved": attention.get("medic_approved"),
                        "supervisor_approved": attention.get("supervisor_approved"),
                        "pertinencia": attention.get("pertinencia"),
                        "is_closed": attention.get("is_closed"),
                        "closed_at": attention.get("closed_at"),
                        "resident_doctor_name": (
                            f"{attention['resident_doctor']['first_name']} "
                            f"{attention['resident_doctor']['last_name']}"
                            if attention.get("resident_doctor")
                            else None
                        ),
                        "supervisor_doctor_name": (
                            f"{attention['supervisor_doctor']['first_name']} "
                            f"{attention['supervisor_doctor']['last_name']}"
                            if attention.get("supervisor_doctor")
                            else None
                        ),
                        "closed_by_name": (
                            f"{attention['closed_by']['first_name']} "
                            f"{attention['closed_by']['last_name']}"
                            if attention.get("closed_by")
                            else None
                        ),
                    }
                )

            result_patients.append(
                {"patient_id": str(patient_id), "attentions": formatted_attentions}
            )

        return {"patients": result_patients}

    except Exception as e:
        import traceback

        error_traceback = traceback.format_exc()
        print(f"Error get_clinical_attention_history: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=500, detail=f"Error getting clinical history: {str(e)}"
        )


@router.post("/clinical_attentions/{attention_id}/close", tags=["Clinical Attentions"])
def close_episode(attention_id: UUID, payload: CloseEpisodeRequest):
    """
    Close a clinical attention episode.
    Can be called by resident, supervisor, or admin.
    Requires closing_reason: Muerte, Hospitalización, Alta, or Traslado.
    """
    try:
        result = clinical_attention_service.close_episode(
            attention_id=attention_id,
            closed_by_id=payload.closed_by_id,
            closing_reason=payload.closing_reason,
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error close_episode endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/clinical_attentions/{attention_id}/reopen", tags=["Clinical Attentions"])
def reopen_episode(attention_id: UUID, payload: ReopenEpisodeRequest):
    """
    Reopen a closed clinical attention episode.
    Can only be called by admin.
    """
    try:
        result = clinical_attention_service.reopen_episode(
            attention_id=attention_id, reopened_by_id=payload.reopened_by_id
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error reopen_episode endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
