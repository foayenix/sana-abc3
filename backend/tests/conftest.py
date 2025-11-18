"""
Pytest configuration and fixtures for SANA Algorithms Suite tests.
"""

import pytest
from fastapi.testclient import TestClient
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
