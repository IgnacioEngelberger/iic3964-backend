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


def _compute_urgency_law(ai_result, medic_approved, supervisor_approved):
    """
    Compute the urgency law application based on AI result and approvals.

    Logic:
    - Start with ai_result
    - If medic_approved is null, return null (pending)
    - If medic_approved is True, keep ai_result; if False, invert it
    - If supervisor_approved is False, invert the result again
    """
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


def list_attentions(
    page: int,
    page_size: int,
    search: str | None,
    order: str | None,
    resident_doctor_id: str | UUID | None = None,
    patient_search: str | None = None,
    doctor_search: str | None = None,
    medic_approved: str | None = None,
    supervisor_approved: str | None = None,
    current_user_id: str | UUID | None = None,
) -> dict:
    try:
        select_query = (
            "id,id_episodio, created_at, updated_at, applies_urgency_law, "
            "diagnostic, ai_result, overwritten_by_id, medic_approved, "
            "pertinencia, supervisor_approved, supervisor_observation, "
            "is_closed, closed_at, closing_reason, "
            "patient:patient_id(rut, first_name, last_name), "
            "resident_doctor:resident_doctor_id(first_name, last_name), "
            "supervisor_doctor:supervisor_doctor_id(first_name, last_name), "
            "closed_by:closed_by_id(first_name, last_name)"
        )

        query = supabase.table("ClinicalAttention").select(select_query)

        # Filter by is_deleted
        query = query.or_("is_deleted.is.null,is_deleted.eq.false")

        if resident_doctor_id:
            query = query.eq("resident_doctor_id", str(resident_doctor_id))

        # Role-based filtering for non-admin users
        if current_user_id:
            # Get user's role
            user_response = (
                supabase.table("User")
                .select("role")
                .eq("id", str(current_user_id))
                .execute()
            )

            if user_response.data and len(user_response.data) > 0:
                user_role = user_response.data[0].get("role")

                # If not admin, filter to show episodes where user is
                # resident or supervisor
                if user_role != "Admin":
                    query = query.or_(
                        f"resident_doctor_id.eq.{current_user_id!s},"
                        f"supervisor_doctor_id.eq.{current_user_id!s}",
                    )

        # Initialize filter variables for reuse in count query
        patient_ids = None
        doctor_ids = None
        search_patient_ids = None

        # Patient search filter - get matching patient IDs first
        if patient_search:
            patient_response = (
                supabase.table("Patient")
                .select("id")
                .or_(
                    f"rut.ilike.%{patient_search}%,"
                    f"first_name.ilike.%{patient_search}%,"
                    f"last_name.ilike.%{patient_search}%"
                )
                .execute()
            )
            patient_ids = [p["id"] for p in (patient_response.data or [])]
            print(
                f"Patient search '{patient_search}' found "
                f"{len(patient_ids)} matching patients"
            )
            if len(patient_ids) > 0:
                # Convert UUIDs to strings and use 'in' filter
                query = query.in_("patient_id", [str(pid) for pid in patient_ids])
            else:
                # No matching patients, return empty result
                query = query.eq("id", "00000000-0000-0000-0000-000000000000")

        # Doctor search filter - get matching doctor IDs first
        if doctor_search:
            doctor_response = (
                supabase.table("User")
                .select("id")
                .or_(
                    f"first_name.ilike.%{doctor_search}%,"
                    f"last_name.ilike.%{doctor_search}%"
                )
                .execute()
            )
            doctor_ids = [d["id"] for d in (doctor_response.data or [])]
            print(
                f"Doctor search '{doctor_search}' found "
                f"{len(doctor_ids)} matching doctors"
            )
            if len(doctor_ids) > 0:
                # Search for either resident or supervisor matching the doctor IDs
                doctor_id_strings = [str(did) for did in doctor_ids]
                # Format: "column.in.(value1,value2,value3)"
                in_clause = f"({','.join(doctor_id_strings)})"
                query = query.or_(
                    f"resident_doctor_id.in.{in_clause},"
                    f"supervisor_doctor_id.in.{in_clause}"
                )
            else:
                # No matching doctors, return empty result
                query = query.eq("id", "00000000-0000-0000-0000-000000000000")

        # Medic approved filter
        if medic_approved:
            if medic_approved == "pending":
                query = query.is_("medic_approved", "null")
            elif medic_approved == "approved":
                query = query.eq("medic_approved", True)
            elif medic_approved == "rejected":
                query = query.eq("medic_approved", False)

        # Supervisor approved filter
        if supervisor_approved:
            if supervisor_approved == "pending":
                query = query.is_("supervisor_approved", "null")
            elif supervisor_approved == "approved":
                query = query.eq("supervisor_approved", True)
            elif supervisor_approved == "rejected":
                query = query.eq("supervisor_approved", False)

        # General search filter (diagnostic or patient info)
        if search:
            # Get matching patient IDs
            search_patient_response = (
                supabase.table("Patient")
                .select("id")
                .or_(
                    f"rut.ilike.%{search}%,"
                    f"first_name.ilike.%{search}%,"
                    f"last_name.ilike.%{search}%"
                )
                .execute()
            )
            search_patient_ids = [p["id"] for p in (search_patient_response.data or [])]

            # Build OR filter: diagnostic OR patient_id in matching patients
            if len(search_patient_ids) > 0:
                patient_id_strings = [str(pid) for pid in search_patient_ids]
                query = query.or_(
                    f"diagnostic.ilike.%{search}%,"
                    f"patient_id.in.({','.join(patient_id_strings)})"
                )
            else:
                # Only search in diagnostic
                query = query.ilike("diagnostic", f"%{search}%")

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

        # Count Logic - apply same filters as main query
        count_query = supabase.table("ClinicalAttention").select("id", count="exact")
        count_query = count_query.or_("is_deleted.is.null,is_deleted.eq.false")

        if resident_doctor_id:
            count_query = count_query.eq("resident_doctor_id", str(resident_doctor_id))

        # Role-based filtering for non-admin users (same as main query)
        if current_user_id:
            user_response = (
                supabase.table("User")
                .select("role")
                .eq("id", str(current_user_id))
                .execute()
            )

            if user_response.data and len(user_response.data) > 0:
                user_role = user_response.data[0].get("role")

                if user_role != "Admin":
                    count_query = count_query.or_(
                        f"resident_doctor_id.eq.{current_user_id!s},"
                        f"supervisor_doctor_id.eq.{current_user_id!s}",
                    )

        # Use the same patient_ids from the search above
        if patient_search:
            if patient_ids is not None and len(patient_ids) > 0:
                patient_id_strings = [str(pid) for pid in patient_ids]
                count_query = count_query.in_("patient_id", patient_id_strings)
                print(
                    f"Count query: Applied patient_id filter with "
                    f"{len(patient_ids)} IDs"
                )
            else:
                count_query = count_query.eq(
                    "id", "00000000-0000-0000-0000-000000000000"
                )
                print("Count query: No matching patients, returning empty")

        # Use the same doctor_ids from the search above
        if doctor_search:
            if doctor_ids is not None and len(doctor_ids) > 0:
                doctor_id_strings = [str(did) for did in doctor_ids]
                in_clause = f"({','.join(doctor_id_strings)})"
                count_query = count_query.or_(
                    f"resident_doctor_id.in.{in_clause},"
                    f"supervisor_doctor_id.in.{in_clause}"
                )
            else:
                count_query = count_query.eq(
                    "id", "00000000-0000-0000-0000-000000000000"
                )

        if medic_approved:
            if medic_approved == "pending":
                count_query = count_query.is_("medic_approved", "null")
            elif medic_approved == "approved":
                count_query = count_query.eq("medic_approved", True)
            elif medic_approved == "rejected":
                count_query = count_query.eq("medic_approved", False)

        if supervisor_approved:
            if supervisor_approved == "pending":
                count_query = count_query.is_("supervisor_approved", "null")
            elif supervisor_approved == "approved":
                count_query = count_query.eq("supervisor_approved", True)
            elif supervisor_approved == "rejected":
                count_query = count_query.eq("supervisor_approved", False)

        # Use the same general search logic from main query
        if search:
            if search_patient_ids is not None and len(search_patient_ids) > 0:
                patient_id_strings = [str(pid) for pid in search_patient_ids]
                count_query = count_query.or_(
                    f"diagnostic.ilike.%{search}%,"
                    f"patient_id.in.({','.join(patient_id_strings)})"
                )
            else:
                count_query = count_query.ilike("diagnostic", f"%{search}%")

        count_response = count_query.execute()
        total_count = count_response.count or len(data)
        print(f"Count query result: total_count={total_count}, data_length={len(data)}")

        # Total Global
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
            closed_by_data = item.get("closed_by") or {}

            # Compute urgency law based on AI result and approvals
            computed_urgency_law = _compute_urgency_law(
                ai_result=item.get("ai_result"),
                medic_approved=item.get("medic_approved"),
                supervisor_approved=item.get("supervisor_approved"),
            )

            results_list.append(
                ClinicalAttentionListItem(
                    id=item["id"],
                    id_episodio=item.get("id_episodio"),
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at"),
                    applies_urgency_law=computed_urgency_law,
                    ai_result=item.get("ai_result"),
                    patient=PatientInfo(**patient_data),
                    diagnostic=item.get("diagnostic"),
                    resident_doctor=DoctorInfo(**resident_data),
                    supervisor_doctor=DoctorInfo(**supervisor_data),
                    medic_approved=item.get("medic_approved"),
                    pertinencia=item.get("pertinencia"),
                    supervisor_approved=item.get("supervisor_approved"),
                    supervisor_observation=item.get("supervisor_observation"),
                    is_closed=item.get("is_closed"),
                    closed_at=item.get("closed_at"),
                    closed_by=DoctorInfo(**closed_by_data) if closed_by_data else None,
                    closing_reason=item.get("closing_reason"),
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
            "id, first_name, last_name, email, phone), "
            "is_closed"
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

        # Compute urgency law based on AI result and approvals
        computed_urgency_law = _compute_urgency_law(
            ai_result=item.get("ai_result"),
            medic_approved=item.get("medic_approved"),
            supervisor_approved=item.get("supervisor_approved"),
        )

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
            applies_urgency_law=computed_urgency_law,
            diagnostic=item.get("diagnostic"),
            ai_confidence=item.get("ai_confidence"),
            medic_approved=item.get("medic_approved"),
            pertinencia=item.get("pertinencia"),
            supervisor_approved=item.get("supervisor_approved"),
            supervisor_observation=item.get("supervisor_observation"),
            is_closed=item.get("is_closed"),
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

        # Note: applies_urgency_law is now computed, not stored in DB
        # Removed: if payload.applies_urgency_law is not None

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

        if "pertinencia" in explicit_data:
            update_data["pertinencia"] = payload.pertinencia

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

        if approved is False:
            if not reason:
                raise HTTPException(
                    status_code=400,
                    detail="Debe entregar una razón al rechazar el diagnóstico",
                )
            update_data["overwritten_reason"] = reason
            update_data["overwritten_by_id"] = str(medic_id)

        if approved is True:
            update_data["overwritten_reason"] = None
            update_data["overwritten_by_id"] = None

        resp = (
            supabase.table("ClinicalAttention")
            .update(update_data)
            .eq("id", str(attention_id))
            .execute()
        )

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


def import_insurance_excel(insurance_company_id: int, file: UploadFile):
    try:
        print(f"Starting import for insurance_company_id: {insurance_company_id}")
        print(f"File: {file.filename}, Content-Type: {file.content_type}")

        content = file.file.read()
        print(f"File size: {len(content)} bytes")

        df = pd.read_excel(BytesIO(content))
        print(f"Excel loaded. Rows: {len(df)}, Columns: {list(df.columns)}")

        # Check for required columns (case insensitive)
        column_mapping = {}
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['"episodio"', "episodio", "id_episodio"]:
                column_mapping["episodio"] = col
            elif col_lower in ["validación", "validacion", "pertinencia"]:
                column_mapping["validacion"] = col

        if "episodio" not in column_mapping or "validacion" not in column_mapping:
            raise HTTPException(
                status_code=400,
                detail="El Excel debe incluir columnas: 'Episodio' y 'Validación'",
            )

        updated_count = 0

        for idx, row in df.iterrows():
            try:
                episode = str(row[column_mapping["episodio"]]).strip()
                validacion_value = (
                    str(row[column_mapping["validacion"]]).strip().upper()
                )

                # Convert "PERTINENTE" / "NO PERTINENTE" to boolean
                if validacion_value == "PERTINENTE":
                    pertinencia = True
                elif validacion_value == "NO PERTINENTE":
                    pertinencia = False
                else:
                    # Try to parse as boolean/numeric for backwards compatibility
                    try:
                        pertinencia = bool(int(validacion_value))
                    except (ValueError, TypeError):
                        print(
                            f"Skipping row {idx}: Invalid validacion value "
                            f"'{validacion_value}'"
                        )
                        continue

                print(
                    f"Processing row {idx}: episode={episode}, "
                    f"pertinencia={pertinencia}"
                )

                attention_resp = (
                    supabase.table("ClinicalAttention")
                    .select("id, patient_id, pertinencia")
                    .eq("id_episodio", episode)
                    .execute()
                )

                if not attention_resp.data:
                    print(f"No clinical attention found for episode: {episode}")
                    continue

                attention = attention_resp.data[0]

                patient_resp = (
                    supabase.table("Patient")
                    .select("insurance_company_id")
                    .eq("id", attention["patient_id"])
                    .single()
                    .execute()
                )

                if not patient_resp.data:
                    print(f"No patient found for attention: {attention['id']}")
                    continue

                if patient_resp.data["insurance_company_id"] != insurance_company_id:
                    print(f"Insurance mismatch for episode {episode}")
                    continue

                supabase.table("ClinicalAttention").update(
                    {"pertinencia": pertinencia}
                ).eq("id", attention["id"]).execute()

                updated_count += 1
            except Exception as row_error:
                print(f"Error processing row {idx}: {str(row_error)}")
                import traceback

                print(traceback.format_exc())
                # Continue with next row instead of failing completely

        print(f"Import completed. Updated {updated_count} records")
        return updated_count

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error import_insurance_excel: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))


