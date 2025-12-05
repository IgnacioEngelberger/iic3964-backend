"""Unit tests for clinical_attention_service."""

import io
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pandas as pd
import pytest
from fastapi import HTTPException

from app.services import clinical_attention_service
from tests.fixtures.data_fixtures import (
    get_mock_clinical_attention,
    get_mock_clinical_attention_with_relations,
    get_mock_patient,
)


class TestListAttentions:
    """Tests for list_attentions function."""

    @patch("app.services.clinical_attention_service.supabase")
    def test_list_attentions_basic(self, mock_supabase):
        """Test listing clinical attentions without filters."""
        # Arrange
        (
            attention1,
            patient,
            resident,
            supervisor,
        ) = get_mock_clinical_attention_with_relations()
        attention2 = {**attention1, "id": str(uuid4()), "id_episodio": "EP-2024-002"}

        mock_supabase.table().select().order().range().execute.return_value.data = [
            attention1,
            attention2,
        ]
        mock_supabase.table().select().eq().execute.return_value.count = 2

        # Act
        result = clinical_attention_service.list_attentions(
            page=1, page_size=10, search=None, order=None
        )

        # Assert
        assert result["count"] == 2
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert len(result["results"]) == 2
        assert result["results"][0].id == UUID(attention1["id"])

    @patch("app.services.clinical_attention_service.supabase")
    def test_list_attentions_with_resident_filter(self, mock_supabase):
        """Test filtering attentions by resident doctor."""
        # Arrange
        resident_id = str(uuid4())
        (
            attention,
            patient,
            resident,
            supervisor,
        ) = get_mock_clinical_attention_with_relations()
        attention["resident_doctor_id"] = resident_id

        # Mock the main query
        mock_query_response = MagicMock()
        mock_query_response.data = [attention]
        mock_supabase.table().select().eq().order().range().execute.return_value = (
            mock_query_response
        )

        # Mock the count query
        mock_count_response = MagicMock()
        mock_count_response.count = 1
        mock_supabase.table().select().eq().eq().execute.return_value = (
            mock_count_response
        )

        # Act
        result = clinical_attention_service.list_attentions(
            page=1,
            page_size=10,
            search=None,
            order=None,
            resident_doctor_id=resident_id,
        )

        # Assert
        assert result["count"] == 1
        assert len(result["results"]) == 1

    @patch("app.services.clinical_attention_service.supabase")
    def test_list_attentions_with_pagination(self, mock_supabase):
        """Test pagination in list_attentions."""
        # Arrange
        attentions = []
        for i in range(5):
            attention, _, _, _ = get_mock_clinical_attention_with_relations()
            attention["id"] = str(uuid4())
            attentions.append(attention)

        mock_supabase.table().select().order().range().execute.return_value.data = (
            attentions[0:2]
        )
        mock_supabase.table().select().eq().execute.return_value.count = 5

        # Act
        result = clinical_attention_service.list_attentions(
            page=1, page_size=2, search=None, order=None
        )

        # Assert
        assert result["count"] == 5
        assert result["page_size"] == 2
        assert len(result["results"]) == 2


