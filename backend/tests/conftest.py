"""
Pytest configuration and fixtures for SANA Platform tests.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "age": 35
    }


@pytest.fixture
def sample_questionnaire_responses():
    """Sample questionnaire responses for testing scoring algorithms."""
    return {
        "physical": {"q1": 70, "q2": 65, "q3": 80},
        "emotional": {"q1": 60, "q2": 55, "q3": 70},
        "social": {"q1": 75, "q2": 80, "q3": 65},
        "cognitive": {"q1": 85, "q2": 90, "q3": 75},
        "spiritual": {"q1": 50, "q2": 55, "q3": 60}
    }


# Authentication fixtures
@pytest.fixture
def sample_login_data():
    """Sample login credentials."""
    return {
        "username": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_register_data():
    """Sample registration data."""
    return {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User"
    }


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock_token"


@pytest.fixture
def auth_headers(mock_auth_token):
    """Authorization headers with mock token."""
    return {"Authorization": f"Bearer {mock_auth_token}"}


# Practitioner fixtures
@pytest.fixture
def sample_practitioner_data():
    """Sample practitioner profile data."""
    return {
        "specialties": ["Acupuncture", "Herbal Medicine"],
        "bio": "Experienced practitioner with 10+ years of experience.",
        "hourly_rate": 100.00,
        "location": {"city": "San Francisco", "state": "CA", "zip": "94102"}
    }


@pytest.fixture
def sample_service_data():
    """Sample service data."""
    return {
        "name": "Initial Consultation",
        "description": "Comprehensive health assessment and treatment plan.",
        "duration_minutes": 90,
        "price": 150.00
    }


# Session/Booking fixtures
@pytest.fixture
def sample_booking_data():
    """Sample booking request data."""
    return {
        "practitioner_id": 1,
        "service_id": 1,
        "scheduled_at": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        "notes": "First visit, chronic back pain"
    }


@pytest.fixture
def sample_session_data():
    """Sample completed session data."""
    return {
        "session_id": 1,
        "status": "completed",
        "notes": "Patient showed improvement",
        "outcome_rating": 4
    }


# Health tracking fixtures
@pytest.fixture
def sample_health_entry():
    """Sample health journal entry."""
    return {
        "entry_type": "symptom",
        "title": "Morning headache",
        "description": "Mild headache upon waking",
        "severity": 3,
        "tags": ["headache", "morning"]
    }


@pytest.fixture
def sample_mood_entry():
    """Sample mood tracking entry."""
    return {
        "mood_score": 7,
        "energy_level": 6,
        "stress_level": 4,
        "notes": "Good day overall"
    }


# Mock services
@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    mock = MagicMock()
    mock.send_email.return_value = True
    mock.send_verification_email.return_value = True
    return mock


@pytest.fixture
def mock_payment_service():
    """Mock payment service for testing."""
    mock = MagicMock()
    mock.create_payment_intent.return_value = {
        "id": "pi_test123",
        "client_secret": "pi_test123_secret",
        "status": "requires_payment_method"
    }
    mock.confirm_payment.return_value = {
        "id": "pi_test123",
        "status": "succeeded"
    }
    mock.create_refund.return_value = {
        "id": "re_test123",
        "status": "succeeded"
    }
    return mock


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing."""
    mock = MagicMock()
    mock.send_push.return_value = True
    mock.send_sms.return_value = True
    return mock
