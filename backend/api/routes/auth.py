"""
Authentication API routes for SANA Platform.

Handles user registration, login, token refresh, and logout.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_db
from database.models import UserRole, User
from services.auth import AuthService, get_current_user

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CLIENT
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """User profile response."""
    id: int
    email: str
    role: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_verified: bool
    subscription_tier: str
    created_at: str


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a user with the specified role (client or practitioner) and
    returns authentication tokens.
    """
    auth_service = AuthService(db)

    user, error = auth_service.register_user(
        email=request.email,
        password=request.password,
        role=request.role,
        first_name=request.first_name,
        last_name=request.last_name
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return auth_service.create_token_pair(user)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return tokens.

    Validates email and password, then returns access and refresh tokens.
    """
    auth_service = AuthService(db)

    user = auth_service.authenticate_user(request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return auth_service.create_token_pair(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Validates the refresh token and issues new access and refresh tokens.
    The old refresh token is revoked.
    """
    auth_service = AuthService(db)

    user = auth_service.verify_refresh_token(request.refresh_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Revoke old refresh token
    auth_service.revoke_refresh_token(request.refresh_token)

    return auth_service.create_token_pair(user)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: RefreshRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logout user by revoking refresh token.

    Requires valid access token in header and refresh token in body.
    """
    auth_service = AuthService(db)
    auth_service.revoke_refresh_token(request.refresh_token)

    return {"message": "Successfully logged out"}


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logout from all devices by revoking all refresh tokens.

    Requires valid access token.
    """
    auth_service = AuthService(db)
    count = auth_service.revoke_all_user_tokens(current_user.id)

    return {"message": f"Logged out from {count} sessions"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.

    Returns basic user information based on the access token.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_verified": current_user.is_verified,
        "subscription_tier": current_user.subscription_tier.value,
        "created_at": current_user.created_at.isoformat()
    }


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile.
    """
    if first_name is not None:
        current_user.first_name = first_name
    if last_name is not None:
        current_user.last_name = last_name
    if phone is not None:
        current_user.phone = phone

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_verified": current_user.is_verified,
        "subscription_tier": current_user.subscription_tier.value,
        "created_at": current_user.created_at.isoformat()
    }


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    current_password: str,
    new_password: str = Field(..., min_length=8),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change user's password.

    Requires current password for verification.
    """
    auth_service = AuthService(db)

    # Verify current password
    if not auth_service.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = auth_service.hash_password(new_password)
    db.commit()

    # Revoke all refresh tokens (force re-login)
    auth_service.revoke_all_user_tokens(current_user.id)

    return {"message": "Password changed successfully. Please login again."}


# ============================================================================
# TEST ENDPOINTS (for development)
# ============================================================================

@router.get("/test-auth")
async def test_auth():
    """Test endpoint to verify auth routes are working."""
    return {
        "status": "Auth routes operational",
        "endpoints": [
            "POST /register - Create new account",
            "POST /login - Authenticate and get tokens",
            "POST /refresh - Refresh access token",
            "POST /logout - Revoke refresh token",
            "POST /logout-all - Revoke all tokens",
            "GET /me - Get current user profile",
            "PUT /me - Update profile",
            "POST /change-password - Change password"
        ]
    }


@router.post("/test-register")
async def test_register_flow(db: Session = Depends(get_db)):
    """
    Test registration flow with dummy data.

    Creates test users for development purposes.
    """
    auth_service = AuthService(db)

    test_users = [
        {
            "email": "client@test.sana.health",
            "password": "testpass123",
            "role": UserRole.CLIENT,
            "first_name": "Test",
            "last_name": "Client"
        },
        {
            "email": "practitioner@test.sana.health",
            "password": "testpass123",
            "role": UserRole.PRACTITIONER,
            "first_name": "Test",
            "last_name": "Practitioner"
        }
    ]

    results = []
    for user_data in test_users:
        user, error = auth_service.register_user(**user_data)
        if user:
            results.append({
                "email": user.email,
                "role": user.role.value,
                "status": "created"
            })
        else:
            results.append({
                "email": user_data["email"],
                "status": "failed",
                "error": error
            })

    return {
        "message": "Test registration complete",
        "users": results,
        "note": "Use email/password to login"
    }
