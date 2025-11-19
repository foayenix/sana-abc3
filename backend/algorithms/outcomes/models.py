"""
Data models for Outcome Measurement System.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class OutcomeMeasureType(str, Enum):
    """Types of validated outcome measures."""
    WHO5 = "who5"              # WHO-5 Wellbeing Index
    DASS21 = "dass21"          # Depression, Anxiety, Stress Scale
    VAS_PAIN = "vas_pain"      # Visual Analogue Scale for pain
    CAM_SYMPTOM = "cam_symptom"  # Custom CAM symptom scale
    CUSTOM = "custom"          # User-defined scale


class MeasureTiming(str, Enum):
    """When to deliver outcome measures."""
    PRE_SESSION = "pre_session"
    POST_SESSION = "post_session"
    ONE_WEEK = "1_week"
    ONE_MONTH = "1_month"
    THREE_MONTH = "3_month"
    SIX_MONTH = "6_month"


class DeliveryMethod(str, Enum):
    """How to deliver outcome measures."""
    EMAIL = "email"
    SMS = "sms"
    APP = "app"
    ALL = "all"


class QuestionType(str, Enum):
    """Types of questions in measures."""
    LIKERT_5 = "likert_5"     # 0-5 scale
    LIKERT_7 = "likert_7"     # 0-6 scale (DASS-21)
    SLIDER = "slider"         # 0-100 continuous
    EMOJI = "emoji"           # 5 emoji scale
    YES_NO = "yes_no"
    MULTIPLE_CHOICE = "multiple_choice"


class Question(BaseModel):
    """A single question in an outcome measure."""
    id: str
    text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    min_value: int = 0
    max_value: int = 5
    subscale: Optional[str] = None  # For DASS-21: depression, anxiety, stress
    reverse_scored: bool = False


class OutcomeMeasureRequest(BaseModel):
    """Request to complete an outcome measure."""
    measure_type: OutcomeMeasureType
    client_id: UUID
    session_id: Optional[UUID] = None
    timing: MeasureTiming
    questions: List[Question]
    instructions: str
    estimated_time: str = "2-3 minutes"


class QuestionResponse(BaseModel):
    """Response to a single question."""
    question_id: str
    value: int  # Raw response value
    response_time_ms: Optional[int] = None


class OutcomeMeasureResponse(BaseModel):
    """Completed outcome measure with scores."""
    measure_id: UUID
    measure_type: OutcomeMeasureType
    client_id: UUID
    session_id: Optional[UUID] = None
    timing: MeasureTiming

    # Responses
    responses: List[QuestionResponse]

    # Calculated scores
    total_score: float
    subscale_scores: Optional[Dict[str, float]] = None
    percentile: Optional[float] = None
    severity: Optional[str] = None  # normal, mild, moderate, severe

    # Interpretation
    interpretation: str
    clinical_flags: List[str] = []  # Any concerning responses

    # Metadata
    completed_at: datetime
    completion_time_seconds: Optional[int] = None


class ScheduledMeasure(BaseModel):
    """A scheduled outcome measure delivery."""
    id: UUID
    client_id: UUID
    session_id: Optional[UUID] = None
    practitioner_id: UUID

    measure_type: OutcomeMeasureType
    timing: MeasureTiming
    delivery_method: DeliveryMethod

    # Scheduling
    scheduled_for: datetime
    reminder_count: int = 0
    max_reminders: int = 3

    # Status
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    expired: bool = False

    # Results
    response_id: Optional[UUID] = None


class MeasureComparison(BaseModel):
    """Compare outcome measures over time."""
    measure_type: OutcomeMeasureType
    client_id: UUID

    # Timeline
    measurements: List[Dict[str, Any]]  # List of {date, score, timing}

    # Analysis
    baseline_score: Optional[float] = None
    current_score: Optional[float] = None
    change: Optional[float] = None
    percent_change: Optional[float] = None

    # Clinical significance
    reliable_change: bool = False  # Exceeds measurement error
    clinically_significant: bool = False  # Meaningful improvement
    effect_size: Optional[float] = None  # Cohen's d
