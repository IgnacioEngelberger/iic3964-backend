"""Tests for doctor endpoints."""

from unittest.mock import patch


class TestResidentDoctorsEndpoint:
    """Tests for GET /v1/doctors/resident-doctors endpoint."""

    @patch("app.services.doctor_service.supabase")
    def test_get_resident_doctors_success(self, mock_supabase, client):
        """Test successful retrieval of resident doctors."""
        # Arrange
        mock_doctors = [
            {
                "id": "doctor-res-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan.perez@hospital.cl",
                "phone": "+56912345678",
            },
            {
                "id": "doctor-res-2",
                "first_name": "María",
                "last_name": "González",
                "email": "maria.gonzalez@hospital.cl",
                "phone": "+56987654321",
            },
        ]

        # Mock the Supabase query chain
        mock_supabase.table().select().eq().eq().order().execute.return_value.data = (
            mock_doctors
        )

        # Act
        response = client.get("/v1/doctors/resident-doctors")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "doctors" in data
        assert len(data["doctors"]) == 2
        assert data["doctors"][0]["first_name"] == "Juan"
        assert data["doctors"][1]["first_name"] == "María"

    @patch("app.services.doctor_service.supabase")
    def test_get_resident_doctors_empty_list(self, mock_supabase, client):
        """Test when no resident doctors exist."""
        # Arrange
        mock_supabase.table().select().eq().eq().order().execute.return_value.data = []

        # Act
        response = client.get("/v1/doctors/resident-doctors")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "doctors" in data
        assert data["doctors"] == []

    @patch("app.services.doctor_service.supabase")
    def test_get_resident_doctors_error(self, mock_supabase, client):
        """Test error handling when database query fails."""
        # Arrange - make the mock raise an exception
        mock_supabase.table().select().eq().eq().order().execute.side_effect = (
            Exception("Database connection failed")
        )

        # Act
        response = client.get("/v1/doctors/resident-doctors")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error al obtener médicos residentes"


class TestSupervisorDoctorsEndpoint:
    """Tests for GET /v1/doctors/supervisor-doctors endpoint."""

    @patch("app.services.doctor_service.supabase")
    def test_get_supervisor_doctors_success(self, mock_supabase, client):
        """Test successful retrieval of supervisor doctors."""
        # Arrange
        mock_doctors = [
            {
                "id": "doctor-sup-1",
                "first_name": "Carlos",
                "last_name": "Ramírez",
                "email": "carlos.ramirez@hospital.cl",
                "phone": "+56998765432",
            },
            {
                "id": "doctor-sup-2",
                "first_name": "Ana",
                "last_name": "Silva",
                "email": "ana.silva@hospital.cl",
                "phone": "+56923456789",
            },
        ]

        # Mock the Supabase query chain
        mock_supabase.table().select().eq().eq().order().execute.return_value.data = (
            mock_doctors
        )

        # Act
        response = client.get("/v1/doctors/supervisor-doctors")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "doctors" in data
        assert len(data["doctors"]) == 2
        assert data["doctors"][0]["first_name"] == "Carlos"
        assert data["doctors"][1]["first_name"] == "Ana"

    @patch("app.services.doctor_service.supabase")
    def test_get_supervisor_doctors_empty_list(self, mock_supabase, client):
        """Test when no supervisor doctors exist."""
        # Arrange
        mock_supabase.table().select().eq().eq().order().execute.return_value.data = []

        # Act
        response = client.get("/v1/doctors/supervisor-doctors")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "doctors" in data
        assert data["doctors"] == []

    @patch("app.services.doctor_service.supabase")
    def test_get_supervisor_doctors_error(self, mock_supabase, client):
        """Test error handling when database query fails."""
        # Arrange - make the mock raise an exception
        mock_supabase.table().select().eq().eq().order().execute.side_effect = (
            Exception("Database connection failed")
        )

        # Act
        response = client.get("/v1/doctors/supervisor-doctors")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error al obtener médicos supervisores"


class TestGetDoctorsEndpoint:
    @patch("app.services.doctor_service.supabase")
    def test_get_doctors_success(self, mock_supabase, client):
        """Test successful retrieval of both resident and supervisor doctors."""
        # Arrange
        mock_residents = [
            {
                "id": "doctor-res-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan.perez@hospital.cl",
                "phone": "+56912345678",
            }
        ]

        mock_supervisors = [
            {
                "id": "doctor-sup-1",
                "first_name": "Carlos",
                "last_name": "Ramírez",
                "email": "carlos.ramirez@hospital.cl",
                "phone": "+56998765432",
            }
        ]

        # Mock both queries - first call returns residents, second returns supervisors
        mock_supabase.table().select().eq().eq().order().execute.return_value.data = (
            mock_residents
        )

        # Create a side_effect to return different data for each call
        def mock_execute():
            class MockResponse:
                data = None

            response = MockResponse()
            # Alternate between resident and supervisor data
            if not hasattr(mock_execute, "call_count"):
                mock_execute.call_count = 0
            if mock_execute.call_count == 0:
                response.data = mock_residents
            else:
                response.data = mock_supervisors
            mock_execute.call_count += 1
            return response

        mock_supabase.table().select().eq().eq().order().execute.side_effect = (
            mock_execute
        )

        # Act
        response = client.get("/v1/doctors/get-doctors")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "resident" in data
        assert "supervisor" in data
        assert len(data["resident"]) == 1
        assert len(data["supervisor"]) == 1
        assert data["resident"][0]["first_name"] == "Juan"
        assert data["supervisor"][0]["first_name"] == "Carlos"

    @patch("app.services.doctor_service.supabase")
    def test_get_doctors_empty_lists(self, mock_supabase, client):
        """Test when no doctors exist."""
        # Arrange
        mock_supabase.table().select().eq().eq().order().execute.return_value.data = []

        # Act
        response = client.get("/v1/doctors/get-doctors")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "resident" in data
        assert "supervisor" in data
        assert data["resident"] == []
        assert data["supervisor"] == []

    @patch("app.services.doctor_service.supabase")
    def test_get_doctors_error(self, mock_supabase, client):
        """Test error handling when database query fails."""
        # Arrange - make the mock raise an exception
        mock_supabase.table().select().eq().eq().order().execute.side_effect = (
            Exception("Database connection failed")
        )

        # Act
        response = client.get("/v1/doctors/get-doctors")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error al obtener médicos"
