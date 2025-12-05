"""Tests for users endpoints."""

from unittest.mock import patch


class TestGetUsersEndpoint:
    """Tests for GET /v1/users/ endpoint."""

    @patch("app.services.user_service.list_admins")
    @patch("app.services.user_service.list_supervisors")
    @patch("app.services.user_service.list_residents")
    def test_get_users_success(
        self, mock_list_residents, mock_list_supervisors, mock_list_admins, client
    ):
        """Test successful retrieval of all users grouped by role."""
        # Arrange
        mock_residents = [
            {
                "id": "res-1",
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan@hospital.cl",
                "role": "Resident",
            }
        ]
        mock_supervisors = [
            {
                "id": "sup-1",
                "first_name": "María",
                "last_name": "González",
                "email": "maria@hospital.cl",
                "role": "Supervisor",
            }
        ]
        mock_admins = [
            {
                "id": "admin-1",
                "first_name": "Carlos",
                "last_name": "Ramírez",
                "email": "carlos@hospital.cl",
                "role": "Admin",
            }
        ]

        mock_list_residents.return_value = mock_residents
        mock_list_supervisors.return_value = mock_supervisors
        mock_list_admins.return_value = mock_admins

        # Act
        response = client.get("/v1/users/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "resident" in data
        assert "supervisor" in data
        assert "admin" in data
        assert len(data["resident"]) == 1
        assert len(data["supervisor"]) == 1
        assert len(data["admin"]) == 1
        assert data["resident"][0]["first_name"] == "Juan"
        assert data["supervisor"][0]["first_name"] == "María"
        assert data["admin"][0]["first_name"] == "Carlos"

    @patch("app.services.user_service.list_admins")
    @patch("app.services.user_service.list_supervisors")
    @patch("app.services.user_service.list_residents")
    def test_get_users_empty_lists(
        self, mock_list_residents, mock_list_supervisors, mock_list_admins, client
    ):
        """Test when no users exist."""
        # Arrange
        mock_list_residents.return_value = []
        mock_list_supervisors.return_value = []
        mock_list_admins.return_value = []

        # Act
        response = client.get("/v1/users/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["resident"] == []
        assert data["supervisor"] == []
        assert data["admin"] == []

    @patch("app.services.user_service.list_admins")
    @patch("app.services.user_service.list_supervisors")
    @patch("app.services.user_service.list_residents")
    def test_get_users_error(
        self, mock_list_residents, mock_list_supervisors, mock_list_admins, client
    ):
        """Test error handling when service fails."""
        # Arrange
        mock_list_residents.side_effect = Exception("Database error")

        # Act
        response = client.get("/v1/users/")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Error al obtener usuarios"


class TestUpdateUserEndpoint:
    """Tests for PATCH /v1/users/{user_id} endpoint."""

    @patch("app.services.user_service.update_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_update_user_success_all_fields(
        self, mock_supabase_admin, mock_update_user, client
    ):
        """Test successful user update with all fields."""
        # Arrange
        user_id = "user-123"
        update_payload = {
            "email": "newemail@hospital.cl",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "supervisor",
            "password": "NewPass123!",
        }

        # Mock supabase admin
        mock_supabase_admin.auth.admin.update_user_by_id.return_value = None

        # Mock service response
        mock_updated_user = {
            "id": user_id,
            "email": "newemail@hospital.cl",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "Supervisor",
        }
        mock_update_user.return_value = mock_updated_user

        # Act
        response = client.patch(f"/v1/users/{user_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["email"] == "newemail@hospital.cl"

        # Verify auth update was called
        mock_supabase_admin.auth.admin.update_user_by_id.assert_called_once()
        call_args = mock_supabase_admin.auth.admin.update_user_by_id.call_args
        assert call_args[0][0] == user_id
        assert "email" in call_args[0][1]
        assert "password" in call_args[0][1]
        assert "data" in call_args[0][1]

    @patch("app.services.user_service.update_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_update_user_email_only(
        self, mock_supabase_admin, mock_update_user, client
    ):
        """Test updating only email."""
        # Arrange
        user_id = "user-123"
        update_payload = {"email": "newemail@hospital.cl"}

        mock_supabase_admin.auth.admin.update_user_by_id.return_value = None

        mock_updated_user = {
            "id": user_id,
            "email": "newemail@hospital.cl",
            "first_name": "Juan",
            "last_name": "Pérez",
        }
        mock_update_user.return_value = mock_updated_user

        # Act
        response = client.patch(f"/v1/users/{user_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("app.services.user_service.update_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_update_user_password_only(
        self, mock_supabase_admin, mock_update_user, client
    ):
        """Test updating only password."""
        # Arrange
        user_id = "user-123"
        update_payload = {"password": "NewPass123!"}

        mock_supabase_admin.auth.admin.update_user_by_id.return_value = None
        mock_update_user.return_value = {"id": user_id}

        # Act
        response = client.patch(f"/v1/users/{user_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("app.services.user_service.update_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_update_user_metadata_only(
        self, mock_supabase_admin, mock_update_user, client
    ):
        """Test updating only metadata fields (first_name, last_name, role)."""
        # Arrange
        user_id = "user-123"
        update_payload = {
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "supervisor",
        }

        mock_supabase_admin.auth.admin.update_user_by_id.return_value = None
        mock_update_user.return_value = {
            "id": user_id,
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "Supervisor",
        }

        # Act
        response = client.patch(f"/v1/users/{user_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("app.services.user_service.update_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_update_user_error(self, mock_supabase_admin, mock_update_user, client):
        """Test error handling when update fails."""
        # Arrange
        user_id = "user-123"
        update_payload = {"email": "newemail@hospital.cl"}

        mock_supabase_admin.auth.admin.update_user_by_id.side_effect = Exception(
            "Auth update failed"
        )

        # Act
        response = client.patch(f"/v1/users/{user_id}", json=update_payload)

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestDeleteUserEndpoint:
    """Tests for DELETE /v1/users/{user_id} endpoint."""

    @patch("app.services.user_service.delete_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_delete_user_success(self, mock_supabase_admin, mock_delete_user, client):
        """Test successful user deactivation."""
        # Arrange
        user_id = "user-123"

        mock_supabase_admin.auth.admin.update_user_by_id.return_value = None
        mock_delete_user.return_value = True

        # Act
        response = client.delete(f"/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User deactivated successfully"

        # Verify both auth ban and DB delete were called
        mock_supabase_admin.auth.admin.update_user_by_id.assert_called_once_with(
            user_id, {"ban_duration": "876600h"}
        )
        mock_delete_user.assert_called_once_with(user_id)

    @patch("app.services.user_service.delete_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_delete_user_not_found_in_auth(
        self, mock_supabase_admin, mock_delete_user, client
    ):
        """Test user deletion when user not found in Auth."""
        # Arrange
        user_id = "user-123"

        mock_supabase_admin.auth.admin.update_user_by_id.side_effect = Exception(
            "User not found"
        )
        mock_delete_user.return_value = True

        # Act
        response = client.delete(f"/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User deactivated (DB only)"

        # Verify DB delete was called at least once in fallback path
        assert mock_delete_user.call_count >= 1

    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_delete_user_no_admin_client(self, mock_supabase_admin, client):
        """Test error when admin client is not configured."""
        # Arrange
        user_id = "user-123"
        mock_supabase_admin.__bool__.return_value = False

        # Act
        response = client.delete(f"/v1/users/{user_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "No Admin Key" in data["detail"]

    @patch("app.services.user_service.delete_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_delete_user_generic_error(
        self, mock_supabase_admin, mock_delete_user, client
    ):
        """Test generic error handling."""
        # Arrange
        user_id = "user-123"

        mock_supabase_admin.auth.admin.update_user_by_id.side_effect = Exception(
            "Database error"
        )

        # Act
        response = client.delete(f"/v1/users/{user_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestReactivateUserEndpoint:
    """Tests for POST /v1/users/{user_id}/reactivate endpoint."""

    @patch("app.services.user_service.reactivate_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_reactivate_user_success(
        self, mock_supabase_admin, mock_reactivate_user, client
    ):
        """Test successful user reactivation."""
        # Arrange
        user_id = "user-123"

        mock_supabase_admin.auth.admin.update_user_by_id.return_value = None
        mock_reactivate_user.return_value = True

        # Act
        response = client.post(f"/v1/users/{user_id}/reactivate")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User reactivated successfully"

        # Verify both auth unban and DB reactivate were called
        mock_supabase_admin.auth.admin.update_user_by_id.assert_called_once_with(
            user_id, {"ban_duration": "0"}
        )
        mock_reactivate_user.assert_called_once_with(user_id)

    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_reactivate_user_no_admin_client(self, mock_supabase_admin, client):
        """Test error when admin client is not configured."""
        # Arrange
        user_id = "user-123"
        mock_supabase_admin.__bool__.return_value = False

        # Act
        response = client.post(f"/v1/users/{user_id}/reactivate")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "No Admin Key" in data["detail"]

    @patch("app.services.user_service.reactivate_user")
    @patch("app.api.v1.endpoints.users.supabase_admin")
    def test_reactivate_user_error(
        self, mock_supabase_admin, mock_reactivate_user, client
    ):
        """Test error handling when reactivation fails."""
        # Arrange
        user_id = "user-123"

        mock_supabase_admin.auth.admin.update_user_by_id.side_effect = Exception(
            "Auth error"
        )

        # Act
        response = client.post(f"/v1/users/{user_id}/reactivate")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