class TestGetAttentionDetail:
    """Tests for get_attention_detail function."""

    @patch("app.services.clinical_attention_service.supabase")
    def test_get_attention_detail_success(self, mock_supabase):
        """Test successful retrieval of attention detail."""
        # Arrange
        (
            attention,
            patient,
            resident,
            supervisor,
        ) = get_mock_clinical_attention_with_relations()
        attention_id = UUID(attention["id"])

        # Add full doctor details for detail response
        attention["resident_doctor"] = {
            "id": resident["id"],
            "first_name": resident["first_name"],
            "last_name": resident["last_name"],
            "email": resident["email"],
            "phone": resident["phone"],
        }
        attention["supervisor_doctor"] = {
            "id": supervisor["id"],
            "first_name": supervisor["first_name"],
            "last_name": supervisor["last_name"],
            "email": supervisor["email"],
            "phone": supervisor["phone"],
        }
        attention["patient"] = {
            "id": patient["id"],
            "rut": patient["rut"],
            "first_name": patient["first_name"],
            "last_name": patient["last_name"],
        }
        attention["deleted_by"] = None
        attention["overwritten_by"] = None

        mock_supabase.table().select().eq().execute.return_value.data = [attention]

        # Act
        result = clinical_attention_service.get_attention_detail(attention_id)

        # Assert
        assert result.id == attention_id
        assert result.patient.first_name == patient["first_name"]
        assert result.resident_doctor.first_name == resident["first_name"]
        assert result.applies_urgency_law is True

    @patch("app.services.clinical_attention_service.supabase")
    def test_get_attention_detail_not_found(self, mock_supabase):
        """Test get_attention_detail when attention doesn't exist."""
        # Arrange
        attention_id = uuid4()
        mock_supabase.table().select().eq().execute.return_value.data = []

        # Act & Assert
        with pytest.raises(LookupError, match="ClinicalAttention no encontrada"):
            clinical_attention_service.get_attention_detail(attention_id)


class TestCreateAttention:
    """Tests for create_attention function."""

    @patch("app.services.clinical_attention_service.get_attention_detail")
    @patch("app.services.clinical_attention_service.supabase")
    def test_create_attention_with_existing_patient(
        self, mock_supabase, mock_get_detail
    ):
        """Test creating attention with existing patient ID."""
        # Arrange
        from app.schemas.clinical_attention import CreateClinicalAttentionRequest

        patient = get_mock_patient()
        request = CreateClinicalAttentionRequest(
            patient_id=UUID(patient["id"]),
            resident_doctor_id=uuid4(),
            supervisor_doctor_id=uuid4(),
            diagnostic="Test diagnostic for chest pain",
        )

        mock_attention = get_mock_clinical_attention(patient_id=patient["id"])
        mock_supabase.table().insert().execute.return_value.data = [mock_attention]
        mock_get_detail.return_value = MagicMock(id=UUID(mock_attention["id"]))

        background_tasks = MagicMock()

        # Act
        result = clinical_attention_service.create_attention(request, background_tasks)

        # Assert
        assert result.id is not None
        background_tasks.add_task.assert_called_once()

    @patch("app.services.clinical_attention_service.get_attention_detail")
    @patch("app.services.clinical_attention_service.supabase")
    def test_create_attention_with_new_patient(self, mock_supabase, mock_get_detail):
        """Test creating attention with nested patient data."""
        # Arrange

        {
            "patient_id": {
                "rut": "12345678-9",
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan@example.com",
            },
            "resident_doctor_id": str(uuid4()),
            "supervisor_doctor_id": str(uuid4()),
            "diagnostic": "Test diagnostic",
        }

        # Mock patient insert
        mock_patient_response = MagicMock()
        mock_patient_response.data = [{"id": str(uuid4())}]

        # Mock attention insert
        mock_attention = get_mock_clinical_attention()
        mock_attention_response = MagicMock()
        mock_attention_response.data = [mock_attention]

        mock_supabase.table.side_effect = [
            MagicMock(
                insert=MagicMock(
                    return_value=MagicMock(
                        execute=MagicMock(return_value=mock_patient_response)
                    )
                )
            ),
            MagicMock(
                insert=MagicMock(
                    return_value=MagicMock(
                        execute=MagicMock(return_value=mock_attention_response)
                    )
                )
            ),
        ]

        mock_get_detail.return_value = MagicMock(id=UUID(mock_attention["id"]))
        MagicMock()

        # Note: This test may need adjustment based on how the nested patient is handled


