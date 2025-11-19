import pytest
from fastapi import status
from datetime import datetime, timedelta

from app.core.security import verify_password, create_access_token


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "securepassword123",
                "full_name": "Duplicate User",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "securepassword123",
                "full_name": "Invalid User",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "123",
                "full_name": "Weak Password User",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, test_user, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, client, user_token):
        """Test token refresh."""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    def test_logout(self, client, auth_headers):
        """Test user logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_password_reset_request(self, client, test_user):
        """Test password reset request."""
        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": test_user.email},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_change_password(self, client, test_user, auth_headers):
        """Test password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )
        assert response.status_code == status.HTTP_200_OK


class TestSecurityFunctions:
    """Test security utility functions."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        from app.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_create_access_token(self):
        """Test access token creation."""
        token = create_access_token(
            data={"sub": "123", "role": "client"}
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_expiration(self):
        """Test token with custom expiration."""
        token = create_access_token(
            data={"sub": "123"},
            expires_delta=timedelta(minutes=5)
        )
        assert isinstance(token, str)
