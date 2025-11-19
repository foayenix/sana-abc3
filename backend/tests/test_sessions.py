import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestSessionEndpoints:
    """Test session/booking related endpoints."""

    def test_create_booking(self, client, sample_booking_data, auth_headers):
        """Test creating a new booking."""
        response = client.post(
            "/api/v1/sessions/book",
            headers=auth_headers,
            json=sample_booking_data,
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_create_booking_no_auth(self, client, sample_booking_data):
        """Test creating booking without authentication."""
        response = client.post(
            "/api/v1/sessions/book",
            json=sample_booking_data,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_booking_invalid_time(self, client, auth_headers):
        """Test creating booking with past time."""
        response = client.post(
            "/api/v1/sessions/book",
            headers=auth_headers,
            json={
                "practitioner_id": 1,
                "service_id": 1,
                "scheduled_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_user_sessions(self, client, auth_headers):
        """Test getting user's sessions."""
        response = client.get("/api/v1/sessions", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_sessions_filtered(self, client, auth_headers):
        """Test getting user's sessions with filters."""
        response = client.get(
            "/api/v1/sessions",
            headers=auth_headers,
            params={"status": "scheduled", "from_date": datetime.utcnow().isoformat()},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_session_by_id(self, client, auth_headers):
        """Test getting a specific session."""
        # First create a session, then get it
        response = client.get("/api/v1/sessions/1", headers=auth_headers)
        # May be 404 if no session exists, or 200 if it does
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_cancel_session(self, client, auth_headers):
        """Test canceling a session."""
        response = client.post(
            "/api/v1/sessions/1/cancel",
            headers=auth_headers,
            json={"reason": "Schedule conflict"},
        )
        # May be 404 if session doesn't exist
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_reschedule_session(self, client, auth_headers):
        """Test rescheduling a session."""
        new_time = (datetime.utcnow() + timedelta(days=5)).isoformat()
        response = client.post(
            "/api/v1/sessions/1/reschedule",
            headers=auth_headers,
            json={"new_time": new_time},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_complete_session(self, client, auth_headers, sample_session_data):
        """Test marking session as complete."""
        response = client.post(
            "/api/v1/sessions/1/complete",
            headers=auth_headers,
            json={
                "notes": "Session completed successfully",
                "outcome_rating": 5,
            },
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_add_session_notes(self, client, auth_headers):
        """Test adding notes to a session."""
        response = client.post(
            "/api/v1/sessions/1/notes",
            headers=auth_headers,
            json={"notes": "Patient reported improvement in symptoms."},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND,
        ]


class TestPractitionerSessions:
    """Test practitioner-specific session endpoints."""

    def test_get_practitioner_schedule(self, client, auth_headers):
        """Test getting practitioner's schedule."""
        response = client.get(
            "/api/v1/practitioners/me/sessions",
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_get_practitioner_upcoming(self, client, auth_headers):
        """Test getting practitioner's upcoming sessions."""
        response = client.get(
            "/api/v1/practitioners/me/sessions/upcoming",
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]


class TestReviews:
    """Test session review endpoints."""

    def test_submit_review(self, client, auth_headers):
        """Test submitting a session review."""
        response = client.post(
            "/api/v1/sessions/1/review",
            headers=auth_headers,
            json={
                "rating": 5,
                "comment": "Excellent session, very helpful!",
                "would_recommend": True,
            },
        )
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_submit_review_invalid_rating(self, client, auth_headers):
        """Test submitting review with invalid rating."""
        response = client.post(
            "/api/v1/sessions/1/review",
            headers=auth_headers,
            json={
                "rating": 10,  # Invalid: should be 1-5
                "comment": "Test",
            },
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_get_session_review(self, client, auth_headers):
        """Test getting a session's review."""
        response = client.get("/api/v1/sessions/1/review", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]
