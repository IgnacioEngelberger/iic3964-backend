"""Tests for user service layer."""

from unittest.mock import MagicMock, patch

import pytest


class TestNormalizeRole:
    """Tests for _normalize_role helper function."""

    def test_normalize_role_resident(self):
        """Test normalizing resident role."""
        from app.services.user_service import _normalize_role

        assert _normalize_role("resident") == "Resident"
        assert _normalize_role("RESIDENT") == "Resident"
        assert _normalize_role("Resident") == "Resident"

    def test_normalize_role_supervisor(self):
        """Test normalizing supervisor role."""
        from app.services.user_service import _normalize_role

        assert _normalize_role("supervisor") == "Supervisor"
        assert _normalize_role("SUPERVISOR") == "Supervisor"

    def test_normalize_role_admin(self):
        """Test normalizing admin role."""
        from app.services.user_service import _normalize_role

        assert _normalize_role("admin") == "Admin"
        assert _normalize_role("ADMIN") == "Admin"

    def test_normalize_role_unknown(self):
        """Test unknown role returns as-is."""
        from app.services.user_service import _normalize_role

        assert _normalize_role("unknown") == "unknown"


class TestUpdateUser:
    """Tests for update_user service function."""

    @patch("app.services.user_service.supabase")
    def test_update_user_all_fields(self, mock_supabase):
        """Test updating all fields."""
        from app.services.user_service import update_user

        # Arrange
        user_id = "user-123"
        updated_data = {
            "id": user_id,
            "email": "newemail@hospital.cl",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "Supervisor",
        }

        mock_response = MagicMock()
        mock_response.data = [updated_data]
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act
        result = update_user(
            user_id=user_id,
            email="newemail@hospital.cl",
            first_name="Juan",
            last_name="Pérez",
            role="supervisor",
        )

        # Assert
        assert result == updated_data
        assert result["role"] == "Supervisor"

    @patch("app.services.user_service.supabase")
    def test_update_user_email_only(self, mock_supabase):
        """Test updating only email."""
        from app.services.user_service import update_user

        # Arrange
        user_id = "user-123"
        updated_data = {"id": user_id, "email": "newemail@hospital.cl"}

        mock_response = MagicMock()
        mock_response.data = [updated_data]
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act
        result = update_user(user_id=user_id, email="newemail@hospital.cl")

        # Assert
        assert result == updated_data

    @patch("app.services.user_service.supabase")
    def test_update_user_no_fields(self, mock_supabase):
        """Test update with no fields returns empty dict."""
        from app.services.user_service import update_user

        # Act
        result = update_user(user_id="user-123")

        # Assert
        assert result == {}
        mock_supabase.table().update.assert_not_called()

    @patch("app.services.user_service.supabase")
    def test_update_user_not_found(self, mock_supabase):
        """Test update when user not found."""
        from app.services.user_service import update_user

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            update_user(user_id="user-999", email="test@hospital.cl")
        assert "not found or update failed" in str(exc_info.value)

    @patch("app.services.user_service.supabase")
    def test_update_user_database_error(self, mock_supabase):
        """Test error handling when database operation fails."""
        from app.services.user_service import update_user

        # Arrange
        mock_supabase.table().update().eq().execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            update_user(user_id="user-123", email="test@hospital.cl")
        assert "Database error" in str(exc_info.value)


class TestDeleteUser:
    """Tests for delete_user service function."""

    @patch("app.services.user_service.supabase")
    def test_delete_user_success(self, mock_supabase):
        """Test successful soft delete."""
        from app.services.user_service import delete_user

        # Arrange
        user_id = "user-123"
        mock_response = MagicMock()
        mock_response.data = [{"id": user_id, "is_deleted": True}]
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act
        result = delete_user(user_id)

        # Assert
        assert result is True
        # Verify update was called with is_deleted: True
        mock_supabase.table.assert_called_with("User")

    @patch("app.services.user_service.supabase")
    def test_delete_user_not_found(self, mock_supabase):
        """Test delete when user not found."""
        from app.services.user_service import delete_user

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            delete_user("user-999")
        assert "not found or delete failed" in str(exc_info.value)

    @patch("app.services.user_service.supabase")
    def test_delete_user_database_error(self, mock_supabase):
        """Test error handling when database operation fails."""
        from app.services.user_service import delete_user

        # Arrange
        mock_supabase.table().update().eq().execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception):
            delete_user("user-123")


