"""Tests for patient service."""
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.schemas.patient import PatientCreate, PatientUpdate


class TestListPatients:
    """Tests for list_patients function."""

    @patch("app.services.patient_service.supabase")
    def test_list_patients_success(self, mock_supabase):
        """Test successful retrieval of all patients."""
        from app.services.patient_service import list_patients

        # Arrange
        mock_patients = [
            {
                "id": str(uuid4()),
                "rut": "12345678-9",
                "first_name": "Juan",
                "last_name": "Pérez",
                "mother_last_name": "García",
                "age": 30,
                "sex": "M",
                "height": 175.0,
                "weight": 70.0,
                "insurance_company_id": 1,
                "insurance_company": {
                    "id": 1,
                    "nombre_juridico": "Isapre Test",
                    "nombre_comercial": "Test",
                    "rut": "12345678-9",
                },
            }
        ]
        mock_response = MagicMock()
        mock_response.data = mock_patients
        mock_supabase.table().select().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_patients()

        # Assert
        assert result == mock_patients
        mock_supabase.table.assert_called_with("Patient")

    @patch("app.services.patient_service.supabase")
    def test_list_patients_empty(self, mock_supabase):
        """Test list patients when no patients exist."""
        from app.services.patient_service import list_patients

        # Arrange
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table().select().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_patients()

        # Assert
        assert result == []

    @patch("app.services.patient_service.supabase")
    def test_list_patients_none_data(self, mock_supabase):
        """Test list patients when response.data is None."""
        from app.services.patient_service import list_patients

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().select().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_patients()

        # Assert
        assert result == []

    @patch("app.services.patient_service.supabase")
    def test_list_patients_error(self, mock_supabase):
        """Test list patients when an error occurs."""
        from app.services.patient_service import list_patients

        # Arrange
        mock_supabase.table().select().eq().order().execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            list_patients()
        assert "Database error" in str(excinfo.value)


class TestGetPatientById:
    """Tests for get_patient_by_id function."""

    @patch("app.services.patient_service.supabase")
    def test_get_patient_by_id_success(self, mock_supabase):
        """Test successful retrieval of patient by ID."""
        from app.services.patient_service import get_patient_by_id

        # Arrange
        patient_id = uuid4()
        mock_patient = {
            "id": str(patient_id),
            "rut": "12345678-9",
            "first_name": "Juan",
            "last_name": "Pérez",
            "mother_last_name": "García",
            "age": 30,
            "sex": "M",
            "height": 175.0,
            "weight": 70.0,
            "insurance_company_id": 1,
            "insurance_company": {
                "id": 1,
                "nombre_juridico": "Isapre Test",
                "nombre_comercial": "Test",
                "rut": "12345678-9",
            },
        }
        mock_response = MagicMock()
        mock_response.data = mock_patient
        mock_supabase.table().select().eq().single().execute.return_value = (
            mock_response
        )

        # Act
        result = get_patient_by_id(patient_id)

        # Assert
        assert result == mock_patient

    @patch("app.services.patient_service.supabase")
    def test_get_patient_by_id_error(self, mock_supabase):
        """Test get patient by ID when an error occurs."""
        from app.services.patient_service import get_patient_by_id

        # Arrange
        patient_id = uuid4()
        mock_supabase.table().select().eq().single().execute.side_effect = Exception(
            "Patient not found"
        )

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            get_patient_by_id(patient_id)
        assert "Patient not found" in str(excinfo.value)


