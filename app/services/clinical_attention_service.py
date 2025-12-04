import uuid
from datetime import datetime
from io import BytesIO
from uuid import UUID

import pandas as pd
from fastapi import BackgroundTasks, HTTPException, UploadFile

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
    page: int,
    page_size: int,
    search: str | None,
    order: str | None,
    resident_doctor_id: str | UUID | None = None,  # <--- NUEVO PARÁMETRO
) -> dict:
    try:
        select_query = (
            "id,id_episodio, created_at, updated_at, applies_urgency_law,"
            "ai_result, overwritten_by_id, medic_approved, pertinencia, "
            "supervisor_approved, supervisor_observation, "
            "patient:patient_id(rut, first_name, last_name), "
            "resident_doctor:resident_doctor_id(first_name, last_name), "
            "supervisor_doctor:supervisor_doctor_id(first_name, last_name)"
        )

        query = supabase.table("ClinicalAttention").select(select_query)

        # --- LÓGICA DE FILTRADO POR ROL ---
        if resident_doctor_id:
            # Si se pasa un ID de residente, filtramos para mostrar SOLO sus atenciones
            query = query.eq("resident_doctor_id", str(resident_doctor_id))
        # ----------------------------------

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

        # Count Query Logic
        count_query = supabase.table("ClinicalAttention").select("id", count="exact")
        count_query = count_query.eq("is_deleted", False)

        # También debemos aplicar el filtro de residente al conteo total
        if resident_doctor_id:
            count_query = count_query.eq("resident_doctor_id", str(resident_doctor_id))

        if search_filter:
            count_query = count_query.filter(f"or({search_filter})")
        count_response = count_query.execute()
        total_count = count_response.count or len(data)

        # Total Global (sin filtros de búsqueda, pero CON filtro de rol)
        total_global_query = supabase.table("ClinicalAttention").select(
            "id", count="exact"
        )
        if resident_doctor_id:
            total_global_query = total_global_query.eq(
                "resident_doctor_id", str(resident_doctor_id)
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
                    id_episodio=item.get("id_episodio"),
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at"),
                    applies_urgency_law=item.get("applies_urgency_law"),
                    ai_result=item.get("ai_result"),
                    patient=PatientInfo(**patient_data),
                    resident_doctor=DoctorInfo(**resident_data),
                    supervisor_doctor=DoctorInfo(**supervisor_data),
                    medic_approved=item.get("medic_approved"),
                    pertinencia=item.get("pertinencia"),
                    supervisor_approved=item.get("supervisor_approved"),  # Mapped
                    supervisor_observation=item.get("supervisor_observation"),  # Mapped
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
            "id, id_episodio, created_at, updated_at, "
            "is_deleted, deleted_at, "
            "deleted_by:deleted_by_id(id, first_name, last_name), "
            "overwritten_reason,pertinencia, "
            "overwritten_by:overwritten_by_id(id, first_name, last_name), "
            "ai_result, ai_reason, applies_urgency_law, diagnostic,"
            "ai_confidence, medic_approved,"
            "supervisor_approved, supervisor_observation, "
            "patient:patient_id(id, rut, first_name, last_name), "
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
            id_episodio=item.get("id_episodio"),
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
            ai_confidence=item.get("ai_confidence"),
            medic_approved=item.get("medic_approved"),
            pertinencia=item.get("pertinencia"),
            supervisor_approved=item.get("supervisor_approved"),  # Mapped
            supervisor_observation=item.get("supervisor_observation"),  # Mapped
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
                    "id_episodio": payload.id_episodio,
                    "patient_id": patient_id,
                    "resident_doctor_id": str(payload.resident_doctor_id),
                    "supervisor_doctor_id": str(payload.supervisor_doctor_id)
                    if payload.supervisor_doctor_id
                    else None,
                    "overwritten_by_id": None,
                    "deleted_by_id": None,
                    "diagnostic": payload.diagnostic,
                    "ai_result": None,
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
    editor_id: UUID = None,
):
    try:
        attention_detail = get_attention_detail(attention_id)
        should_ai_reevaluate = False
        update_data = {}

        explicit_data = payload.model_dump(exclude_unset=True)

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

        if payload.applies_urgency_law is not None:
            update_data["applies_urgency_law"] = payload.applies_urgency_law

        if payload.id_episodio is not None:
            update_data["id_episodio"] = payload.id_episodio
        if "overwritten_reason" in explicit_data:
            update_data["overwritten_reason"] = payload.overwritten_reason

        if "medic_approved" in explicit_data:
            update_data["medic_approved"] = payload.medic_approved

        if "overwritten_by" in explicit_data:
            val = payload.overwritten_by
            update_data["overwritten_by_id"] = str(val) if val else None
        elif editor_id:
            update_data["overwritten_by_id"] = str(editor_id)

        if "supervisor_approved" in explicit_data:
            update_data["supervisor_approved"] = payload.supervisor_approved

        if "supervisor_observation" in explicit_data:
            update_data["supervisor_observation"] = payload.supervisor_observation

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


def medic_approval(
    attention_id: UUID, medic_id: UUID, approved: bool, reason: str | None
):
    try:
        detail = get_attention_detail(attention_id)
        if not detail:
            raise HTTPException(
                status_code=404, detail="Atención clínica no encontrada"
            )

        update_data = {"medic_approved": approved}
        print(update_data)
        if approved is False:
            if not reason:
                raise HTTPException(
                    status_code=400,
                    detail="Debe entregar una razón al rechazar el diagnóstico",
                )
            update_data["applies_urgency_law"] = not detail.applies_urgency_law
            update_data["overwritten_reason"] = reason
            update_data["overwritten_by_id"] = str(medic_id)

        # Si aprueba, limpiamos rechazo anterior
        if approved is True:
            update_data["overwritten_reason"] = None
            update_data["overwritten_by_id"] = None

        resp = (
            supabase.table("ClinicalAttention")
            .update(update_data)
            .eq("id", str(attention_id))
            .execute()
        )
        print(resp)
        if not resp.data:
            raise HTTPException(status_code=400, detail="No se pudo actualizar")

        return get_attention_detail(attention_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error medic_approval service: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


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


# app/services/clinical_attention_service.py


def import_insurance_excel(insurance_company_id: int, file: UploadFile):
    try:
        # Leer Excel
        content = file.file.read()
        df = pd.read_excel(BytesIO(content))

        # Validar columnas
        if "id_episodio" not in df.columns or "pertinencia" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="El Excel debe incluir columnas: id_episodio, pertinencia",
            )

        updated_count = 0

        for _, row in df.iterrows():
            episode = str(row["id_episodio"]).strip()
            pertinencia = bool(row["pertinencia"])

            # Encontrar la atención clínica
            attention_resp = (
                supabase.table("ClinicalAttention")
                .select("id, patient_id, partinencia")
                .eq("id_episodio", episode)
                .execute()
            )

            if not attention_resp.data:
                continue

            attention = attention_resp.data[0]

            # Validar aseguradora del paciente
            patient_resp = (
                supabase.table("Patient")
                .select("insurance_company_id")
                .eq("id", attention["patient_id"])
                .single()
                .execute()
            )

            if not patient_resp.data:
                continue

            if patient_resp.data["insurance_company_id"] != insurance_company_id:
                continue

            # Actualizar pertinencia
            supabase.table("ClinicalAttention").update({"partinencia": pertinencia}).eq(
                "id", attention["id"]
            ).execute()

            updated_count += 1

        return updated_count

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error import_insurance_excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))
