"""
Intervention models for the SANA Algorithms Suite.

Contains Pydantic models for CAM interventions and treatments.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4


class Intervention(BaseModel):
    """Base intervention model."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: str  # yoga, meditation, herbal, nutrition, etc.
    evidence_rating: str  # strong, moderate, weak, insufficient
    target_domains: List[str]
    contraindications: List[str] = []
    typical_duration_minutes: int
    cost_estimate: Optional[float] = None


class InterventionDetail(BaseModel):
    """Detailed intervention information."""
    intervention_id: UUID
    description: str
    benefits: List[str] = []
    risks: List[str] = []
    dosage_info: Optional[str] = None
    frequency_recommendation: Optional[str] = None
    research_citations: List[str] = []


class InterventionRecommendation(BaseModel):
    """Model for intervention recommendations."""
    intervention: Intervention
    relevance_score: float
    expected_impact: dict  # domain: expected_improvement
    confidence: float


class InterventionCreate(BaseModel):
    """Model for intervention creation requests."""
    name: str
    category: str
    evidence_rating: str
    target_domains: List[str]
    contraindications: List[str] = []
    typical_duration_minutes: int
    cost_estimate: Optional[float] = None


class InterventionResponse(BaseModel):
    """Model for intervention API responses."""
    id: UUID
    name: str
    category: str
    evidence_rating: str
    target_domains: List[str]
    contraindications: List[str]
    typical_duration_minutes: int
    cost_estimate: Optional[float]

    class Config:
        from_attributes = True
