import uuid
from datetime import datetime
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException

from app.core.supabase_client import supabase
from app.schemas.clinical_attention import (
    ClinicalAttentionDetailResponse,
    ClinicalAttentionListItem,
    CreateClinicalAttentionRequest,
    DeletedBy,
    DoctorDetail,
    DoctorInfo,
    OverwrittenBy,
    PatientDetail,
    PatientInfo,
    UpdateClinicalAttentionRequest,
)
from app.services.IA.ai_task import run_ai_reasoning_task


def list_attentions(
    page: int, page_size: int, search: str | None, order: str | None
) -> dict:
    try:
        select_query = (
            "id, created_at, updated_at, applies_urgency_law, ai_result, "
            "diagnostic, overwritten_by_id, "
            "patient:patient_id(rut, first_name, last_name), "
            "resident_doctor:resident_doctor_id(first_name, last_name), "
            "supervisor_doctor:supervisor_doctor_id(first_name, last_name)"
        )

        query = supabase.table("ClinicalAttention").select(select_query)

        search_filter = None
        if search:
            search_filter = (
                f"diagnostic.ilike.%{search}%,"
                f"Patient!patient_id.rut.ilike.%{search}%,"
                f"Patient!patient_id.first_name.ilike.%{search}%,"
                f"Patient!patient_id.last_name.ilike.%{search}%"
            )
            query = query.filter(f"or({search_filter})")

        if order:
            order_fields = order.split(",")
            for field in order_fields:
                col_name = field.lstrip("-")
                ascending = not field.startswith("-")
                if "." not in col_name:
                    query = query.order(col_name, desc=not ascending)
        else:
            query = query.order("created_at", desc=True)

        offset = (page - 1) * page_size
        to = offset + page_size - 1
        query = query.range(offset, to)

        response = query.execute()
        data = response.data or []

        count_query = supabase.table("ClinicalAttention").select("id", count="exact")
        count_query = count_query.eq("is_deleted", False)
        if search_filter:
            count_query = count_query.filter(f"or({search_filter})")
        count_response = count_query.execute()
        total_count = count_response.count or len(data)

        total_global_query = supabase.table("ClinicalAttention").select(
            "id", count="exact"
        )
        total_global_response = total_global_query.execute()
        total_global_count = total_global_response.count or 0

        results_list: list[ClinicalAttentionListItem] = []
        for item in data:
            patient_data = item.get("patient") or {}
            resident_data = item.get("resident_doctor") or {}
            supervisor_data = item.get("supervisor_doctor") or {}

            results_list.append(
                ClinicalAttentionListItem(
                    id=item["id"],
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at"),
                    applies_urgency_law=item.get("applies_urgency_law"),
                    ai_result=item.get("ai_result"),
                    is_overwritten=(item.get("overwritten_by_id") is not None),
                    patient=PatientInfo(**patient_data),
                    resident_doctor=DoctorInfo(**resident_data),
                    supervisor_doctor=DoctorInfo(**supervisor_data),
                )
            )

        return {
            "count": total_count,
            "total": total_global_count,
            "page": page,
            "page_size": page_size,
            "results": results_list,
        }

    except Exception as e:
        print(f"Error en el servicio: {e}")
        raise


def get_attention_detail(attention_id: UUID) -> ClinicalAttentionDetailResponse:
    try:
        select_query = (
            "id, created_at, updated_at, "
            "is_deleted, deleted_at, "
            "deleted_by:deleted_by_id(id, first_name, last_name), "
            "overwritten_reason, "
            "overwritten_by:overwritten_by_id(id, first_name, last_name), "
            "ai_result, ai_reason, applies_urgency_law, diagnostic, "
            "patient:patient_id(id, rut, first_name, last_name, email), "
            "resident_doctor:resident_doctor_id("
            "id, first_name, last_name, email, phone), "
            "supervisor_doctor:supervisor_doctor_id("
            "id, first_name, last_name, email, phone)"
        )

        response = (
            supabase.table("ClinicalAttention")
            .select(select_query)
            .eq("id", str(attention_id))
            .execute()
        )
        if not response.data:
            raise LookupError("ClinicalAttention no encontrada")

        item = response.data[0]

        def safe_dict(data: dict | None):
            return data if data else None

        deleted_by_data = safe_dict(item.get("deleted_by"))
        overwritten_by_data = safe_dict(item.get("overwritten_by"))
        patient_data = safe_dict(item.get("patient"))
        resident_data = safe_dict(item.get("resident_doctor"))
        supervisor_data = safe_dict(item.get("supervisor_doctor"))

        return ClinicalAttentionDetailResponse(
            id=item["id"],
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
            is_deleted=bool(item.get("is_deleted", False)),
            deleted_at=item.get("deleted_at"),
            deleted_by=DeletedBy(**deleted_by_data) if deleted_by_data else None,
            overwritten_by=OverwrittenBy(**overwritten_by_data)
            if overwritten_by_data
            else None,
            patient=PatientDetail(**patient_data) if patient_data else None,
            resident_doctor=DoctorDetail(**resident_data) if resident_data else None,
            supervisor_doctor=DoctorDetail(**supervisor_data)
            if supervisor_data
            else None,
            overwritten_reason=item.get("overwritten_reason"),
            ai_result=item.get("ai_result"),
            ai_reason=item.get("ai_reason"),
            applies_urgency_law=item.get("applies_urgency_law"),
            diagnostic=item.get("diagnostic"),
        )

    except LookupError:
        raise
    except Exception as e:
        print(f"Error en el servicio (detalle): {e}")
        raise


