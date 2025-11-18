"""
Data models for SOU (Outcome Uplift Model)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class OutcomeTimeframe(str, Enum):
    """Timeframes for measuring outcomes"""
    FOUR_WEEKS = "4_weeks"
    EIGHT_WEEKS = "8_weeks"
    TWELVE_WEEKS = "12_weeks"
    SIX_MONTHS = "6_months"


class AdherenceLevel(str, Enum):
    """User adherence to recommendations"""
    HIGH = "high"          # >80% completion
    MEDIUM = "medium"      # 50-80% completion
    LOW = "low"            # <50% completion
    NONE = "none"          # Never started


class OutcomeRecord(BaseModel):
    """Complete outcome record for a user's treatment journey"""
    record_id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    # Initial state (baseline)
    baseline_sism_score: float
    baseline_domain_scores: Dict[str, float]
    baseline_weak_domains: List[str]
    baseline_recorded_at: datetime

    # User profile
    user_age: Optional[int] = None
    user_gender: Optional[str] = None
    primary_conditions: List[str] = []
    primary_goals: List[str] = []

    # Interventions received
    recommended_interventions: List[UUID]  # Intervention IDs
    interventions_actually_used: List[UUID]  # What user actually did
    adherence_level: AdherenceLevel
    adherence_percentage: float = Field(..., ge=0, le=100)

    # Practitioner (if applicable)
    practitioner_id: Optional[UUID] = None
    practitioner_specialty: Optional[str] = None
    sessions_completed: int = 0

    # Outcome state
    outcome_sism_score: float
    outcome_domain_scores: Dict[str, float]
    outcome_recorded_at: datetime
    timeframe: OutcomeTimeframe

    # Calculated improvements
    overall_improvement: float  # Percentage change in SISM
    domain_improvements: Dict[str, float]  # Per-domain % changes

    # User feedback
    user_satisfaction: int = Field(..., ge=1, le=5)  # 1-5 stars
    would_recommend: bool
    reported_side_effects: List[str] = []
    free_text_feedback: Optional[str] = None

    # Dropout tracking
    completed_full_program: bool
    dropout_reason: Optional[str] = None

    # Context
    season: str  # "spring", "summer", "fall", "winter"
    cost_per_week: float
    time_per_week_minutes: int

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InterventionPerformance(BaseModel):
    """Performance metrics for a specific intervention"""
    intervention_id: UUID
    intervention_name: str

    # Usage stats
    times_recommended: int = 0
    times_actually_used: int = 0
    acceptance_rate: float = 0.0  # % of recommendations that were followed

    # Outcome stats (for users who completed)
    completions: int = 0
    average_improvement: float = 0.0
    median_improvement: float = 0.0
    improvement_std: float = 0.0

    # By domain
    domain_performance: Dict[str, float] = {}  # domain -> avg improvement

    # By user segment
    performance_by_age: Dict[str, float] = {}  # age_range -> avg improvement
    performance_by_initial_score: Dict[str, float] = {}  # score_range -> avg improvement

    # Confidence
    sample_size: int = 0
    confidence_interval_95: Tuple[float, float] = (0.0, 0.0)

    # Rankings
    overall_rank: Optional[int] = None  # Rank among all interventions
    rank_in_category: Optional[int] = None  # Rank within category

    # Last updated
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PractitionerPerformance(BaseModel):
    """Performance metrics for a practitioner"""
    practitioner_id: UUID
    practitioner_name: str

    # Usage stats
    total_clients: int = 0
    active_clients: int = 0
    completed_treatments: int = 0

    # Outcome stats
    average_improvement: float = 0.0
    median_improvement: float = 0.0
    top_quartile_rate: float = 0.0  # % achieving >25% improvement

    # By condition
    performance_by_condition: Dict[str, float] = {}  # condition -> avg improvement

    # Client feedback
    average_satisfaction: float = 0.0
    would_recommend_rate: float = 0.0

    # Retention
    retention_rate: float = 0.0  # % completing full program
    average_sessions_per_client: float = 0.0

    # Rankings
    overall_rank: Optional[int] = None
    rank_in_specialty: Optional[int] = None

    # Confidence
    sample_size: int = 0

    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PredictedOutcome(BaseModel):
    """Predicted outcome for a user + intervention combo"""
    prediction_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    intervention_id: UUID

    # Prediction
    predicted_improvement: float  # Expected % improvement in SISM
    confidence: float = Field(..., ge=0, le=100)
    confidence_interval_95: Tuple[float, float]

    # Feature importance
    key_factors: List[str]  # Top features driving prediction

    # Comparison
    percentile_among_users: Optional[float] = None  # How good is this prediction?
    better_than_average: bool

    # Metadata
    model_version: str = "1.0"
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


class SOURecommendation(BaseModel):
    """Outcome-optimized recommendation"""
    recommendation_id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    intervention_id: UUID
    intervention_name: str

    # Prediction
    predicted_outcome: PredictedOutcome

    # Ranking factors
    outcome_score: float  # Expected improvement
    evidence_score: float  # Clinical evidence
    cost_efficiency: float  # Improvement per pound
    time_efficiency: float  # Improvement per hour

    # Combined score (outcome-weighted)
    total_score: float

    # Explanation
    why_recommended: str
    expected_timeline: str
    success_rate: float  # % of similar users who improved

    # Exploration flag
    is_exploration: bool = False  # True if trying something new
    exploration_reason: Optional[str] = None


class SOUOutput(BaseModel):
    """Complete output from SOU learning system"""
    analysis_id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    # Outcome-optimized recommendations
    recommendations: List[SOURecommendation]

    # Performance insights
    best_performing_interventions: List[str]  # Top 5 overall
    best_for_your_profile: List[str]  # Top 5 for this user

    # Learning stats
    total_outcomes_analyzed: int
    user_profile_matches: int  # Similar users in dataset
    prediction_confidence: str  # "high", "medium", "low"

    # Comparison to baseline
    expected_improvement_with_sou: float
    expected_improvement_baseline: float
    uplift: float  # Difference (SOU advantage)

    # Metadata
    model_version: str = "1.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningMetrics(BaseModel):
    """Overall learning system metrics"""
    metrics_id: UUID = Field(default_factory=uuid4)

    # Data stats
    total_outcome_records: int
    outcome_records_last_30_days: int
    users_with_outcomes: int

    # Model performance
    model_mae: float  # Mean Absolute Error (how far off predictions are)
    model_r2: float  # R-squared (how much variance explained)
    prediction_accuracy_within_10pct: float  # % predictions within 10% of actual

    # Business impact
    average_improvement_with_sou: float
    average_improvement_baseline: float
    uplift_percentage: float

    # Top performers
    top_interventions: List[str]
    top_practitioners: List[str]

    # Learning status
    learning_phase: str  # "cold_start", "early_learning", "mature"
    exploration_rate: float  # Current exploration %

    last_updated: datetime = Field(default_factory=datetime.utcnow)
