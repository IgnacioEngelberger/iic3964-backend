"""Tests for metric service layer."""

from unittest.mock import MagicMock, patch


class TestCalculatePercentage:
    """Tests for _calculate_percentage helper function."""

    def test_calculate_percentage_normal(self):
        """Test normal percentage calculation."""
        from app.services.metric_service import _calculate_percentage

        result = _calculate_percentage(25, 100)
        assert result == 25.0

    def test_calculate_percentage_zero_total(self):
        """Test division by zero returns 0.0."""
        from app.services.metric_service import _calculate_percentage

        result = _calculate_percentage(10, 0)
        assert result == 0.0

    def test_calculate_percentage_rounding(self):
        """Test rounding to 1 decimal place."""
        from app.services.metric_service import _calculate_percentage

        result = _calculate_percentage(1, 3)
        assert result == 33.3  # 33.333... rounded to 1 decimal


class TestProcessRowsToStats:
    """Tests for _process_rows_to_stats function."""

    def test_process_rows_empty_list(self):
        """Test processing empty list returns zero metrics."""
        from app.services.metric_service import _process_rows_to_stats

        result = _process_rows_to_stats([], "user-123", "Juan Pérez")

        assert result.id == "user-123"
        assert result.name == "Juan Pérez"
        assert result.total_episodes == 0
        assert result.total_urgency_law == 0
        assert result.percent_urgency_law_rejected == 0.0
        assert result.total_ai_yes == 0
        assert result.percent_ai_yes_rejected == 0.0
        assert result.total_ai_no_medic_yes == 0
        assert result.percent_ai_no_medic_yes_rejected == 0.0

    def test_process_rows_with_urgency_law(self):
        """Test processing rows with urgency law cases."""
        from app.services.metric_service import _process_rows_to_stats

        rows = [
            {"applies_urgency_law": True, "pertinencia": True, "ai_result": True},
            {"applies_urgency_law": True, "pertinencia": False, "ai_result": True},
            {"applies_urgency_law": False, "pertinencia": None, "ai_result": False},
        ]

        result = _process_rows_to_stats(rows, "user-123", "Juan Pérez")

        assert result.total_episodes == 3
        assert result.total_urgency_law == 2
        assert result.percent_urgency_law_rejected == 50.0  # 1 out of 2

    def test_process_rows_ai_yes_cases(self):
        """Test processing AI yes cases."""
        from app.services.metric_service import _process_rows_to_stats

        rows = [
            {"applies_urgency_law": True, "pertinencia": True, "ai_result": True},
            {"applies_urgency_law": False, "pertinencia": False, "ai_result": True},
            {"applies_urgency_law": False, "pertinencia": None, "ai_result": False},
        ]

        result = _process_rows_to_stats(rows, "user-123", "Juan Pérez")

        assert result.total_ai_yes == 2
        assert result.percent_ai_yes_rejected == 50.0  # 1 rejected out of 2

    def test_process_rows_ai_no_medic_yes(self):
        """Test AI said NO but medic said YES cases."""
        from app.services.metric_service import _process_rows_to_stats

        rows = [
            # AI NO, Medic YES, approved
            {"applies_urgency_law": True, "pertinencia": True, "ai_result": False},
            # AI NO, Medic YES, rejected
            {"applies_urgency_law": True, "pertinencia": False, "ai_result": False},
            # AI YES, Medic YES - not counted
            {"applies_urgency_law": True, "pertinencia": True, "ai_result": True},
        ]

        result = _process_rows_to_stats(rows, "user-123", "Juan Pérez")

        assert result.total_ai_no_medic_yes == 2
        assert result.percent_ai_no_medic_yes_rejected == 50.0  # 1 rejected out of 2

    def test_process_rows_pertinencia_none_not_rejected(self):
        """Test that pertinencia=None is not counted as rejected."""
        from app.services.metric_service import _process_rows_to_stats

        rows = [
            {"applies_urgency_law": True, "pertinencia": None, "ai_result": True},
            {"applies_urgency_law": True, "pertinencia": False, "ai_result": True},
        ]

        result = _process_rows_to_stats(rows, "user-123", "Juan Pérez")

        assert result.total_urgency_law == 2
        # Only 1 rejected (pertinencia=False), None is not rejected
        assert result.percent_urgency_law_rejected == 50.0


