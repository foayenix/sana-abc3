"""
Data models for SPRM (SANA Practitioner Recommendation Model)

Intelligent matchmaking between users and verified CAM practitioners.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, time
from uuid import UUID, uuid4
from enum import Enum


class TreatmentPhilosophy(str, Enum):
    """Treatment approach philosophy"""
    HOLISTIC = "holistic"
    INTEGRATIVE = "integrative"
    TRADITIONAL = "traditional"
    EVIDENCE_BASED = "evidence_based"
    PREVENTIVE = "preventive"


class CommunicationStyle(str, Enum):
    """Practitioner communication style"""
    WARM = "warm"
    DIRECT = "direct"
    EDUCATIONAL = "educational"
    COLLABORATIVE = "collaborative"


class AvailabilityWindow(BaseModel):
    """Time availability window"""
    day_of_week: str
    start_time: time
    end_time: time


class PractitionerProfile(BaseModel):
    """Complete practitioner profile for matching"""
    practitioner_id: UUID
    full_name: str
    business_name: Optional[str] = None

    # Specialties and expertise
    specialties: List[str]
    primary_modalities: List[str]
    target_domains: List[str]

    # Credentials
    years_experience: int
    credentials: List[str]
    professional_memberships: List[str] = []

    # Verification (from SCVM)
    verification_tier: str
    scvm_confidence_score: float
    trust_score: int

    # Treatment approach
    treatment_philosophy: TreatmentPhilosophy
    evidence_based: bool = True
    uses_interventions: List[str] = []

    # Location
    location_latitude: float
    location_longitude: float
    location_address: str
    travel_radius_km: float = 0

    # Pricing
    hourly_rate: float
    session_duration_minutes: int = 60
    offers_sliding_scale: bool = False
    accepts_insurance: bool = False

    # Availability
    availability_windows: List[AvailabilityWindow] = []
    accepts_new_clients: bool = True

    # Communication
    communication_style: CommunicationStyle
    languages_spoken: List[str] = ["English"]

    # Outcomes
    total_clients_treated: int = 0
    average_outcome_improvement: Optional[float] = None
    client_satisfaction_rating: Optional[float] = None

    # Profile
    bio: str = ""
    profile_photo_url: Optional[str] = None
    website: Optional[str] = None


class UserMatchingPreferences(BaseModel):
    """User preferences for practitioner matching"""
    user_id: UUID

    # Geographic constraints
    location_latitude: float
    location_longitude: float
    max_travel_distance_km: float = 10.0
    willing_to_do_virtual: bool = True

    # Budget constraints
    max_budget_per_session: float
    preferred_session_frequency: str = "weekly"

    # Preferences
    preferred_philosophies: List[TreatmentPhilosophy] = []
    preferred_communication_style: Optional[CommunicationStyle] = None
    preferred_language: str = "English"
    prefer_female: Optional[bool] = None
    prefer_male: Optional[bool] = None

    # Priority factors
    prioritize_experience: bool = True
    prioritize_credentials: bool = True
    prioritize_proximity: bool = False
    prioritize_affordability: bool = False

    # Availability
    preferred_days: List[str] = []
    preferred_times: List[str] = []

    # Deal breakers
    must_accept_insurance: bool = False
    must_offer_sliding_scale: bool = False


class MatchScore(BaseModel):
    """Match score for a single practitioner"""
    practitioner_id: UUID
    overall_score: float = Field(..., ge=0, le=100)

    # Component scores
    health_need_score: float = Field(..., ge=0, le=100)
    credibility_score: float = Field(..., ge=0, le=100)
    practical_fit_score: float = Field(..., ge=0, le=100)
    evidence_alignment_score: float = Field(..., ge=0, le=100)
    preference_match_score: float = Field(..., ge=0, le=100)

    # Weights used
    weights: Dict[str, float] = {
        "health_need": 0.40,
        "credibility": 0.25,
        "practical_fit": 0.20,
        "evidence_alignment": 0.10,
        "preference_match": 0.05
    }

    # Breakdown
    match_reasons: List[str] = []
    potential_concerns: List[str] = []

    # Distance
    distance_km: Optional[float] = None


class PractitionerRecommendation(BaseModel):
    """Complete recommendation for a practitioner"""
    recommendation_id: UUID = Field(default_factory=uuid4)
    practitioner: PractitionerProfile
    match_score: MatchScore

    # Personalized messaging
    headline: str
    why_recommended: str
    what_to_expect: str

    # Practical next steps
    estimated_sessions_needed: Optional[int] = None
    estimated_total_cost: Optional[float] = None
    available_time_slots: List[str] = []
    booking_url: Optional[str] = None

    # Social proof
    similar_client_outcomes: Optional[str] = None

    # Alternative options
    if_unavailable: Optional[str] = None


class SPRMOutput(BaseModel):
    """Complete output from SPRM matching algorithm"""
    recommendation_id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    # Results
    top_recommendations: List[PractitionerRecommendation]
    total_practitioners_considered: int
    total_practitioners_filtered: int

    # Insights
    match_summary: str
    key_factors: List[str]

    # Alternatives
    honorable_mentions: List[PractitionerRecommendation] = []

    # If no good matches
    no_match_reason: Optional[str] = None
    alternative_suggestions: List[str] = []

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sism_score_at_matching: Optional[float] = None
    weak_domains_at_matching: List[str] = []
    algorithm_version: str = "1.0"


class OutcomeRecord(BaseModel):
    """Historical outcome record for collaborative filtering"""
    record_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    practitioner_id: UUID

    # User state before treatment
    initial_sism_score: float
    initial_weak_domains: List[str]

    # Treatment
    sessions_completed: int
    total_cost: float
    duration_weeks: int

    # Outcomes
    final_sism_score: float
    improvement_percentage: float
    domains_improved: List[str]

    # Satisfaction
    client_satisfaction: int = Field(..., ge=1, le=5)
    would_recommend: bool

    # Date
    treatment_completed: datetime


# Legacy models for backwards compatibility
class PractitionerMatchInput(BaseModel):
    """Legacy input model for practitioner recommendation."""
    user_id: UUID
    health_goals: List[str]
    preferences: Dict


class PractitionerMatchOutput(BaseModel):
    """Legacy output model for practitioner recommendation."""
    practitioner_id: UUID
    match_score: float
    match_reasons: List[str]
    specialties_matched: List[str]


class MatchingInput(BaseModel):
    """Legacy input model for detailed matching."""
    user_id: UUID
    practitioner_id: UUID
    user_profile: Dict
    practitioner_profile: Dict


class MatchingOutput(BaseModel):
    """Legacy output model for detailed matching."""
    user_id: UUID
    practitioner_id: UUID
    match_score: float
    compatibility_breakdown: Dict[str, float]
    recommendations: List[str]
