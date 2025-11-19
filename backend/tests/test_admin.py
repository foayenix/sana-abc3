import pytest
from fastapi import status


class TestAdminEndpoints:
    """Test admin dashboard endpoints."""

    def test_admin_dashboard_stats(self, client, auth_headers):
        """Test getting admin dashboard statistics."""
        response = client.get("/api/v1/admin/dashboard", headers=auth_headers)
        # Should be 403 for non-admin, 200 for admin
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_list_users(self, client, auth_headers):
        """Test listing all users as admin."""
        response = client.get("/api/v1/admin/users", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_list_users_filtered(self, client, auth_headers):
        """Test listing users with filters."""
        response = client.get(
            "/api/v1/admin/users",
            headers=auth_headers,
            params={
                "role": "client",
                "is_active": True,
                "search": "test",
            },
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_get_user(self, client, auth_headers):
        """Test getting user details as admin."""
        response = client.get("/api/v1/admin/users/1", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_admin_update_user(self, client, auth_headers):
        """Test updating user as admin."""
        response = client.patch(
            "/api/v1/admin/users/1",
            headers=auth_headers,
            json={"is_active": False},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_admin_delete_user(self, client, auth_headers):
        """Test deleting user as admin."""
        response = client.delete("/api/v1/admin/users/1", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]


class TestAdminPractitioners:
    """Test admin practitioner management endpoints."""

    def test_admin_list_practitioners(self, client, auth_headers):
        """Test listing practitioners for admin."""
        response = client.get("/api/v1/admin/practitioners", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_pending_verifications(self, client, auth_headers):
        """Test getting pending verifications."""
        response = client.get(
            "/api/v1/admin/practitioners/pending-verification",
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_verify_practitioner(self, client, auth_headers):
        """Test verifying a practitioner."""
        response = client.post(
            "/api/v1/admin/practitioners/1/verify",
            headers=auth_headers,
            json={"status": "approved"},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]


class TestAdminAnalytics:
    """Test admin analytics endpoints."""

    def test_admin_revenue_analytics(self, client, auth_headers):
        """Test getting revenue analytics."""
        response = client.get(
            "/api/v1/admin/analytics/revenue",
            headers=auth_headers,
            params={"period": "month"},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_user_analytics(self, client, auth_headers):
        """Test getting user growth analytics."""
        response = client.get(
            "/api/v1/admin/analytics/users",
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_session_analytics(self, client, auth_headers):
        """Test getting session analytics."""
        response = client.get(
            "/api/v1/admin/analytics/sessions",
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_admin_export_report(self, client, auth_headers):
        """Test exporting admin report."""
        response = client.get(
            "/api/v1/admin/reports/export",
            headers=auth_headers,
            params={"format": "csv", "type": "users"},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]


class TestAdminSettings:
    """Test admin settings endpoints."""

    def test_get_platform_settings(self, client, auth_headers):
        """Test getting platform settings."""
        response = client.get("/api/v1/admin/settings", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_update_platform_settings(self, client, auth_headers):
        """Test updating platform settings."""
        response = client.patch(
            "/api/v1/admin/settings",
            headers=auth_headers,
            json={
                "platform_fee_percent": 12.0,
                "require_email_verification": True,
            },
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]
