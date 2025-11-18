"""
Health data models for the SANA Algorithms Suite.

Contains Pydantic models for health scores and metrics.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID, uuid4


class HealthScore(BaseModel):
    """Model for overall health score."""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    overall_score: float  # 0-100
    domain_scores: Dict[str, float]  # domain: score
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}


class DomainScore(BaseModel):
    """Model for individual domain score."""
    domain: str
    score: float
    trend: Optional[str] = None  # improving, stable, declining
    components: Dict[str, float] = {}


class HealthMetric(BaseModel):
    """Model for individual health metrics."""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None  # manual, device, integration


class HealthTrend(BaseModel):
    """Model for health score trends over time."""
    user_id: UUID
    domain: str
    scores: List[Dict[str, Any]]  # list of {date, score}
    trend_direction: str  # improving, stable, declining
    change_percentage: float


class HealthScoreCreate(BaseModel):
    """Model for creating health score records."""
    user_id: UUID
    overall_score: float
    domain_scores: Dict[str, float]
    metadata: dict = {}


class HealthScoreResponse(BaseModel):
    """Model for health score API responses."""
    id: UUID
    user_id: UUID
    overall_score: float
    domain_scores: Dict[str, float]
    calculated_at: datetime

    class Config:
        from_attributes = True