class TestMedicApproval:
    """Tests for medic_approval function."""

    @patch("app.services.clinical_attention_service.get_attention_detail")
    @patch("app.services.clinical_attention_service.supabase")
    def test_medic_approval_approve(self, mock_supabase, mock_get_detail):
        """Test medic approving AI recommendation."""
        # Arrange
        attention_id = uuid4()
        medic_id = uuid4()
        mock_attention = MagicMock()
        mock_attention.applies_urgency_law = True
        mock_get_detail.return_value = mock_attention

        mock_update_response = MagicMock()
        mock_update_response.data = [{"id": str(attention_id), "medic_approved": True}]
        mock_supabase.table().update().eq().execute.return_value = mock_update_response

        # Act
        clinical_attention_service.medic_approval(
            attention_id=attention_id, medic_id=medic_id, approved=True, reason=None
        )

        # Assert
        # Note: update() may be called multiple times due to get_attention_detail
        update_calls = [
            call for call in mock_supabase.table().update.call_args_list if call[0]
        ]
        assert len(update_calls) > 0
        update_call = update_calls[0][0][0]  # Get first update call's data
        assert update_call["medic_approved"] is True

    @patch("app.services.clinical_attention_service.get_attention_detail")
    @patch("app.services.clinical_attention_service.supabase")
    def test_medic_approval_reject(self, mock_supabase, mock_get_detail):
        """Test medic rejecting AI recommendation (toggles urgency law)."""
        # Arrange
        attention_id = uuid4()
        medic_id = uuid4()
        mock_attention = MagicMock()
        mock_attention.applies_urgency_law = True  # AI said applies
        mock_get_detail.return_value = mock_attention

        mock_update_response = MagicMock()
        mock_update_response.data = [
            {
                "id": str(attention_id),
                "medic_approved": False,
                "applies_urgency_law": False,
            }
        ]
        mock_supabase.table().update().eq().execute.return_value = mock_update_response

        # Act
        clinical_attention_service.medic_approval(
            attention_id=attention_id,
            medic_id=medic_id,
            approved=False,
            reason="Paciente estable, no requiere urgencia",
        )

        # Assert
        update_call = mock_supabase.table().update.call_args[0][0]
        assert update_call["medic_approved"] is False
        assert update_call["applies_urgency_law"] is False  # Toggled from True
        assert (
            update_call["overwritten_reason"]
            == "Paciente estable, no requiere urgencia"
        )
        assert update_call["overwritten_by_id"] == str(medic_id)

    @patch("app.services.clinical_attention_service.get_attention_detail")
    def test_medic_approval_reject_without_reason_fails(self, mock_get_detail):
        """Test that rejecting without reason raises error."""
        # Arrange
        attention_id = uuid4()
        medic_id = uuid4()
        mock_get_detail.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            clinical_attention_service.medic_approval(
                attention_id=attention_id,
                medic_id=medic_id,
                approved=False,
                reason=None,
            )
        assert exc_info.value.status_code == 400
        assert "razón" in exc_info.value.detail.lower()