def create_attention(
    payload: CreateClinicalAttentionRequest,
    background_tasks: BackgroundTasks,
) -> ClinicalAttentionDetailResponse:
    try:
        if isinstance(payload.patient_id, dict):
            patient_data = payload.patient_id
            patient_id = str(uuid.uuid4())
            patient_insert = (
                supabase.table("Patient")
                .insert(
                    {
                        "id": patient_id,
                        "rut": patient_data["rut"],
                        "first_name": patient_data["first_name"],
                        "last_name": patient_data["last_name"],
                        "email": patient_data["email"],
                    }
                )
                .execute()
            )

            if not patient_insert.data:
                raise HTTPException(
                    status_code=400, detail="Error al crear el paciente"
                )
        else:
            patient_id = str(payload.patient_id)
        attention_id = str(uuid.uuid4())
        insert_result = (
            supabase.table("ClinicalAttention")
            .insert(
                {
                    "id": attention_id,
                    "patient_id": patient_id,
                    "resident_doctor_id": str(payload.resident_doctor_id),
                    "supervisor_doctor_id": str(payload.supervisor_doctor_id)
                    if payload.supervisor_doctor_id
                    else None,
                    "overwritten_by_id": None,
                    "deleted_by_id": None,
                    "diagnostic": payload.diagnostic,
                    "ai_result": False,
                    "ai_reason": None,
                }
            )
            .execute()
        )

        if not insert_result.data:
            raise HTTPException(
                status_code=400, detail="Error al crear la atención clínica"
            )
        background_tasks.add_task(
            run_ai_reasoning_task, UUID(attention_id), payload.diagnostic
        )
        detail_result = get_attention_detail(UUID(attention_id))
        return detail_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en el servicio (create): {e}")
        raise HTTPException(status_code=500, detail=str(e))


def update_attention(
    attention_id: UUID,
    payload: UpdateClinicalAttentionRequest,
    background_tasks: BackgroundTasks,
):
    try:
        attention_detail = get_attention_detail(attention_id)
        should_ai_reevaluate = False
        update_data = {}

        def to_str(v):
            return str(v) if isinstance(v, UUID) else v

        if payload.patient:
            if isinstance(payload.patient, dict):
                new_patient_id = str(uuid.uuid4())
                supabase.table("Patient").insert(
                    {
                        "id": new_patient_id,
                        "rut": payload.patient.rut,
                        "first_name": payload.patient.first_name,
                        "last_name": payload.patient.last_name,
                        "email": payload.patient.email,
                    }
                ).execute()
                update_data["patient_id"] = new_patient_id
            else:
                update_data["patient_id"] = to_str(payload.patient)

        if payload.resident_doctor_id:
            update_data["resident_doctor_id"] = to_str(payload.resident_doctor_id)

        if payload.supervisor_doctor_id:
            update_data["supervisor_doctor_id"] = to_str(payload.supervisor_doctor_id)

        if payload.diagnostic is not None:
            update_data["diagnostic"] = payload.diagnostic
            if payload.diagnostic != attention_detail.diagnostic:
                should_ai_reevaluate = True

        if payload.is_deleted is not None:
            update_data["is_deleted"] = payload.is_deleted

        if not update_data:
            return attention_detail

        supabase.table("ClinicalAttention").update(update_data).eq(
            "id", str(attention_id)
        ).execute()

        if should_ai_reevaluate:
            background_tasks.add_task(
                run_ai_reasoning_task, attention_id, payload.diagnostic
            )

        return get_attention_detail(attention_id)

    except LookupError:
        raise HTTPException(status_code=404, detail="Atención clínica no encontrada")
    except Exception as e:
        print(f"Error en el servicio (update): {e}")
        raise HTTPException(
            status_code=500, detail="Error al actualizar la atención clínica"
        )


def delete_attention(attention_id: UUID, deleted_by_id: UUID):
    try:
        detail = get_attention_detail(attention_id)
        if not detail:
            raise HTTPException(
                status_code=404, detail="Atención clínica no encontrada"
            )

        response = (
            supabase.table("ClinicalAttention")
            .update(
                {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow().isoformat(),
                    "deleted_by_id": str(deleted_by_id),
                }
            )
            .eq("id", str(attention_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=400, detail="No se pudo eliminar la atención clínica"
            )

        return None
    except Exception as e:
        print(f"Error en delete_attention: {e}")
        raise HTTPException(status_code=500, detail=str(e))