def close_episode(attention_id: UUID, closed_by_id: UUID, closing_reason: str):
    """
    Close a clinical attention episode.
    Can be called by resident, supervisor, or admin.
    Requires a closing reason: Muerte, Hospitalización, or Alta.
    """
    try:
        from datetime import datetime

        # Validate closing reason
        valid_reasons = ["Muerte", "Hospitalización", "Alta", "Traslado"]
        if closing_reason not in valid_reasons:
            reasons_str = ", ".join(valid_reasons)
            raise HTTPException(
                status_code=400,
                detail=f"Razón de cierre inválida. Debe ser una de: {reasons_str}",
            )

        # Check if episode exists and is not deleted
        response = (
            supabase.table("ClinicalAttention")
            .select("id, is_closed, is_deleted")
            .eq("id", str(attention_id))
            .execute()
        )

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404, detail="Atención clínica no encontrada"
            )

        attention = response.data[0]

        if attention.get("is_deleted"):
            raise HTTPException(
                status_code=400, detail="No se puede cerrar una atención eliminada"
            )

        if attention.get("is_closed"):
            raise HTTPException(status_code=400, detail="La atención ya está cerrada")

        # Close the episode
        update_response = (
            supabase.table("ClinicalAttention")
            .update(
                {
                    "is_closed": True,
                    "closed_at": datetime.utcnow().isoformat(),
                    "closed_by_id": str(closed_by_id),
                    "closing_reason": closing_reason,
                }
            )
            .eq("id", str(attention_id))
            .execute()
        )

        if not update_response.data:
            raise HTTPException(status_code=500, detail="Error al cerrar la atención")

        return {"success": True, "message": "Atención cerrada exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in close_episode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def reopen_episode(attention_id: UUID, reopened_by_id: UUID):
    """
    Reopen a closed clinical attention episode.
    Can only be called by admin.
    """
    try:
        # Verify user is admin
        user_response = (
            supabase.table("User")
            .select("role")
            .eq("id", str(reopened_by_id))
            .execute()
        )

        if not user_response.data or len(user_response.data) == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user_role = user_response.data[0].get("role")
        if user_role != "Admin":
            raise HTTPException(
                status_code=403,
                detail="Solo los administradores pueden reabrir episodios",
            )

        # Check if episode exists and is closed
        response = (
            supabase.table("ClinicalAttention")
            .select("id, is_closed, is_deleted")
            .eq("id", str(attention_id))
            .execute()
        )

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404, detail="Atención clínica no encontrada"
            )

        attention = response.data[0]

        if attention.get("is_deleted"):
            raise HTTPException(
                status_code=400, detail="No se puede reabrir una atención eliminada"
            )

        if not attention.get("is_closed"):
            raise HTTPException(status_code=400, detail="La atención no está cerrada")

        # Reopen the episode
        update_response = (
            supabase.table("ClinicalAttention")
            .update(
                {
                    "is_closed": False,
                    "closed_at": None,
                    "closed_by_id": None,
                    "closing_reason": None,
                }
            )
            .eq("id", str(attention_id))
            .execute()
        )

        if not update_response.data:
            raise HTTPException(status_code=500, detail="Error al reabrir la atención")

        return {"success": True, "message": "Atención reabierta exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reopen_episode: {e}")
        raise HTTPException(status_code=500, detail=str(e))
