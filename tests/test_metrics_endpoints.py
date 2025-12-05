"""Tests for metrics endpoints."""

from unittest.mock import patch

from app.schemas.metric import MetricStats


class TestGetUsersMetricsEndpoint:
    """Tests for GET /v1/metrics/users endpoint."""

    @patch("app.services.metric_service.get_all_users_metrics")
    def test_get_users_metrics_success(self, mock_get_all_users_metrics, client):
        """Test successful retrieval of all users metrics."""
        # Arrange
        mock_metrics = [
            MetricStats(
                id="user-1",
                name="Juan Pérez",
                total_episodes=10,
                total_urgency_law=5,
                percent_urgency_law_rejected=20.0,
                total_ai_yes=6,
                percent_ai_yes_rejected=16.7,
                total_ai_no_medic_yes=2,
                percent_ai_no_medic_yes_rejected=50.0,
            ),
            MetricStats(
                id="user-2",
                name="María González",
                total_episodes=8,
                total_urgency_law=4,
                percent_urgency_law_rejected=25.0,
                total_ai_yes=3,
                percent_ai_yes_rejected=33.3,
                total_ai_no_medic_yes=1,
                percent_ai_no_medic_yes_rejected=0.0,
            ),
        ]

        mock_get_all_users_metrics.return_value = mock_metrics

        # Act
        response = client.get("/v1/metrics/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Juan Pérez"
        assert data[0]["total_episodes"] == 10
        assert data[1]["name"] == "María González"
        assert data[1]["total_episodes"] == 8

    @patch("app.services.metric_service.get_all_users_metrics")
    def test_get_users_metrics_with_date_filters(
        self, mock_get_all_users_metrics, client
    ):
        """Test users metrics with date range filters."""
        # Arrange
        mock_metrics = [
            MetricStats(
                id="user-1",
                name="Juan Pérez",
                total_episodes=5,
                total_urgency_law=2,
                percent_urgency_law_rejected=0.0,
                total_ai_yes=3,
                percent_ai_yes_rejected=0.0,
                total_ai_no_medic_yes=0,
                percent_ai_no_medic_yes_rejected=0.0,
            )
        ]

        mock_get_all_users_metrics.return_value = mock_metrics

        # Act
        response = client.get(
            "/v1/metrics/users?start_date=2024-01-01&end_date=2024-12-31"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_get_all_users_metrics.assert_called_once_with("2024-01-01", "2024-12-31")

    @patch("app.services.metric_service.get_all_users_metrics")
    def test_get_users_metrics_empty_result(self, mock_get_all_users_metrics, client):
        """Test when no users have metrics."""
        # Arrange
        mock_get_all_users_metrics.return_value = []

        # Act
        response = client.get("/v1/metrics/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @patch("app.services.metric_service.get_all_users_metrics")
    def test_get_users_metrics_error(self, mock_get_all_users_metrics, client):
        """Test error handling when service fails."""
        # Arrange
        mock_get_all_users_metrics.side_effect = Exception("Database connection failed")

        # Act
        response = client.get("/v1/metrics/users")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error calculando métricas de usuarios"


class TestGetUserMetricsEndpoint:
    """Tests for GET /v1/metrics/users/{user_id} endpoint."""

    @patch("app.services.metric_service.get_single_user_metrics")
    def test_get_user_metrics_success(self, mock_get_single_user_metrics, client):
        """Test successful retrieval of single user metrics."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_metric = MetricStats(
            id=user_id,
            name="Juan Pérez",
            total_episodes=15,
            total_urgency_law=8,
            percent_urgency_law_rejected=12.5,
            total_ai_yes=9,
            percent_ai_yes_rejected=11.1,
            total_ai_no_medic_yes=3,
            percent_ai_no_medic_yes_rejected=33.3,
        )

        mock_get_single_user_metrics.return_value = mock_metric

        # Act
        response = client.get(f"/v1/metrics/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Juan Pérez"
        assert data["total_episodes"] == 15

    @patch("app.services.metric_service.get_single_user_metrics")
    def test_get_user_metrics_with_dates(self, mock_get_single_user_metrics, client):
        """Test user metrics with date filters."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_metric = MetricStats(
            id=user_id,
            name="Juan Pérez",
            total_episodes=5,
            total_urgency_law=2,
            percent_urgency_law_rejected=0.0,
            total_ai_yes=3,
            percent_ai_yes_rejected=0.0,
            total_ai_no_medic_yes=1,
            percent_ai_no_medic_yes_rejected=0.0,
        )

        mock_get_single_user_metrics.return_value = mock_metric

        # Act
        response = client.get(
            f"/v1/metrics/users/{user_id}?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_episodes"] == 5
        mock_get_single_user_metrics.assert_called_once_with(
            user_id, "2024-01-01", "2024-01-31"
        )

    @patch("app.services.metric_service.get_single_user_metrics")
    def test_get_user_metrics_user_not_found(
        self, mock_get_single_user_metrics, client
    ):
        """Test metrics for non-existent user (returns zero metrics)."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_metric = MetricStats(
            id=user_id,
            name="Usuario Desconocido",
            total_episodes=0,
            total_urgency_law=0,
            percent_urgency_law_rejected=0.0,
            total_ai_yes=0,
            percent_ai_yes_rejected=0.0,
            total_ai_no_medic_yes=0,
            percent_ai_no_medic_yes_rejected=0.0,
        )

        mock_get_single_user_metrics.return_value = mock_metric

        # Act
        response = client.get(f"/v1/metrics/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Usuario Desconocido"
        assert data["total_episodes"] == 0

    @patch("app.services.metric_service.get_single_user_metrics")
    def test_get_user_metrics_error(self, mock_get_single_user_metrics, client):
        """Test error handling when service fails."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_get_single_user_metrics.side_effect = Exception("Database error")

        # Act
        response = client.get(f"/v1/metrics/users/{user_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error calculando métricas del usuario"


class TestGetInsuranceMetricsEndpoint:
    """Tests for GET /v1/metrics/insurance_companies/{company_id} endpoint."""

    @patch("app.services.metric_service.get_insurance_metrics")
    def test_get_insurance_metrics_success(self, mock_get_insurance_metrics, client):
        """Test successful retrieval of insurance company metrics."""
        # Arrange
        company_id = 1
        mock_metric = MetricStats(
            id=company_id,
            name="Isapre Test",
            total_episodes=25,
            total_urgency_law=12,
            percent_urgency_law_rejected=16.7,
            total_ai_yes=15,
            percent_ai_yes_rejected=13.3,
            total_ai_no_medic_yes=5,
            percent_ai_no_medic_yes_rejected=20.0,
        )

        mock_get_insurance_metrics.return_value = mock_metric

        # Act
        response = client.get(f"/v1/metrics/insurance_companies/{company_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == company_id
        assert data["name"] == "Isapre Test"
        assert data["total_episodes"] == 25

    @patch("app.services.metric_service.get_insurance_metrics")
    def test_get_insurance_metrics_with_dates(self, mock_get_insurance_metrics, client):
        """Test insurance metrics with date filters."""
        # Arrange
        company_id = 1
        mock_metric = MetricStats(
            id=company_id,
            name="Isapre Test",
            total_episodes=10,
            total_urgency_law=5,
            percent_urgency_law_rejected=0.0,
            total_ai_yes=6,
            percent_ai_yes_rejected=0.0,
            total_ai_no_medic_yes=2,
            percent_ai_no_medic_yes_rejected=0.0,
        )

        mock_get_insurance_metrics.return_value = mock_metric

        # Act
        url = (
            f"/v1/metrics/insurance_companies/{company_id}"
            f"?start_date=2024-01-01&end_date=2024-12-31"
        )
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_episodes"] == 10
        mock_get_insurance_metrics.assert_called_once_with(
            company_id, "2024-01-01", "2024-12-31"
        )

    @patch("app.services.metric_service.get_insurance_metrics")
    def test_get_insurance_metrics_no_patients(
        self, mock_get_insurance_metrics, client
    ):
        """Test insurance company with no patients."""
        # Arrange
        company_id = 999
        mock_metric = MetricStats(
            id=company_id,
            name="Isapre Sin Pacientes",
            total_episodes=0,
            total_urgency_law=0,
            percent_urgency_law_rejected=0.0,
            total_ai_yes=0,
            percent_ai_yes_rejected=0.0,
            total_ai_no_medic_yes=0,
            percent_ai_no_medic_yes_rejected=0.0,
        )

        mock_get_insurance_metrics.return_value = mock_metric

        # Act
        response = client.get(f"/v1/metrics/insurance_companies/{company_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Isapre Sin Pacientes"
        assert data["total_episodes"] == 0

    @patch("app.services.metric_service.get_insurance_metrics")
    def test_get_insurance_metrics_company_not_found(
        self, mock_get_insurance_metrics, client
    ):
        """Test metrics for non-existent insurance company."""
        # Arrange
        company_id = 999
        mock_metric = MetricStats(
            id=company_id,
            name="Desconocida",
            total_episodes=0,
            total_urgency_law=0,
            percent_urgency_law_rejected=0.0,
            total_ai_yes=0,
            percent_ai_yes_rejected=0.0,
            total_ai_no_medic_yes=0,
            percent_ai_no_medic_yes_rejected=0.0,
        )

        mock_get_insurance_metrics.return_value = mock_metric

        # Act
        response = client.get(f"/v1/metrics/insurance_companies/{company_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Desconocida"
        assert data["total_episodes"] == 0

    @patch("app.services.metric_service.get_insurance_metrics")
    def test_get_insurance_metrics_error(self, mock_get_insurance_metrics, client):
        """Test error handling when service fails."""
        # Arrange
        company_id = 1
        mock_get_insurance_metrics.side_effect = Exception("Database error")

        # Act
        response = client.get(f"/v1/metrics/insurance_companies/{company_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error calculando métricas de aseguradora"
