"""
Questionnaire models for the SANA Algorithms Suite.

Contains Pydantic models for health assessment questionnaires.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID, uuid4


class QuestionnaireResponse(BaseModel):
    """Model for user questionnaire responses."""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    domain: str  # physical, emotional, social, cognitive, spiritual
    responses: Dict[str, int]  # question_id: score (0-100)
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class DomainQuestionnaire(BaseModel):
    """Model for a domain-specific questionnaire."""
    domain: str
    questions: List[dict]  # list of {id, text, scale}


class Question(BaseModel):
    """Model for an individual question."""
    id: str
    text: str
    domain: str
    scale_min: int = 0
    scale_max: int = 100
    scale_labels: Optional[Dict[str, str]] = None  # e.g., {"0": "Never", "100": "Always"}


class QuestionnaireSubmission(BaseModel):
    """Model for submitting questionnaire responses."""
    user_id: UUID
    domain: str
    responses: Dict[str, int]


class QuestionnaireResult(BaseModel):
    """Model for questionnaire analysis results."""
    domain: str
    raw_score: float
    normalized_score: float
    percentile: Optional[float] = None
    interpretation: str
    recommendations: List[str] = []
