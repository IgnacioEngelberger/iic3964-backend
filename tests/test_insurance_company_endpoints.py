"""Tests for insurance company endpoints."""

from unittest.mock import patch


class TestListInsuranceCompaniesEndpoint:
    """Tests for GET /v1/insurance_companies endpoint."""

    @patch("app.services.insurance_company_service.list_companies")
    def test_list_companies_success(self, mock_list_companies, client):
        """Test successful retrieval of insurance companies."""
        # Arrange
        mock_response = {
            "count": 2,
            "total": 2,
            "page": 1,
            "page_size": 10,
            "results": [
                {
                    "id": 1,
                    "nombre_juridico": "Isapre Test 1",
                    "nombre_comercial": "Test 1",
                    "rut": "12345678-9",
                },
                {
                    "id": 2,
                    "nombre_juridico": "Isapre Test 2",
                    "nombre_comercial": "Test 2",
                    "rut": "98765432-1",
                },
            ],
        }
        mock_list_companies.return_value = mock_response

        # Act
        response = client.get("/v1/insurance_companies")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["total"] == 2

    @patch("app.services.insurance_company_service.list_companies")
    def test_list_companies_with_pagination(self, mock_list_companies, client):
        """Test list with pagination parameters."""
        # Arrange
        mock_response = {
            "count": 1,
            "total": 50,
            "page": 2,
            "page_size": 20,
            "results": [
                {
                    "id": 1,
                    "nombre_juridico": "Test",
                    "nombre_comercial": None,
                    "rut": None,
                }
            ],
        }
        mock_list_companies.return_value = mock_response

        # Act
        response = client.get("/v1/insurance_companies?page=2&page_size=20")

        # Assert
        assert response.status_code == 200
        mock_list_companies.assert_called_once_with(
            page=2, page_size=20, search=None, order=None
        )

    @patch("app.services.insurance_company_service.list_companies")
    def test_list_companies_with_search(self, mock_list_companies, client):
        """Test list with search parameter."""
        # Arrange
        mock_response = {
            "count": 1,
            "total": 1,
            "page": 1,
            "page_size": 10,
            "results": [
                {
                    "id": 1,
                    "nombre_juridico": "Isapre Encontrada",
                    "nombre_comercial": "Encontrada",
                    "rut": "11111111-1",
                }
            ],
        }
        mock_list_companies.return_value = mock_response

        # Act
        response = client.get("/v1/insurance_companies?search=Encontrada")

        # Assert
        assert response.status_code == 200
        mock_list_companies.assert_called_once_with(
            page=1, page_size=10, search="Encontrada", order=None
        )


class TestGetInsuranceCompanyEndpoint:
    """Tests for GET /v1/insurance_companies/{company_id} endpoint."""

    @patch("app.services.insurance_company_service.get_company")
    def test_get_company_success(self, mock_get_company, client):
        """Test successful retrieval of single company."""
        # Arrange
        company_id = 1
        mock_company = {
            "id": company_id,
            "nombre_juridico": "Isapre Test",
            "nombre_comercial": "Test",
            "rut": "12345678-9",
        }
        mock_get_company.return_value = mock_company

        # Act
        response = client.get(f"/v1/insurance_companies/{company_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == company_id
        assert data["nombre_juridico"] == "Isapre Test"


class TestCreateInsuranceCompanyEndpoint:
    """Tests for POST /v1/insurance_companies endpoint."""

    @patch("app.services.insurance_company_service.create_company")
    def test_create_company_success(self, mock_create_company, client):
        """Test successful creation of insurance company."""
        # Arrange
        payload = {
            "nombre_juridico": "Nueva Isapre",
            "nombre_comercial": "Nueva",
            "rut": "11111111-1",
        }
        mock_created = {
            "id": 5,
            **payload,
        }
        mock_create_company.return_value = mock_created

        # Act
        response = client.post("/v1/insurance_companies", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 5
        assert data["nombre_juridico"] == "Nueva Isapre"


class TestUpdateInsuranceCompanyEndpoint:
    """Tests for PATCH /v1/insurance_companies/{company_id} endpoint."""

    @patch("app.services.insurance_company_service.update_company")
    def test_update_company_success(self, mock_update_company, client):
        """Test successful update of insurance company."""
        # Arrange
        company_id = 1
        payload = {
            "nombre_comercial": "Nombre Actualizado",
        }
        mock_updated = {
            "id": company_id,
            "nombre_juridico": "Original",
            "nombre_comercial": "Nombre Actualizado",
            "rut": "12345678-9",
        }
        mock_update_company.return_value = mock_updated

        # Act
        response = client.patch(f"/v1/insurance_companies/{company_id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_comercial"] == "Nombre Actualizado"


class TestDeleteInsuranceCompanyEndpoint:
    """Tests for DELETE /v1/insurance_companies/{company_id} endpoint."""

    @patch("app.services.insurance_company_service.delete_company")
    def test_delete_company_success(self, mock_delete_company, client):
        """Test successful deletion of insurance company."""
        # Arrange
        company_id = 1
        mock_delete_company.return_value = None

        # Act
        response = client.delete(f"/v1/insurance_companies/{company_id}")

        # Assert
        assert response.status_code == 204
        mock_delete_company.assert_called_once_with(company_id)
