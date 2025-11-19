import pytest
from fastapi import status
from datetime import datetime


class TestHealthJournal:
    """Test health journal endpoints."""

    def test_create_journal_entry(self, client, auth_headers, sample_health_entry):
        """Test creating a health journal entry."""
        response = client.post(
            "/api/v1/health/journal",
            headers=auth_headers,
            json=sample_health_entry,
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_get_journal_entries(self, client, auth_headers):
        """Test getting journal entries."""
        response = client.get("/api/v1/health/journal", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_journal_entries_filtered(self, client, auth_headers):
        """Test getting filtered journal entries."""
        response = client.get(
            "/api/v1/health/journal",
            headers=auth_headers,
            params={
                "entry_type": "symptom",
                "from_date": "2024-01-01",
                "to_date": "2024-12-31",
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_journal_entry(self, client, auth_headers):
        """Test updating a journal entry."""
        response = client.patch(
            "/api/v1/health/journal/1",
            headers=auth_headers,
            json={"description": "Updated description", "severity": 2},
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_delete_journal_entry(self, client, auth_headers):
        """Test deleting a journal entry."""
        response = client.delete("/api/v1/health/journal/1", headers=auth_headers)
        assert response.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]


class TestMoodTracking:
    """Test mood tracking endpoints."""

    def test_log_mood(self, client, auth_headers, sample_mood_entry):
        """Test logging mood entry."""
        response = client.post(
            "/api/v1/health/mood",
            headers=auth_headers,
            json=sample_mood_entry,
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_get_mood_history(self, client, auth_headers):
        """Test getting mood history."""
        response = client.get("/api/v1/health/mood", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_mood_analytics(self, client, auth_headers):
        """Test getting mood analytics."""
        response = client.get(
            "/api/v1/health/mood/analytics",
            headers=auth_headers,
            params={"period": "week"},
        )
        assert response.status_code == status.HTTP_200_OK


class TestHealthScore:
    """Test health score endpoints."""

    def test_get_health_score(self, client, auth_headers):
        """Test getting user's health score."""
        response = client.get("/api/v1/health/score", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_health_score_history(self, client, auth_headers):
        """Test getting health score history."""
        response = client.get("/api/v1/health/score/history", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_health_dimensions(self, client, auth_headers):
        """Test getting health dimension breakdown."""
        response = client.get("/api/v1/health/dimensions", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_submit_questionnaire(self, client, auth_headers, sample_questionnaire_responses):
        """Test submitting health questionnaire."""
        response = client.post(
            "/api/v1/health/questionnaire",
            headers=auth_headers,
            json={"responses": sample_questionnaire_responses},
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]


class TestSymptomTracking:
    """Test symptom tracking endpoints."""

    def test_log_symptom(self, client, auth_headers):
        """Test logging a symptom."""
        response = client.post(
            "/api/v1/health/symptoms",
            headers=auth_headers,
            json={
                "symptom_type": "headache",
                "severity": 5,
                "location": "temple",
                "duration_minutes": 60,
            },
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_get_symptom_patterns(self, client, auth_headers):
        """Test getting symptom patterns."""
        response = client.get("/api/v1/health/symptoms/patterns", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_symptom_triggers(self, client, auth_headers):
        """Test getting potential symptom triggers."""
        response = client.get("/api/v1/health/symptoms/triggers", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
