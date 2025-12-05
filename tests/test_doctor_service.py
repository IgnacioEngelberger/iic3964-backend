"""Tests for doctor service layer."""

from unittest.mock import MagicMock, patch

import pytest


class TestCreateDoctorService:
    """Tests for create_doctor service function."""

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_success_resident(self, mock_supabase):
        """Test successful creation of a resident doctor."""
        from app.services.doctor_service import create_doctor

        # Arrange
        doctor_id = "doctor-123"
        email = "test@hospital.cl"
        first_name = "Juan"
        last_name = "Pérez"
        role = "resident"

        expected_payload = {
            "id": doctor_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": "Resident",  # Normalized
            "is_deleted": False,
        }

        mock_response = MagicMock()
        mock_response.data = [expected_payload]
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        result = create_doctor(doctor_id, email, first_name, last_name, role)

        # Assert
        assert result == expected_payload
        assert result["role"] == "Resident"
        mock_supabase.table.assert_called_with("User")

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_success_supervisor(self, mock_supabase):
        """Test successful creation of a supervisor doctor."""
        from app.services.doctor_service import create_doctor

        # Arrange
        doctor_id = "doctor-456"
        email = "supervisor@hospital.cl"
        first_name = "María"
        last_name = "González"
        role = "supervisor"

        expected_payload = {
            "id": doctor_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": "Supervisor",  # Normalized
            "is_deleted": False,
        }

        mock_response = MagicMock()
        mock_response.data = [expected_payload]
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        result = create_doctor(doctor_id, email, first_name, last_name, role)

        # Assert
        assert result == expected_payload
        assert result["role"] == "Supervisor"

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_success_admin(self, mock_supabase):
        """Test successful creation of an admin doctor."""
        from app.services.doctor_service import create_doctor

        # Arrange
        doctor_id = "doctor-789"
        email = "admin@hospital.cl"
        first_name = "Carlos"
        last_name = "Ramírez"
        role = "admin"

        expected_payload = {
            "id": doctor_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": "Admin",  # Normalized
            "is_deleted": False,
        }

        mock_response = MagicMock()
        mock_response.data = [expected_payload]
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        result = create_doctor(doctor_id, email, first_name, last_name, role)

        # Assert
        assert result == expected_payload
        assert result["role"] == "Admin"

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_role_normalization(self, mock_supabase):
        """Test that roles are normalized to title case."""
        from app.services.doctor_service import create_doctor

        # Arrange - test with uppercase role
        doctor_id = "doctor-999"
        email = "test@hospital.cl"
        first_name = "Test"
        last_name = "Doctor"
        role = "RESIDENT"  # Uppercase

        expected_payload = {
            "id": doctor_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": "Resident",  # Should be normalized
            "is_deleted": False,
        }

        mock_response = MagicMock()
        mock_response.data = [expected_payload]
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        result = create_doctor(doctor_id, email, first_name, last_name, role)

        # Assert
        assert result["role"] == "Resident"

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_unknown_role_defaults_to_resident(self, mock_supabase):
        """Test that unknown roles default to Resident."""
        from app.services.doctor_service import create_doctor

        # Arrange - test with unknown role
        doctor_id = "doctor-000"
        email = "unknown@hospital.cl"
        first_name = "Unknown"
        last_name = "Role"
        role = "unknown_role"  # Not in mapping

        expected_payload = {
            "id": doctor_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": "Resident",  # Default
            "is_deleted": False,
        }

        mock_response = MagicMock()
        mock_response.data = [expected_payload]
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        result = create_doctor(doctor_id, email, first_name, last_name, role)

        # Assert
        assert result["role"] == "Resident"

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_no_data_returned(self, mock_supabase):
        """Test error when Supabase returns no data."""
        from app.services.doctor_service import create_doctor

        # Arrange
        doctor_id = "doctor-fail"
        email = "fail@hospital.cl"
        first_name = "Fail"
        last_name = "Test"
        role = "resident"

        mock_response = MagicMock()
        mock_response.data = None  # No data returned
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            create_doctor(doctor_id, email, first_name, last_name, role)
        assert "No se pudo insertar el doctor en la tabla User" in str(exc_info.value)

    @patch("app.services.doctor_service.supabase")
    def test_create_doctor_database_error(self, mock_supabase):
        """Test error handling when database operation fails."""
        from app.services.doctor_service import create_doctor

        # Arrange
        doctor_id = "doctor-error"
        email = "error@hospital.cl"
        first_name = "Error"
        last_name = "Test"
        role = "resident"

        # Make the mock raise an exception
        mock_supabase.table().insert().execute.side_effect = Exception(
            "Database connection failed"
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            create_doctor(doctor_id, email, first_name, last_name, role)
        assert "Database connection failed" in str(exc_info.value)


class TestListResidentDoctorsService:
    """Tests for list_resident_doctors service function."""

    @patch("app.services.doctor_service.supabase")
    def test_list_resident_doctors_success(self, mock_supabase):
        """Test successful retrieval of resident doctors."""
        from app.services.doctor_service import list_resident_doctors

        # Arrange
        mock_doctors = [
            {
                "id": "doctor-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan@hospital.cl",
                "phone": "+56912345678",
            }
        ]

        mock_response = MagicMock()
        mock_response.data = mock_doctors
        mock_supabase.table().select().eq().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_resident_doctors()

        # Assert
        assert result == mock_doctors

    @patch("app.services.doctor_service.supabase")
    def test_list_resident_doctors_returns_empty_on_none(self, mock_supabase):
        """Test that None data returns empty list."""
        from app.services.doctor_service import list_resident_doctors

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().select().eq().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_resident_doctors()

        # Assert
        assert result == []

    @patch("app.services.doctor_service.supabase")
    def test_list_resident_doctors_error(self, mock_supabase):
        """Test error handling when database query fails."""
        from app.services.doctor_service import list_resident_doctors

        # Arrange
        mock_supabase.table().select().eq().eq().order().execute.side_effect = (
            Exception("Database error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            list_resident_doctors()
        assert "Database error" in str(exc_info.value)


class TestListSupervisorDoctorsService:
    """Tests for list_supervisor_doctors service function."""

    @patch("app.services.doctor_service.supabase")
    def test_list_supervisor_doctors_success(self, mock_supabase):
        """Test successful retrieval of supervisor doctors."""
        from app.services.doctor_service import list_supervisor_doctors

        # Arrange
        mock_doctors = [
            {
                "id": "doctor-1",
                "first_name": "Carlos",
                "last_name": "Ramírez",
                "email": "carlos@hospital.cl",
                "phone": "+56998765432",
            }
        ]

        mock_response = MagicMock()
        mock_response.data = mock_doctors
        mock_supabase.table().select().eq().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_supervisor_doctors()

        # Assert
        assert result == mock_doctors

    @patch("app.services.doctor_service.supabase")
    def test_list_supervisor_doctors_returns_empty_on_none(self, mock_supabase):
        """Test that None data returns empty list."""
        from app.services.doctor_service import list_supervisor_doctors

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().select().eq().eq().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_supervisor_doctors()

        # Assert
        assert result == []

    @patch("app.services.doctor_service.supabase")
    def test_list_supervisor_doctors_error(self, mock_supabase):
        """Test error handling when database query fails."""
        from app.services.doctor_service import list_supervisor_doctors

        # Arrange
        mock_supabase.table().select().eq().eq().order().execute.side_effect = (
            Exception("Database error")
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            list_supervisor_doctors()
        assert "Database error" in str(exc_info.value)
