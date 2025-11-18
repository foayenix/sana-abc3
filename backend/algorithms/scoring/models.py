"""
Pydantic models for scoring algorithms.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from uuid import UUID


class DomainScoreOutput(BaseModel):
    """Output model for individual domain scores."""
    domain: str
    score: float
    weight: float


class SISMInput(BaseModel):
    """Input model for SISM calculation."""
    user_id: UUID
    domain_responses: Dict[str, Dict[str, int]]  # domain -> {question_id: score}


class SISMOutput(BaseModel):
    """Output model for SISM calculation results."""
    user_id: UUID
    overall_score: float
    domain_scores: List[DomainScoreOutput]
    metadata: dict = {}


class ScoreRequest(BaseModel):
    """API request model for scoring endpoint."""
    user_id: UUID
    domain_responses: Dict[str, Dict[str, int]]
    custom_weights: Optional[Dict[str, float]] = None


class ScoreResponse(BaseModel):
    """API response model for scoring endpoint."""
    user_id: UUID
    overall_score: float
    domain_scores: Dict[str, float]
    percentile: Optional[float] = None
    interpretation: str = ""
