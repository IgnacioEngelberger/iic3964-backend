from typing import List, Optional
from app.core.supabase_client import supabase
from app.schemas.metric import MetricStats

def _calculate_percentage(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)

def _process_rows_to_stats(rows: List[dict], entity_id: str | int, entity_name: str) -> MetricStats:
    """
    Recibe una lista de atenciones (filas) y calcula las métricas solicitadas.
    """
    total_episodes = len(rows)
    
    # 2. Ley de urgencia (Final = True)
    # applies_urgency_law es la decisión final (ya sea porque la IA acertó o el médico corrigió a True)
    urgency_law_rows = [r for r in rows if r.get("applies_urgency_law") is True]
    total_urgency_law = len(urgency_law_rows)
    
    # De estos, cuántos fueron rechazados (pertinencia == False)
    # Nota: pertinencia None se considera pendiente, no rechazado.
    urgency_law_rejected = len([r for r in urgency_law_rows if r.get("pertinencia") is False])
    
    # 3. IA dijo SI
    ai_yes_rows = [r for r in rows if r.get("ai_result") is True]
    total_ai_yes = len(ai_yes_rows)
    ai_yes_rejected = len([r for r in ai_yes_rows if r.get("pertinencia") is False])
    
    # 4. IA dijo NO y Médico dijo SI
    # ai_result False AND applies_urgency_law True
    ai_no_medic_yes_rows = [
        r for r in rows 
        if r.get("ai_result") is False and r.get("applies_urgency_law") is True
    ]
    total_ai_no_medic_yes = len(ai_no_medic_yes_rows)
    ai_no_medic_yes_rejected = len([r for r in ai_no_medic_yes_rows if r.get("pertinencia") is False])

    return MetricStats(
        id=entity_id,
        name=entity_name,
        total_episodes=total_episodes,
        
        total_urgency_law=total_urgency_law,
        percent_urgency_law_rejected=_calculate_percentage(urgency_law_rejected, total_urgency_law),
        
        total_ai_yes=total_ai_yes,
        percent_ai_yes_rejected=_calculate_percentage(ai_yes_rejected, total_ai_yes),
        
        total_ai_no_medic_yes=total_ai_no_medic_yes,
        percent_ai_no_medic_yes_rejected=_calculate_percentage(ai_no_medic_yes_rejected, total_ai_no_medic_yes)
    )

def get_base_query(start_date: Optional[str], end_date: Optional[str]):
    """Helper para iniciar la query con filtros de fecha y columnas necesarias"""
    # Traemos patient(insurance_company_id) para métricas de aseguradora
    # Traemos resident_doctor para el nombre del usuario
    query = supabase.table("ClinicalAttention").select(
        "id, created_at, applies_urgency_law, ai_result, pertinencia, resident_doctor_id, "
        "resident_doctor:resident_doctor_id(first_name, last_name), "
        "patient:patient_id(insurance_company_id)"
    )

    if start_date:
        query = query.gte("created_at", f"{start_date}T00:00:00")
    if end_date:
        query = query.lte("created_at", f"{end_date}T23:59:59")
        
    return query

# --- USER METRICS ---

def get_all_users_metrics(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[MetricStats]:
    # 1. Obtener toda la data
    query = get_base_query(start_date, end_date)
    
    response = query.execute()
    data = response.data or []
    
    # 2. Agrupar por resident_doctor_id
    grouped = {}
    
    for row in data:
        doc_id = row.get("resident_doctor_id")

        if not doc_id:
            continue
            
        if doc_id not in grouped:
            doc_info = row.get("resident_doctor") or {}
            full_name = f"{doc_info.get('first_name', '')} {doc_info.get('last_name', '')}".strip()
            grouped[doc_id] = {"name": full_name, "rows": []}
        
        grouped[doc_id]["rows"].append(row)
        
    # 3. Calcular métricas para cada grupo
    results = []
    for doc_id, info in grouped.items():
        stats = _process_rows_to_stats(info["rows"], doc_id, info["name"])
        results.append(stats)
        
    return results

def get_single_user_metrics(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> MetricStats:
    query = get_base_query(start_date, end_date).eq("resident_doctor_id", user_id)
    response = query.execute()
    data = response.data or []
    
    # Obtener nombre (si hay data, sacarlo del primer registro, si no, buscarlo en User table)
    name = "Desconocido"
    if data:
        doc_info = data[0].get("resident_doctor") or {}
        name = f"{doc_info.get('first_name', '')} {doc_info.get('last_name', '')}".strip()
    else:
        # Fallback si no hay atenciones en el rango, buscamos el nombre del usuario
        user_resp = supabase.table("User").select("first_name, last_name").eq("id", user_id).single().execute()
        if user_resp.data:
            name = f"{user_resp.data.get('first_name','')} {user_resp.data.get('last_name','')}".strip()

    return _process_rows_to_stats(data, user_id, name)

# --- INSURANCE METRICS ---

def get_insurance_metrics(company_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> MetricStats:
    # PASO 1: Obtener la aseguradora para el nombre
    company_resp = supabase.table("insurance_company").select("nombre_juridico").eq("id", company_id).single().execute()
    
    # Si la aseguradora no existe o falla
    company_name = "Desconocida"
    if company_resp.data:
        company_name = company_resp.data.get("nombre_juridico")

    # PASO 2: Obtener todos los IDs de pacientes que pertenecen a esta aseguradora
    # Esto evita el error de relación compleja en la query principal
    patients_resp = supabase.table("Patient").select("id").eq("insurance_company_id", company_id).execute()
    
    patient_ids = [p['id'] for p in (patients_resp.data or [])]

    # Si la aseguradora no tiene pacientes, retornamos métricas en 0 inmediatamente
    if not patient_ids:
        return MetricStats(
            id=company_id,
            name=company_name,
            total_episodes=0,
            total_urgency_law=0,
            percent_urgency_law_rejected=0.0,
            total_ai_yes=0,
            percent_ai_yes_rejected=0.0,
            total_ai_no_medic_yes=0,
            percent_ai_no_medic_yes_rejected=0.0
        )

    # PASO 3: Buscar las atenciones clínicas que pertenezcan a esos pacientes
    # Usamos el operador .in_() para filtrar por la lista de IDs
    query = supabase.table("ClinicalAttention").select(
        "id, created_at, applies_urgency_law, ai_result, pertinencia, resident_doctor_id"
    ).in_("patient_id", patient_ids)

    if start_date:
        query = query.gte("created_at", f"{start_date}T00:00:00")
    if end_date:
        query = query.lte("created_at", f"{end_date}T23:59:59")
        
    response = query.execute()
    data = response.data or []
    
    # PASO 4: Procesar estadísticas
    return _process_rows_to_stats(data, company_id, company_name)
