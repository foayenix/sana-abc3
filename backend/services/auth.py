"""
Authentication service for SANA Platform.

Handles user registration, login, JWT token management, and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from database.models import User, RefreshToken, ClientProfile, PractitionerProfile, UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, db: Session):
        self.db = db

    # ========================================================================
    # PASSWORD OPERATIONS
    # ========================================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    # ========================================================================
    # TOKEN OPERATIONS
    # ========================================================================

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User's database ID
            role: User's role (client, practitioner, admin)

        Returns:
            Encoded JWT token
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, user_id: int) -> str:
        """
        Create a refresh token and store in database.

        Args:
            user_id: User's database ID

        Returns:
            Encoded refresh token
        """
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        # Store in database
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expire
        )
        self.db.add(db_token)
        self.db.commit()

        return token

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    def verify_refresh_token(self, token: str) -> Optional[User]:
        """
        Verify a refresh token and return the associated user.

        Args:
            token: Refresh token string

        Returns:
            User object if valid, None otherwise
        """
        payload = self.decode_token(token)
        if not payload or payload.get("type") != "refresh":
            return None

        # Check if token exists and not revoked
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()

        if not db_token:
            return None

        return self.db.query(User).filter(User.id == db_token.user_id).first()

    def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoke a refresh token.

        Args:
            token: Refresh token to revoke

        Returns:
            True if revoked, False if not found
        """
        db_token = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if db_token:
            db_token.revoked = True
            self.db.commit()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: User's database ID

        Returns:
            Number of tokens revoked
        """
        result = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).update({"revoked": True})
        self.db.commit()
        return result

    # ========================================================================
    # USER OPERATIONS
    # ========================================================================

    def register_user(
        self,
        email: str,
        password: str,
        role: UserRole,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.

        Args:
            email: User's email address
            password: Plain text password
            role: User role (client, practitioner)
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            Tuple of (User object, error message)
        """
        # Check if email already exists
        existing = self.db.query(User).filter(User.email == email.lower()).first()
        if existing:
            return None, "Email already registered"

        # Validate password
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return None, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"

        # Create user
        user = User(
            email=email.lower(),
            hashed_password=self.hash_password(password),
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        self.db.add(user)
        self.db.flush()  # Get the user ID

        # Create profile based on role
        if role == UserRole.CLIENT:
            profile = ClientProfile(user_id=user.id)
            self.db.add(profile)
        elif role == UserRole.PRACTITIONER:
            profile = PractitionerProfile(user_id=user.id)
            self.db.add(profile)

        self.db.commit()
        self.db.refresh(user)

        return user, None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            email: User's email
            password: Plain text password

        Returns:
            User object if authenticated, None otherwise
        """
        user = self.db.query(User).filter(User.email == email.lower()).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None

        # Update last login
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email.lower()).first()

    # ========================================================================
    # TOKEN RESPONSE HELPERS
    # ========================================================================

    def create_token_pair(self, user: User) -> dict:
        """
        Create both access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            Dictionary with access_token, refresh_token, and token_type
        """
        access_token = self.create_access_token(user.id, user.role.value)
        refresh_token = self.create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }


# ============================================================================
# DEPENDENCY FOR ROUTES
# ============================================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.connection import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Usage:
        @router.get("/me")
        def get_me(user: User = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    payload = AuthService.decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


def require_role(*roles: UserRole):
    """
    Create a dependency that requires specific roles.

    Usage:
        @router.get("/admin-only")
        def admin_route(user: User = Depends(require_role(UserRole.ADMIN))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {[r.value for r in roles]}"
            )
        return user
    return role_checker


# Convenience dependencies
get_current_client = require_role(UserRole.CLIENT)
get_current_practitioner = require_role(UserRole.PRACTITIONER)
get_current_admin = require_role(UserRole.ADMIN)
