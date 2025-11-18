"""
Practitioner models for the SANA Algorithms Suite.

Contains Pydantic models for CAM practitioner data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4


class Practitioner(BaseModel):
    """Base practitioner model."""
    id: UUID = Field(default_factory=uuid4)
    full_name: str
    specialties: List[str]
    credentials: List[str]
    verified: bool = False
    sana_index_score: Optional[float] = None
    hourly_rate: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PractitionerProfile(BaseModel):
    """Extended practitioner profile with additional details."""
    practitioner_id: UUID
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    location: Optional[str] = None
    availability: dict = {}
    modalities: List[str] = []
    languages: List[str] = ["English"]


class PractitionerCreate(BaseModel):
    """Model for practitioner creation requests."""
    full_name: str
    specialties: List[str]
    credentials: List[str]
    hourly_rate: Optional[float] = None


class PractitionerResponse(BaseModel):
    """Model for practitioner API responses."""
    id: UUID
    full_name: str
    specialties: List[str]
    credentials: List[str]
    verified: bool
    sana_index_score: Optional[float]
    hourly_rate: Optional[float]

    class Config:
        from_attributes = True


class PractitionerMatch(BaseModel):
    """Model for practitioner matching results."""
    practitioner: Practitioner
    match_score: float
    match_reasons: List[str]
