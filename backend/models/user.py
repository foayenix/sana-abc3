"""
User models for the SANA Algorithms Suite.

Contains Pydantic models for user data validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class User(BaseModel):
    """Base user model."""
    id: UUID = Field(default_factory=uuid4)
    email: str
    full_name: str
    age: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(BaseModel):
    """Extended user profile with preferences and health goals."""
    user_id: UUID
    preferences: dict = {}
    health_goals: list[str] = []
    budget_weekly: Optional[float] = None
    time_available_weekly: Optional[int] = None  # minutes


class UserCreate(BaseModel):
    """Model for user creation requests."""
    email: str
    full_name: str
    age: Optional[int] = None


class UserResponse(BaseModel):
    """Model for user API responses."""
    id: UUID
    email: str
    full_name: str
    age: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