class TestGetBaseQuery:
    """Tests for get_base_query helper function."""

    @patch("app.services.metric_service.supabase")
    def test_get_base_query_no_dates(self, mock_supabase):
        """Test base query without date filters."""
        from app.services.metric_service import get_base_query

        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table

        result = get_base_query(None, None)

        mock_supabase.table.assert_called_once_with("ClinicalAttention")
        mock_table.select.assert_called_once()
        assert result == mock_table.select.return_value

    @patch("app.services.metric_service.supabase")
    def test_get_base_query_with_start_date(self, mock_supabase):
        """Test base query with start date filter."""
        from app.services.metric_service import get_base_query

        mock_query = MagicMock()
        mock_supabase.table().select.return_value = mock_query

        get_base_query("2024-01-01", None)

        mock_query.gte.assert_called_once_with("created_at", "2024-01-01T00:00:00")

    @patch("app.services.metric_service.supabase")
    def test_get_base_query_with_end_date(self, mock_supabase):
        """Test base query with end date filter."""
        from app.services.metric_service import get_base_query

        mock_query = MagicMock()
        mock_supabase.table().select.return_value = mock_query

        get_base_query(None, "2024-12-31")

        mock_query.lte.assert_called_once_with("created_at", "2024-12-31T23:59:59")

    @patch("app.services.metric_service.supabase")
    def test_get_base_query_with_both_dates(self, mock_supabase):
        """Test base query with both date filters."""
        from app.services.metric_service import get_base_query

        mock_query = MagicMock()
        mock_gte = MagicMock()
        mock_query.gte.return_value = mock_gte
        mock_supabase.table().select.return_value = mock_query

        get_base_query("2024-01-01", "2024-12-31")

        mock_query.gte.assert_called_once_with("created_at", "2024-01-01T00:00:00")
        mock_gte.lte.assert_called_once_with("created_at", "2024-12-31T23:59:59")


class TestGetAllUsersMetrics:
    """Tests for get_all_users_metrics function."""

    @patch("app.services.metric_service.supabase")
    def test_get_all_users_metrics_no_users(self, mock_supabase):
        """Test when no users exist."""
        from app.services.metric_service import get_all_users_metrics

        # Mock users query
        mock_users_response = MagicMock()
        mock_users_response.data = []

        # Mock attentions query
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = []

        mock_supabase.table().select().eq().execute.return_value = mock_users_response
        mock_supabase.table().select().execute.return_value = mock_attentions_response

        result = get_all_users_metrics()

        assert result == []

    @patch("app.services.metric_service.get_base_query")
    @patch("app.services.metric_service.supabase")
    def test_get_all_users_metrics_users_with_no_attentions(
        self, mock_supabase, mock_get_base_query
    ):
        """Test users with no clinical attentions."""
        from app.services.metric_service import get_all_users_metrics

        # Mock users
        mock_users_response = MagicMock()
        mock_users_response.data = [
            {
                "id": "user-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": "Resident",
            }
        ]

        # Mock no attentions
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = []

        mock_supabase.table().select().eq().execute.return_value = mock_users_response

        mock_query = MagicMock()
        mock_query.execute.return_value = mock_attentions_response
        mock_get_base_query.return_value = mock_query

        result = get_all_users_metrics()

        assert len(result) == 1
        assert result[0].id == "user-1"
        assert result[0].name == "Juan Pérez"
        assert result[0].total_episodes == 0

    @patch("app.services.metric_service.get_base_query")
    @patch("app.services.metric_service.supabase")
    def test_get_all_users_metrics_with_attentions(
        self, mock_supabase, mock_get_base_query
    ):
        """Test users with clinical attentions."""
        from app.services.metric_service import get_all_users_metrics

        # Mock users
        mock_users_response = MagicMock()
        mock_users_response.data = [
            {
                "id": "user-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": "Resident",
            }
        ]

        # Mock attentions
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = [
            {
                "resident_doctor_id": "user-1",
                "applies_urgency_law": True,
                "pertinencia": True,
                "ai_result": True,
            },
            {
                "resident_doctor_id": "user-1",
                "applies_urgency_law": False,
                "pertinencia": None,
                "ai_result": False,
            },
        ]

        mock_supabase.table().select().eq().execute.return_value = mock_users_response

        mock_query = MagicMock()
        mock_query.execute.return_value = mock_attentions_response
        mock_get_base_query.return_value = mock_query

        result = get_all_users_metrics()

        assert len(result) == 1
        assert result[0].id == "user-1"
        assert result[0].name == "Juan Pérez"
        assert result[0].total_episodes == 2

    @patch("app.services.metric_service.get_base_query")
    @patch("app.services.metric_service.supabase")
    def test_get_all_users_metrics_sorted_by_name(
        self, mock_supabase, mock_get_base_query
    ):
        """Test that results are sorted by name."""
        from app.services.metric_service import get_all_users_metrics

        # Mock users
        mock_users_response = MagicMock()
        mock_users_response.data = [
            {
                "id": "user-1",
                "first_name": "Zoe",
                "last_name": "Zapata",
                "role": "Resident",
            },
            {
                "id": "user-2",
                "first_name": "Ana",
                "last_name": "Álvarez",
                "role": "Supervisor",
            },
        ]

        # Mock no attentions
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = []

        mock_supabase.table().select().eq().execute.return_value = mock_users_response

        mock_query = MagicMock()
        mock_query.execute.return_value = mock_attentions_response
        mock_get_base_query.return_value = mock_query

        result = get_all_users_metrics()

        assert len(result) == 2
        # Should be sorted alphabetically by name
        assert result[0].name == "Ana Álvarez"
        assert result[1].name == "Zoe Zapata"


