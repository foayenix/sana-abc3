"""
Pydantic models for index algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID


class IndexComponent(BaseModel):
    """Component of the SANA Index score."""
    name: str
    score: float
    weight: float
    details: Dict = {}


class IndexInput(BaseModel):
    """Input model for SANA Index calculation."""
    practitioner_id: UUID
    credentials: List[str]
    outcome_data: Dict
    reviews: List[Dict]
    verification_status: bool


class IndexOutput(BaseModel):
    """Output model for SANA Index calculation."""
    practitioner_id: UUID
    overall_score: float
    components: List[IndexComponent]
    percentile: float
    trend: str  # improving, stable, declining
