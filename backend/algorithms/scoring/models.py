"""
Pydantic models for SISM (Intake Scoring Model)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID, uuid4


class QuestionResponse(BaseModel):
    """Individual question response"""
    question_id: str
    domain: str
    raw_score: int = Field(..., ge=0, le=10)  # 0-10 scale from questionnaire
    normalized_score: Optional[float] = None  # 0-100 scale

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        valid_domains = ['physical', 'emotional', 'social', 'cognitive', 'spiritual']
        if v.lower() not in valid_domains:
            raise ValueError(f'Domain must be one of {valid_domains}')
        return v.lower()


class QuestionnaireInput(BaseModel):
    """Complete questionnaire input for SISM"""
    user_id: UUID
    responses: List[QuestionResponse]
    questionnaire_version: str = "1.0"
    completed_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator('responses')
    @classmethod
    def validate_responses(cls, v):
        if len(v) == 0:
            raise ValueError('At least one response required')
        # Ensure all domains are represented
        domains = set(r.domain for r in v)
        required_domains = {'physical', 'emotional', 'social', 'cognitive', 'spiritual'}
        missing = required_domains - domains
        if missing:
            raise ValueError(f'Missing responses for domains: {missing}')
        return v


class DomainScore(BaseModel):
    """Score for a single domain"""
    domain: str
    raw_average: float  # Average of raw scores
    normalized_score: float  # 0-100 scale
    weight: float  # Weight used in overall calculation
    weighted_contribution: float  # Contribution to overall score
    question_count: int
    questions_scored: List[str]  # Question IDs included


class SISMOutput(BaseModel):
    """Complete output from SISM algorithm"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    overall_score: float = Field(..., ge=0, le=100)
    domain_scores: Dict[str, DomainScore]
    weak_domains: List[str]  # Domains scoring < 60
    calculation_metadata: Dict
    questionnaire_version: str
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "overall_score": 68.5,
                "domain_scores": {
                    "physical": {
                        "domain": "physical",
                        "normalized_score": 75.0,
                        "weight": 0.25,
                        "weighted_contribution": 18.75
                    }
                },
                "weak_domains": ["emotional", "social"],
                "calculation_metadata": {
                    "weights_used": {"physical": 0.25, "emotional": 0.25},
                    "total_questions": 25
                }
            }
        }


class DomainWeights(BaseModel):
    """Configurable weights for each domain"""
    physical: float = Field(default=0.25, ge=0, le=1)
    emotional: float = Field(default=0.25, ge=0, le=1)
    social: float = Field(default=0.15, ge=0, le=1)
    cognitive: float = Field(default=0.20, ge=0, le=1)
    spiritual: float = Field(default=0.15, ge=0, le=1)

    def validate_sum(self):
        """Ensure weights sum to 1.0"""
        total = self.physical + self.emotional + self.social + self.cognitive + self.spiritual
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f'Domain weights must sum to 1.0, got {total}')


# Legacy models for backwards compatibility
class DomainScoreOutput(BaseModel):
    """Output model for individual domain scores (legacy)."""
    domain: str
    score: float
    weight: float


class SISMInput(BaseModel):
    """Input model for SISM calculation (legacy)."""
    user_id: UUID
    domain_responses: Dict[str, Dict[str, int]]  # domain -> {question_id: score}


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
