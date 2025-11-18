"""
Data models for SST (Safety & Triage Model)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class SafetyStatus(str, Enum):
    """Safety status levels"""
    SAFE = "safe"              # No concerns
    MONITOR = "monitor"        # Watch closely, provide resources
    ESCALATE = "escalate"      # Needs human review within 24h
    URGENT = "urgent"          # Immediate intervention required


class RiskCategory(str, Enum):
    """Categories of risk"""
    SELF_HARM = "self_harm"
    SEVERE_DEPRESSION = "severe_depression"
    ANXIETY_CRISIS = "anxiety_crisis"
    CHRONIC_PAIN = "chronic_pain"
    EATING_DISORDER = "eating_disorder"
    SUBSTANCE_ABUSE = "substance_abuse"
    RAPID_DETERIORATION = "rapid_deterioration"
    EXTREME_ISOLATION = "extreme_isolation"
    SUICIDAL_IDEATION = "suicidal_ideation"


class EscalationPathway(str, Enum):
    """Where to escalate"""
    NHS_111 = "nhs_111"                    # NHS urgent advice
    NHS_999 = "nhs_999"                    # Emergency services
    SAMARITANS = "samaritans"              # 116 123
    CRISIS_TEXT = "crisis_text"            # Text SHOUT to 85258
    SANA_REVIEWER = "sana_reviewer"        # Internal human review
    USER_GP = "user_gp"                    # User's GP
    MENTAL_HEALTH_CRISIS = "mental_health_crisis"  # Local crisis team
    NO_ESCALATION = "no_escalation"


class RiskIndicator(BaseModel):
    """Individual risk indicator detected"""
    indicator_id: UUID = Field(default_factory=uuid4)
    indicator_type: str  # "low_score", "keyword_detected", "score_drop", "pattern_change"
    risk_category: RiskCategory
    severity: int = Field(..., ge=1, le=10)  # 1=low, 10=critical
    description: str
    evidence: Dict[str, Any] = {}
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class CrisisKeyword(BaseModel):
    """Crisis keyword configuration"""
    keyword: str
    category: RiskCategory
    severity: int = Field(..., ge=1, le=10)
    context_required: bool = False


class HistoricalScore(BaseModel):
    """Historical SISM score for trend analysis"""
    score_id: UUID
    user_id: UUID
    overall_score: float
    domain_scores: Dict[str, float]
    recorded_at: datetime


class SSTInput(BaseModel):
    """Input for safety & triage analysis"""
    user_id: UUID

    # Current state
    current_sism_score: float
    current_domain_scores: Dict[str, float]
    current_sism_id: UUID

    # Historical data
    historical_scores: List[HistoricalScore] = []

    # Optional text analysis
    recent_journal_entries: List[str] = []
    questionnaire_free_text: List[str] = []

    # Activity patterns
    days_since_last_activity: Optional[int] = None
    missed_practitioner_appointments: int = 0
    declined_interventions: int = 0

    # Context
    user_age: Optional[int] = None
    has_existing_mental_health_diagnosis: bool = False
    currently_in_therapy: bool = False
    on_medication: bool = False


class SafetyResource(BaseModel):
    """Resource to provide to user"""
    resource_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    contact_method: str  # "phone", "text", "online", "in_person"
    contact_details: str
    availability: str  # "24/7", "weekdays 9-5", etc.
    appropriate_for: List[RiskCategory]


class ImmediateAction(BaseModel):
    """Immediate action to take"""
    action_id: UUID = Field(default_factory=uuid4)
    action_type: str  # "display_message", "send_notification", "block_content", "escalate"
    message: str
    urgency: str  # "low", "medium", "high", "critical"
    requires_acknowledgment: bool = False


class HumanReviewCase(BaseModel):
    """Case for human review"""
    case_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    risk_score: float
    safety_status: SafetyStatus
    risk_indicators: List[RiskIndicator]
    recommended_action: str
    escalation_pathway: EscalationPathway
    priority: str  # "routine", "high", "urgent", "critical"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    outcome: Optional[str] = None


class SSTOutput(BaseModel):
    """Complete output from SST analysis"""
    analysis_id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    # Risk assessment
    safety_status: SafetyStatus
    risk_score: float = Field(..., ge=0, le=100)
    risk_category: Optional[RiskCategory] = None

    # Risk factors
    risk_indicators: List[RiskIndicator]
    primary_concerns: List[str]  # Human-readable summary

    # Trend analysis
    score_trend: str  # "improving", "stable", "declining", "rapidly_declining"
    trend_percentage: Optional[float] = None  # % change over time period

    # Recommendations
    recommended_action: str
    immediate_actions: List[ImmediateAction]
    escalation_pathway: EscalationPathway
    resources_to_provide: List[SafetyResource]

    # Review requirements
    requires_human_review: bool
    human_review_case: Optional[HumanReviewCase] = None
    review_deadline: Optional[datetime] = None

    # User-facing messages
    user_message: Optional[str] = None  # What to show the user
    show_emergency_banner: bool = False

    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    algorithm_version: str = "1.0"
    confidence: float = Field(..., ge=0, le=100)  # Confidence in assessment


class SafetyAuditLog(BaseModel):
    """Audit log for safety decisions"""
    log_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    analysis_id: UUID
    event_type: str  # "risk_detected", "escalation_triggered", "human_review_requested"
    risk_score: float
    safety_status: SafetyStatus
    action_taken: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None


# Legacy models for backwards compatibility
class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyInput(BaseModel):
    """Input model for safety assessment."""
    user_id: UUID
    health_data: Dict
    recent_responses: List[Dict] = []


class SafetyOutput(BaseModel):
    """Output model for safety assessment."""
    user_id: UUID
    risk_level: RiskLevel
    risk_score: float
    flags: List[str]
    recommendations: List[str]
    requires_immediate_action: bool
    escalation_contact: Optional[str] = None