class TestGetSingleUserMetrics:
    """Tests for get_single_user_metrics function."""

    @patch("app.services.metric_service.get_base_query")
    @patch("app.services.metric_service.supabase")
    def test_get_single_user_metrics_user_exists(
        self, mock_supabase, mock_get_base_query
    ):
        """Test getting metrics for an existing user."""
        from app.services.metric_service import get_single_user_metrics

        # Mock user info
        mock_user_response = MagicMock()
        mock_user_response.data = {"first_name": "Juan", "last_name": "Pérez"}

        # Mock attentions
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = [
            {
                "applies_urgency_law": True,
                "pertinencia": True,
                "ai_result": True,
            }
        ]

        mock_supabase.table().select().eq().single().execute.return_value = (
            mock_user_response
        )

        mock_query = MagicMock()
        mock_query.eq().execute.return_value = mock_attentions_response
        mock_get_base_query.return_value = mock_query

        result = get_single_user_metrics("user-123")

        assert result.id == "user-123"
        assert result.name == "Juan Pérez"
        assert result.total_episodes == 1

    @patch("app.services.metric_service.get_base_query")
    @patch("app.services.metric_service.supabase")
    def test_get_single_user_metrics_user_not_found(
        self, mock_supabase, mock_get_base_query
    ):
        """Test getting metrics when user doesn't exist."""
        from app.services.metric_service import get_single_user_metrics

        # Mock user not found
        mock_user_response = MagicMock()
        mock_user_response.data = None

        # Mock no attentions
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = []

        mock_supabase.table().select().eq().single().execute.return_value = (
            mock_user_response
        )

        mock_query = MagicMock()
        mock_query.eq().execute.return_value = mock_attentions_response
        mock_get_base_query.return_value = mock_query

        result = get_single_user_metrics("user-unknown")

        assert result.id == "user-unknown"
        assert result.name == "Usuario Desconocido"
        assert result.total_episodes == 0


class TestGetInsuranceMetrics:
    """Tests for get_insurance_metrics function."""

    @patch("app.services.metric_service.supabase")
    def test_get_insurance_metrics_company_exists(self, mock_supabase):
        """Test getting metrics for existing insurance company."""
        from app.services.metric_service import get_insurance_metrics

        # Mock company info
        mock_company_response = MagicMock()
        mock_company_response.data = {"nombre_juridico": "Isapre Test"}

        # Mock patients
        mock_patients_response = MagicMock()
        mock_patients_response.data = [{"id": "patient-1"}, {"id": "patient-2"}]

        # Mock attentions
        mock_attentions_response = MagicMock()
        mock_attentions_response.data = [
            {
                "applies_urgency_law": True,
                "pertinencia": True,
                "ai_result": True,
            }
        ]

        # Setup mock call sequence
        def mock_table_call(table_name):
            mock_table = MagicMock()
            if table_name == "insurance_company":
                mock_table.select().eq().single().execute.return_value = (
                    mock_company_response
                )
            elif table_name == "Patient":
                mock_table.select().eq().execute.return_value = mock_patients_response
            elif table_name == "ClinicalAttention":
                mock_table.select().in_().execute.return_value = (
                    mock_attentions_response
                )
            return mock_table

        mock_supabase.table.side_effect = mock_table_call

        result = get_insurance_metrics(1)

        assert result.id == 1
        assert result.name == "Isapre Test"
        assert result.total_episodes == 1

    @patch("app.services.metric_service.supabase")
    def test_get_insurance_metrics_no_patients(self, mock_supabase):
        """Test insurance company with no patients."""
        from app.services.metric_service import get_insurance_metrics

        # Mock company info
        mock_company_response = MagicMock()
        mock_company_response.data = {"nombre_juridico": "Isapre Sin Pacientes"}

        # Mock no patients
        mock_patients_response = MagicMock()
        mock_patients_response.data = []

        # Setup mock call sequence
        def mock_table_call(table_name):
            mock_table = MagicMock()
            if table_name == "insurance_company":
                mock_table.select().eq().single().execute.return_value = (
                    mock_company_response
                )
            elif table_name == "Patient":
                mock_table.select().eq().execute.return_value = mock_patients_response
            return mock_table

        mock_supabase.table.side_effect = mock_table_call

        result = get_insurance_metrics(1)

        assert result.id == 1
        assert result.name == "Isapre Sin Pacientes"
        assert result.total_episodes == 0
        assert result.total_urgency_law == 0

    @patch("app.services.metric_service.supabase")
    def test_get_insurance_metrics_company_not_found(self, mock_supabase):
        """Test metrics when company doesn't exist."""
        from app.services.metric_service import get_insurance_metrics

        # Mock company not found
        mock_company_response = MagicMock()
        mock_company_response.data = None

        # Mock no patients
        mock_patients_response = MagicMock()
        mock_patients_response.data = []

        # Setup mock call sequence
        def mock_table_call(table_name):
            mock_table = MagicMock()
            if table_name == "insurance_company":
                mock_table.select().eq().single().execute.return_value = (
                    mock_company_response
                )
            elif table_name == "Patient":
                mock_table.select().eq().execute.return_value = mock_patients_response
            return mock_table

        mock_supabase.table.side_effect = mock_table_call

        result = get_insurance_metrics(999)

        assert result.id == 999
        assert result.name == "Desconocida"
        assert result.total_episodes == 0
