"""Tests for patient endpoints."""
from unittest.mock import patch
from uuid import uuid4


class TestGetPatientsEndpoint:
    """Tests for GET /patients endpoint."""

    @patch("app.api.v1.endpoints.patients.patient_service.list_patients")
    def test_get_patients_success(self, mock_list_patients, client):
        """Test successful retrieval of all patients."""
        # Arrange
        mock_patients = [
            {
                "id": str(uuid4()),
                "rut": "12345678-9",
                "first_name": "Juan",
                "last_name": "Pérez",
            },
            {
                "id": str(uuid4()),
                "rut": "98765432-1",
                "first_name": "María",
                "last_name": "González",
            },
        ]
        mock_list_patients.return_value = mock_patients

        # Act
        response = client.get("/v1/patients/patients")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patients" in data
        assert len(data["patients"]) == 2
        assert data["patients"][0]["first_name"] == "Juan"

    @patch("app.api.v1.endpoints.patients.patient_service.list_patients")
    def test_get_patients_empty_list(self, mock_list_patients, client):
        """Test when no patients exist."""
        # Arrange
        mock_list_patients.return_value = []

        # Act
        response = client.get("/v1/patients/patients")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["patients"] == []

    @patch("app.api.v1.endpoints.patients.patient_service.list_patients")
    def test_get_patients_error(self, mock_list_patients, client):
        """Test error handling when service fails."""
        # Arrange
        mock_list_patients.side_effect = Exception("Database error")

        # Act
        response = client.get("/v1/patients/patients")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error al obtener pacientes"


class TestGetPatientEndpoint:
    """Tests for GET /patients/{patient_id} endpoint."""

    @patch("app.api.v1.endpoints.patients.patient_service.get_patient_by_id")
    def test_get_patient_success(self, mock_get_patient, client):
        """Test successful retrieval of single patient."""
        # Arrange
        patient_id = uuid4()
        mock_patient = {
            "id": str(patient_id),
            "rut": "12345678-9",
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "juan@example.com",
        }
        mock_get_patient.return_value = mock_patient

        # Act
        response = client.get(f"/v1/patients/patients/{patient_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(patient_id)
        assert data["first_name"] == "Juan"

    @patch("app.api.v1.endpoints.patients.patient_service.get_patient_by_id")
    def test_get_patient_not_found(self, mock_get_patient, client):
        """Test when patient doesn't exist."""
        # Arrange
        patient_id = uuid4()
        mock_get_patient.return_value = None

        # Act
        response = client.get(f"/v1/patients/patients/{patient_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Paciente no encontrado"


class TestCreatePatientEndpoint:
    """Tests for POST /patients endpoint."""

    @patch("app.api.v1.endpoints.patients.patient_service.create_patient")
    def test_create_patient_success(self, mock_create_patient, client):
        """Test successful patient creation."""
        # Arrange
        payload = {
            "rut": "12345678-9",
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "juan@example.com",
        }
        mock_created = {
            "id": str(uuid4()),
            **payload,
        }
        mock_create_patient.return_value = mock_created

        # Act
        response = client.post("/v1/patients/patients", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["first_name"] == "Juan"

    @patch("app.api.v1.endpoints.patients.patient_service.create_patient")
    def test_create_patient_error(self, mock_create_patient, client):
        """Test error handling when creation fails."""
        # Arrange
        payload = {
            "rut": "12345678-9",
            "first_name": "Juan",
            "last_name": "Pérez",
        }
        mock_create_patient.side_effect = Exception("Duplicate RUT")

        # Act
        response = client.post("/v1/patients/patients", json=payload)

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Error al crear paciente" in data["detail"]


class TestUpdatePatientEndpoint:
    """Tests for PATCH /patients/{patient_id} endpoint."""

    @patch("app.api.v1.endpoints.patients.patient_service.update_patient")
    def test_update_patient_success(self, mock_update_patient, client):
        """Test successful patient update."""
        # Arrange
        patient_id = uuid4()
        payload = {
            "first_name": "Juan Updated",
            "email": "newemail@example.com",
        }
        mock_updated = {
            "id": str(patient_id),
            "rut": "12345678-9",
            "first_name": "Juan Updated",
            "last_name": "Pérez",
            "email": "newemail@example.com",
        }
        mock_update_patient.return_value = mock_updated

        # Act
        response = client.patch(f"/v1/patients/patients/{patient_id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Juan Updated"
        assert data["email"] == "newemail@example.com"