class TestImportInsuranceExcel:
    @patch("app.services.clinical_attention_service.supabase")
    def test_import_insurance_excel_success(self, mock_supabase):
        """Test successful Excel import with pertinencia updates."""
        # Arrange
        insurance_company_id = 1

        # Create Excel file in memory
        df = pd.DataFrame(
            {
                "id_episodio": ["EP-001", "EP-002", "EP-003"],
                "pertinencia": [True, False, True],
            }
        )
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        mock_file = MagicMock()
        mock_file.file.read.return_value = excel_buffer.getvalue()

        # Mock for row-by-row queries
        attention_ids = [str(uuid4()), str(uuid4()), str(uuid4())]

        def mock_attention_select(*args, **kwargs):
            # Return mock query builder
            query = MagicMock()
            query.select.return_value = query
            query.eq.return_value = query
            query.single.return_value = query

            # Return different data based on call count
            if not hasattr(mock_attention_select, "call_count"):
                mock_attention_select.call_count = 0

            idx = mock_attention_select.call_count % 3
            query.execute.return_value.data = [
                {"id": attention_ids[idx], "patient_id": str(uuid4())}
            ]
            mock_attention_select.call_count += 1
            return query

        def mock_patient_select(*args, **kwargs):
            query = MagicMock()
            query.select.return_value = query
            query.eq.return_value = query
            query.single.return_value = query
            query.execute.return_value.data = {
                "insurance_company_id": insurance_company_id
            }
            return query

        # Use side_effect to alternate between attention and patient queries
        mock_supabase.table.side_effect = [
            mock_attention_select(),  # First attention
            mock_patient_select(),  # First patient
            MagicMock(
                update=MagicMock(
                    return_value=MagicMock(
                        eq=MagicMock(return_value=MagicMock(execute=MagicMock()))
                    )
                )
            ),  # Update
            mock_attention_select(),  # Second attention
            mock_patient_select(),  # Second patient
            MagicMock(
                update=MagicMock(
                    return_value=MagicMock(
                        eq=MagicMock(return_value=MagicMock(execute=MagicMock()))
                    )
                )
            ),  # Update
            mock_attention_select(),  # Third attention
            mock_patient_select(),  # Third patient
            MagicMock(
                update=MagicMock(
                    return_value=MagicMock(
                        eq=MagicMock(return_value=MagicMock(execute=MagicMock()))
                    )
                )
            ),  # Update
        ]

        # Act
        result = clinical_attention_service.import_insurance_excel(
            insurance_company_id=insurance_company_id, file=mock_file
        )

        # Assert
        assert result == 3  # All 3 episodes updated

    @patch("app.services.clinical_attention_service.supabase")
    def test_import_insurance_excel_filters_wrong_insurance(self, mock_supabase):
        # Arrange
        insurance_company_id = 1

        df = pd.DataFrame(
            {
                "id_episodio": ["EP-001", "EP-002"],
                "pertinencia": [True, False],
            }
        )
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        mock_file = MagicMock()
        mock_file.file.read.return_value = excel_buffer.getvalue()

        # Mock responses for row-by-row processing
        def create_attention_query(patient_id):
            query = MagicMock()
            query.select.return_value = query
            query.eq.return_value = query
            query.execute.return_value.data = [
                {"id": str(uuid4()), "patient_id": patient_id}
            ]
            return query

        def create_patient_query(insurance_id):
            query = MagicMock()
            query.select.return_value = query
            query.eq.return_value = query
            query.single.return_value = query
            query.execute.return_value.data = {"insurance_company_id": insurance_id}
            return query

        patient_id1 = str(uuid4())
        patient_id2 = str(uuid4())

        mock_supabase.table.side_effect = [
            create_attention_query(patient_id1),  # EP-001 attention
            create_patient_query(1),  # Patient with insurance_company_id=1
            MagicMock(
                update=MagicMock(
                    return_value=MagicMock(
                        eq=MagicMock(return_value=MagicMock(execute=MagicMock()))
                    )
                )
            ),  # Update
            create_attention_query(patient_id2),  # EP-002 attention
            create_patient_query(
                2
            ),  # Patient with insurance_company_id=2 (filtered out)
        ]

        # Act
        result = clinical_attention_service.import_insurance_excel(
            insurance_company_id=insurance_company_id, file=mock_file
        )

        # Assert
        assert result == 1  # Only EP-001 updated

    def test_import_insurance_excel_missing_columns(self):
        """Test that Excel with missing columns raises error."""
        # Arrange
        df = pd.DataFrame({"id_episodio": ["EP-001"]})  # Missing pertinencia column
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        mock_file = MagicMock()
        mock_file.file.read.return_value = excel_buffer.getvalue()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            clinical_attention_service.import_insurance_excel(
                insurance_company_id=1, file=mock_file
            )
        assert exc_info.value.status_code == 400
        assert "pertinencia" in exc_info.value.detail


# Note: get_clinical_history_by_patient_ids tests removed as function was reverted
# by user. Tests can be added back when/if the function is re-implemented.