class TestCreatePatient:
    """Tests for create_patient function."""

    @patch("app.services.patient_service.uuid.uuid4")
    @patch("app.services.patient_service.supabase")
    def test_create_patient_success(self, mock_supabase, mock_uuid):
        """Test successful creation of patient."""
        from app.services.patient_service import create_patient

        # Arrange
        patient_id = uuid4()
        mock_uuid.return_value = patient_id

        payload = PatientCreate(
            rut="12345678-9",
            first_name="Juan",
            last_name="Pérez",
            mother_last_name="García",
            age=30,
            sex="M",
            height=175.0,
            weight=70.0,
            insurance_company_id=1,
        )

        expected_patient = {
            "id": str(patient_id),
            "rut": "12345678-9",
            "first_name": "Juan",
            "last_name": "Pérez",
            "mother_last_name": "García",
            "age": 30,
            "sex": "M",
            "height": 175.0,
            "weight": 70.0,
            "insurance_company_id": 1,
            "is_deleted": False,
        }

        mock_response = MagicMock()
        mock_response.data = [expected_patient]
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        result = create_patient(payload)

        # Assert
        assert result == expected_patient
        mock_supabase.table.assert_called_with("Patient")

    @patch("app.services.patient_service.uuid.uuid4")
    @patch("app.services.patient_service.supabase")
    def test_create_patient_no_data(self, mock_supabase, mock_uuid):
        """Test create patient when response has no data."""
        from app.services.patient_service import create_patient

        # Arrange
        patient_id = uuid4()
        mock_uuid.return_value = patient_id

        payload = PatientCreate(
            rut="12345678-9",
            first_name="Juan",
            last_name="Pérez",
            age=30,
            sex="M",
            insurance_company_id=1,
        )

        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            create_patient(payload)
        assert "No se pudo crear el paciente" in str(excinfo.value)

    @patch("app.services.patient_service.supabase")
    def test_create_patient_error(self, mock_supabase):
        """Test create patient when an error occurs."""
        from app.services.patient_service import create_patient

        # Arrange
        payload = PatientCreate(
            rut="12345678-9",
            first_name="Juan",
            last_name="Pérez",
            age=30,
            sex="M",
            insurance_company_id=1,
        )

        mock_supabase.table().insert().execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            create_patient(payload)
        assert "Database error" in str(excinfo.value)


class TestUpdatePatient:
    """Tests for update_patient function."""

    @patch("app.services.patient_service.supabase")
    def test_update_patient_success(self, mock_supabase):
        """Test successful update of patient."""
        from app.services.patient_service import update_patient

        # Arrange
        patient_id = uuid4()
        payload = PatientUpdate(
            first_name="Juan Updated", email="newemail@example.com"
        )

        updated_patient = {
            "id": str(patient_id),
            "rut": "12345678-9",
            "first_name": "Juan Updated",
            "last_name": "Pérez",
            "email": "newemail@example.com",
        }

        mock_response = MagicMock()
        mock_response.data = [updated_patient]
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act
        result = update_patient(patient_id, payload)

        # Assert
        assert result == updated_patient
        mock_supabase.table.assert_called_with("Patient")

    @patch("app.services.patient_service.get_patient_by_id")
    @patch("app.services.patient_service.supabase")
    def test_update_patient_no_changes(self, mock_supabase, mock_get_patient):
        """Test update patient when no fields to update."""
        from app.services.patient_service import update_patient

        # Arrange
        patient_id = uuid4()
        payload = PatientUpdate()  # No fields set

        existing_patient = {
            "id": str(patient_id),
            "rut": "12345678-9",
            "first_name": "Juan",
            "last_name": "Pérez",
        }
        mock_get_patient.return_value = existing_patient

        # Act
        result = update_patient(patient_id, payload)

        # Assert
        assert result == existing_patient
        mock_get_patient.assert_called_once_with(patient_id)
        # Should not call update if no changes
        mock_supabase.table().update.assert_not_called()

    @patch("app.services.patient_service.supabase")
    def test_update_patient_no_data_returned(self, mock_supabase):
        """Test update patient when response has no data."""
        from app.services.patient_service import update_patient

        # Arrange
        patient_id = uuid4()
        payload = PatientUpdate(first_name="Juan Updated")

        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            update_patient(patient_id, payload)
        assert "No se pudo actualizar el paciente" in str(excinfo.value)

    @patch("app.services.patient_service.supabase")
    def test_update_patient_error(self, mock_supabase):
        """Test update patient when an error occurs."""
        from app.services.patient_service import update_patient

        # Arrange
        patient_id = uuid4()
        payload = PatientUpdate(first_name="Juan Updated")

        mock_supabase.table().update().eq().execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            update_patient(patient_id, payload)
        assert "Database error" in str(excinfo.value)
