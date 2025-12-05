"""Test data fixtures for clinical attention system."""

from datetime import datetime, timezone
from uuid import uuid4


def get_mock_patient():
    """Mock patient data."""
    return {
        "id": str(uuid4()),
        "rut": "12345678-9",
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan.perez@example.com",
        "insurance_company_id": 1,
    }


def get_mock_resident_doctor():
    """Mock resident doctor data."""
    return {
        "id": str(uuid4()),
        "first_name": "María",
        "last_name": "González",
        "email": "maria.gonzalez@hospital.cl",
        "phone": "+56912345678",
        "role": "resident",
    }


def get_mock_supervisor_doctor():
    """Mock supervisor doctor data."""
    return {
        "id": str(uuid4()),
        "first_name": "Carlos",
        "last_name": "Rodríguez",
        "email": "carlos.rodriguez@hospital.cl",
        "phone": "+56987654321",
        "role": "supervisor",
    }


def get_mock_clinical_attention(
    patient_id: str = None,
    resident_doctor_id: str = None,
    supervisor_doctor_id: str = None,
    applies_urgency_law: bool = True,
    medic_approved: bool = None,
    supervisor_approved: bool = None,
):
    """Mock clinical attention data."""
    attention_id = str(uuid4())
    return {
        "id": attention_id,
        "id_episodio": f"EP-2024-{uuid4().hex[:6].upper()}",
        "patient_id": patient_id or str(uuid4()),
        "resident_doctor_id": resident_doctor_id or str(uuid4()),
        "supervisor_doctor_id": supervisor_doctor_id or str(uuid4()),
        "diagnostic": """Paciente con dolor torácico
        opresivo irradiado a brazo izquierdo,
        diaforesis y náuseas. Sospecha de infarto agudo al miocardio.""",
        "applies_urgency_law": applies_urgency_law,
        "ai_result": applies_urgency_law,
        "ai_reason": """{"urgency_assessment":
        "Critical cardiovascular emergency", "risk_level": "high"}""",
        "ai_confidence": 0.95,
        "medic_approved": medic_approved,
        "supervisor_approved": supervisor_approved,
        "pertinencia": None,
        "is_deleted": False,
        "deleted_at": None,
        "deleted_by_id": None,
        "overwritten_by_id": None,
        "overwritten_reason": None,
        "supervisor_observation": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def get_mock_clinical_attention_with_relations():
    """Mock clinical attention with nested patient and doctor data."""
    patient = get_mock_patient()
    resident = get_mock_resident_doctor()
    supervisor = get_mock_supervisor_doctor()

    attention = get_mock_clinical_attention(
        patient_id=patient["id"],
        resident_doctor_id=resident["id"],
        supervisor_doctor_id=supervisor["id"],
    )

    # Add nested relations
    attention["patient"] = {
        "rut": patient["rut"],
        "first_name": patient["first_name"],
        "last_name": patient["last_name"],
    }
    attention["resident_doctor"] = {
        "first_name": resident["first_name"],
        "last_name": resident["last_name"],
    }
    attention["supervisor_doctor"] = {
        "first_name": supervisor["first_name"],
        "last_name": supervisor["last_name"],
    }

    return attention, patient, resident, supervisor


def get_mock_insurance_company():
    """Mock insurance company data."""
    return {
        "id": 1,
        "name": "Isapre Test",
        "rut": "76543210-K",
    }


def get_mock_gemini_response(urgency_applies: bool = True, confidence: float = 0.95):
    """Mock Gemini AI response."""

    class MockGeminiOutput:
        def __init__(self, urgency_applies: bool, confidence: float):
            self.urgency_flag = "applies" if urgency_applies else "does_not_apply"
            self.rationale = (
                """{"urgency_assessment":
                "Critical emergency requiring
                immediate attention", "risk_level": "high"}"""
                if urgency_applies
                else """{"urgency_assessment": "Non-urgent condition"
                , "risk_level": "low"}"""
            )
            self.urgency_confidence = confidence

    return MockGeminiOutput(urgency_applies, confidence)


def get_mock_clinical_attention_detail_response():
    """Mock ClinicalAttentionDetailResponse for endpoint tests."""
    from app.schemas.clinical_attention import (
        ClinicalAttentionDetailResponse,
        DoctorDetail,
        PatientDetail,
    )

    (
        attention,
        patient,
        resident,
        supervisor,
    ) = get_mock_clinical_attention_with_relations()

    return ClinicalAttentionDetailResponse(
        id=attention["id"],
        id_episodio=attention.get("id_episodio"),
        created_at=attention.get("created_at"),
        updated_at=attention.get("updated_at"),
        is_deleted=False,
        deleted_at=None,
        deleted_by=None,
        overwritten_by=None,
        patient=PatientDetail(
            id=patient["id"],
            rut=patient["rut"],
            first_name=patient["first_name"],
            last_name=patient["last_name"],
        ),
        resident_doctor=DoctorDetail(
            id=resident["id"],
            first_name=resident["first_name"],
            last_name=resident["last_name"],
            email=resident.get("email"),
            phone=resident.get("phone"),
        ),
        supervisor_doctor=DoctorDetail(
            id=supervisor["id"],
            first_name=supervisor["first_name"],
            last_name=supervisor["last_name"],
            email=supervisor.get("email"),
            phone=supervisor.get("phone"),
        ),
        overwritten_reason=None,
        ai_result=attention.get("ai_result"),
        ai_reason=attention.get("ai_reason"),
        applies_urgency_law=attention.get("applies_urgency_law"),
        diagnostic=attention.get("diagnostic"),
        ai_confidence=attention.get("ai_confidence"),
        medic_approved=attention.get("medic_approved"),
        pertinencia=attention.get("pertinencia"),
        supervisor_approved=attention.get("supervisor_approved"),
        supervisor_observation=attention.get("supervisor_observation"),
    )