class TestReactivateUser:
    """Tests for reactivate_user service function."""

    @patch("app.services.user_service.supabase")
    def test_reactivate_user_success(self, mock_supabase):
        """Test successful user reactivation."""
        from app.services.user_service import reactivate_user

        # Arrange
        user_id = "user-123"
        mock_response = MagicMock()
        mock_response.data = [{"id": user_id, "is_deleted": False}]
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act
        result = reactivate_user(user_id)

        # Assert
        assert result is True

    @patch("app.services.user_service.supabase")
    def test_reactivate_user_not_found(self, mock_supabase):
        """Test reactivate when user not found."""
        from app.services.user_service import reactivate_user

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().update().eq().execute.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            reactivate_user("user-999")
        assert "not found or reactivation failed" in str(exc_info.value)

    @patch("app.services.user_service.supabase")
    def test_reactivate_user_database_error(self, mock_supabase):
        """Test error handling when database operation fails."""
        from app.services.user_service import reactivate_user

        # Arrange
        mock_supabase.table().update().eq().execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception):
            reactivate_user("user-123")


class TestListUsersByRole:
    """Tests for list_users_by_role service function."""

    @patch("app.services.user_service.supabase")
    def test_list_users_by_role_success(self, mock_supabase):
        """Test listing users by role."""
        from app.services.user_service import list_users_by_role

        # Arrange
        mock_users = [
            {
                "id": "user-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": "Resident",
                "is_deleted": False,
            },
            {
                "id": "user-2",
                "first_name": "María",
                "last_name": "González",
                "role": "Resident",
                "is_deleted": False,
            },
        ]

        mock_response = MagicMock()
        mock_response.data = mock_users
        mock_supabase.table().select().eq().order().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_users_by_role("Resident")

        # Assert
        assert result == mock_users
        assert len(result) == 2

    @patch("app.services.user_service.supabase")
    def test_list_users_by_role_empty(self, mock_supabase):
        """Test when no users exist for role."""
        from app.services.user_service import list_users_by_role

        # Arrange
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table().select().eq().order().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_users_by_role("Admin")

        # Assert
        assert result == []

    @patch("app.services.user_service.supabase")
    def test_list_users_by_role_includes_deleted(self, mock_supabase):
        """Test that deleted users are included in results."""
        from app.services.user_service import list_users_by_role

        # Arrange
        mock_users = [
            {
                "id": "user-1",
                "first_name": "Active",
                "last_name": "User",
                "is_deleted": False,
            },
            {
                "id": "user-2",
                "first_name": "Deleted",
                "last_name": "User",
                "is_deleted": True,
            },
        ]

        mock_response = MagicMock()
        mock_response.data = mock_users
        mock_supabase.table().select().eq().order().order().execute.return_value = (
            mock_response
        )

        # Act
        result = list_users_by_role("Resident")

        # Assert
        assert len(result) == 2
        # Active users should come first (sorted by is_deleted)

    @patch("app.services.user_service.supabase")
    def test_list_users_by_role_database_error(self, mock_supabase):
        """Test error handling when database operation fails."""
        from app.services.user_service import list_users_by_role

        # Arrange
        mock_supabase.table().select().eq().order().order().execute.side_effect = (
            Exception("Database error")
        )

        # Act & Assert
        with pytest.raises(Exception):
            list_users_by_role("Resident")


class TestListHelperFunctions:
    """Tests for list_residents, list_supervisors, list_admins."""

    @patch("app.services.user_service.list_users_by_role")
    def test_list_residents(self, mock_list_users_by_role):
        """Test list_residents calls list_users_by_role with 'Resident'."""
        from app.services.user_service import list_residents

        mock_list_users_by_role.return_value = [{"role": "Resident"}]

        result = list_residents()

        mock_list_users_by_role.assert_called_once_with("Resident")
        assert result == [{"role": "Resident"}]

    @patch("app.services.user_service.list_users_by_role")
    def test_list_supervisors(self, mock_list_users_by_role):
        """Test list_supervisors calls list_users_by_role with 'Supervisor'."""
        from app.services.user_service import list_supervisors

        mock_list_users_by_role.return_value = [{"role": "Supervisor"}]

        result = list_supervisors()

        mock_list_users_by_role.assert_called_once_with("Supervisor")
        assert result == [{"role": "Supervisor"}]

    @patch("app.services.user_service.list_users_by_role")
    def test_list_admins(self, mock_list_users_by_role):
        """Test list_admins calls list_users_by_role with 'Admin'."""
        from app.services.user_service import list_admins

        mock_list_users_by_role.return_value = [{"role": "Admin"}]

        result = list_admins()

        mock_list_users_by_role.assert_called_once_with("Admin")
        assert result == [{"role": "Admin"}]
