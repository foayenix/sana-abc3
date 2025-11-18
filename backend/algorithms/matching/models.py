"""
Pydantic models for matching algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID


class PractitionerMatchInput(BaseModel):
    """Input model for practitioner recommendation."""
    user_id: UUID
    health_goals: List[str]
    preferences: Dict


class PractitionerMatchOutput(BaseModel):
    """Output model for practitioner recommendation."""
    practitioner_id: UUID
    match_score: float
    match_reasons: List[str]
    specialties_matched: List[str]


class MatchingInput(BaseModel):
    """Input model for detailed matching."""
    user_id: UUID
    practitioner_id: UUID
    user_profile: Dict
    practitioner_profile: Dict


class MatchingOutput(BaseModel):
    """Output model for detailed matching."""
    user_id: UUID
    practitioner_id: UUID
    match_score: float
    compatibility_breakdown: Dict[str, float]
    recommendations: List[str]
