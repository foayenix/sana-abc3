import pytest
from fastapi import status


class TestPractitionerEndpoints:
    """Test practitioner-related endpoints."""

    def test_list_practitioners(self, client):
        """Test listing all practitioners."""
        response = client.get("/api/v1/practitioners")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_practitioners_with_filters(self, client, test_practitioner):
        """Test listing practitioners with filters."""
        response = client.get(
            "/api/v1/practitioners",
            params={
                "specialty": "Acupuncture",
                "min_rating": 4.0,
                "verified_only": True,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_practitioner_by_id(self, client, test_practitioner):
        """Test getting a specific practitioner."""
        response = client.get(f"/api/v1/practitioners/{test_practitioner.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_practitioner.id

    def test_get_practitioner_not_found(self, client):
        """Test getting nonexistent practitioner."""
        response = client.get("/api/v1/practitioners/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_practitioner_services(self, client, test_practitioner, test_service):
        """Test getting practitioner's services."""
        response = client.get(f"/api/v1/practitioners/{test_practitioner.id}/services")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_practitioner_availability(self, client, test_practitioner):
        """Test getting practitioner's availability."""
        response = client.get(
            f"/api/v1/practitioners/{test_practitioner.id}/availability",
            params={"date": "2024-03-15"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_practitioner_reviews(self, client, test_practitioner):
        """Test getting practitioner's reviews."""
        response = client.get(f"/api/v1/practitioners/{test_practitioner.id}/reviews")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_practitioner_profile(
        self, client, test_practitioner, practitioner_headers
    ):
        """Test updating practitioner profile."""
        response = client.patch(
            f"/api/v1/practitioners/{test_practitioner.id}",
            headers=practitioner_headers,
            json={
                "bio": "Updated bio with more experience.",
                "hourly_rate": 120.00,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bio"] == "Updated bio with more experience."
        assert data["hourly_rate"] == 120.00

    def test_update_practitioner_unauthorized(self, client, test_practitioner, auth_headers):
        """Test updating practitioner profile without authorization."""
        response = client.patch(
            f"/api/v1/practitioners/{test_practitioner.id}",
            headers=auth_headers,
            json={"bio": "Unauthorized update"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_service(self, client, test_practitioner, practitioner_headers):
        """Test creating a new service."""
        response = client.post(
            f"/api/v1/practitioners/{test_practitioner.id}/services",
            headers=practitioner_headers,
            json={
                "name": "Follow-up Session",
                "description": "Regular treatment session.",
                "duration_minutes": 60,
                "price": 100.00,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Follow-up Session"

    def test_update_service(
        self, client, test_practitioner, test_service, practitioner_headers
    ):
        """Test updating a service."""
        response = client.patch(
            f"/api/v1/practitioners/{test_practitioner.id}/services/{test_service.id}",
            headers=practitioner_headers,
            json={"price": 175.00},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["price"] == 175.00

    def test_delete_service(
        self, client, test_practitioner, test_service, practitioner_headers
    ):
        """Test deleting a service."""
        response = client.delete(
            f"/api/v1/practitioners/{test_practitioner.id}/services/{test_service.id}",
            headers=practitioner_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_set_availability(self, client, test_practitioner, practitioner_headers):
        """Test setting practitioner availability."""
        response = client.post(
            f"/api/v1/practitioners/{test_practitioner.id}/availability",
            headers=practitioner_headers,
            json={
                "day_of_week": 1,  # Monday
                "start_time": "09:00",
                "end_time": "17:00",
            },
        )
        assert response.status_code == status.HTTP_200_OK


class TestPractitionerVerification:
    """Test practitioner verification endpoints."""

    def test_submit_verification(self, client, practitioner_headers):
        """Test submitting verification documents."""
        response = client.post(
            "/api/v1/practitioners/verification/submit",
            headers=practitioner_headers,
            json={
                "license_number": "LIC-12345",
                "license_state": "CA",
                "documents": ["doc1.pdf", "doc2.pdf"],
            },
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_admin_approve_verification(
        self, client, test_practitioner, admin_headers
    ):
        """Test admin approving verification."""
        response = client.post(
            f"/api/v1/admin/practitioners/{test_practitioner.id}/verify",
            headers=admin_headers,
            json={"status": "approved"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_admin_reject_verification(
        self, client, test_practitioner, admin_headers
    ):
        """Test admin rejecting verification."""
        response = client.post(
            f"/api/v1/admin/practitioners/{test_practitioner.id}/verify",
            headers=admin_headers,
            json={
                "status": "rejected",
                "reason": "Invalid license number",
            },
        )
        assert response.status_code == status.HTTP_200_OK
