"""
SANA Herbs & Treatments Index - Data Models

Models for the Herb Index (SHI) and Treatment Modality Index (STMI)
"""
from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Enums
class PreparationForm(str, Enum):
    """Forms of herb preparation"""
    TINCTURE = "tincture"
    CAPSULE = "capsule"
    TEA = "tea"
    POWDER = "powder"
    TOPICAL = "topical"
    EXTRACT = "extract"
    WHOLE_HERB = "whole_herb"
    ESSENTIAL_OIL = "essential_oil"


class DosageUnit(str, Enum):
    """Units for dosage measurement"""
    MG = "mg"
    ML = "ml"
    DROPS = "drops"
    CAPSULES = "capsules"
    GRAMS = "g"
    TEASPOONS = "tsp"
    TABLESPOONS = "tbsp"


class Frequency(str, Enum):
    """Dosing frequency"""
    DAILY = "daily"
    BID = "BID"  # twice daily
    TID = "TID"  # three times daily
    QID = "QID"  # four times daily
    PRN = "PRN"  # as needed
    WEEKLY = "weekly"


class EvidenceLevel(str, Enum):
    """Evidence level classification"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class AdverseEventSeverity(str, Enum):
    """Severity levels for adverse events"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class TreatmentModality(str, Enum):
    """Treatment modality categories"""
    WESTERN_HERBALISM = "western_herbalism"
    TCM = "traditional_chinese_medicine"
    AYURVEDA = "ayurveda"
    ACUPUNCTURE = "acupuncture"
    CHIROPRACTIC = "chiropractic"
    MASSAGE = "massage"
    OSTEOPATHY = "osteopathy"
    NATUROPATHY = "naturopathy"
    HOMEOPATHY = "homeopathy"
    NUTRITION = "nutritional_therapy"
    MIND_BODY = "mind_body"


# Core Models
class Herb(BaseModel):
    """Master record for an herb/supplement"""
    herb_id: UUID = Field(default_factory=uuid4)
    botanical_name: str
    common_names: List[str]
    taxonomy_family: Optional[str] = None
    taxonomy_genus: Optional[str] = None
    taxonomy_species: Optional[str] = None
    active_constituents: Optional[Dict[str, str]] = None
    known_interactions: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HerbUsage(BaseModel):
    """Record of herb usage in a treatment session"""
    usage_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    herb_id: UUID
    client_id: UUID
    practitioner_id: UUID

    # Dosage information
    dosage_amount: Optional[float] = None
    dosage_unit: Optional[DosageUnit] = None
    frequency: Optional[Frequency] = None
    duration_days: Optional[int] = None

    # Preparation details
    preparation_form: Optional[PreparationForm] = None
    extract_ratio: Optional[str] = None  # e.g., "1:2", "1:5"
    standardization: Optional[str] = None  # % of active constituent

    # Treatment context
    indication_tags: List[str] = Field(default_factory=list)
    primary_condition_id: Optional[UUID] = None
    region: Optional[str] = None

    # Metadata
    prescribed_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HerbOutcome(BaseModel):
    """Outcome measurement for herb usage"""
    outcome_id: UUID = Field(default_factory=uuid4)
    usage_id: UUID
    client_id: UUID

    # Outcome measurement
    outcome_measure: str  # e.g., "DASS-21-Anxiety", "WHO-5", "VAS-Pain"
    baseline_score: float
    followup_score: float
    improvement_percentage: Optional[float] = None  # Calculated field

    # Timing
    days_since_start: int
    measurement_date: date

    # Safety
    adverse_events: List[str] = Field(default_factory=list)
    adverse_event_severity: Optional[AdverseEventSeverity] = None
    discontinued: bool = False
    discontinuation_reason: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate improvement percentage
        if self.baseline_score > 0:
            self.improvement_percentage = (
                (self.baseline_score - self.followup_score) / self.baseline_score * 100
            )
        else:
            self.improvement_percentage = 0.0


class HerbIndexScore(BaseModel):
    """SANA Herb Index (SHI) score for an herb"""
    herb_id: UUID
    herb_name: str
    botanical_name: str

    # Overall score (0-100)
    overall_score: int = Field(ge=0, le=100)

    # Component scores
    evidence_volume_score: int = Field(ge=0, le=25)
    efficacy_score: int = Field(ge=0, le=40)
    safety_score: int = Field(ge=0, le=20)
    data_quality_score: int = Field(ge=0, le=15)

    # Metadata
    total_cases: int
    unique_practitioners: int
    unique_conditions: int
    evidence_level: EvidenceLevel

    # Confidence
    confidence_interval: Tuple[float, float]

    # Timestamps
    last_calculated: datetime = Field(default_factory=datetime.utcnow)


class ConditionHerbEfficacy(BaseModel):
    """Condition-specific herb efficacy data"""
    efficacy_id: UUID = Field(default_factory=uuid4)
    herb_id: UUID
    herb_name: str
    condition_id: UUID
    condition_name: str

    # Efficacy metrics
    mean_improvement: float
    median_improvement: float
    std_deviation: float
    effect_size: float  # Cohen's d

    # Sample
    sample_size: int
    outcome_measure: str

    # Timing
    median_days_to_improvement: Optional[int] = None

    # Ranking
    rank: Optional[int] = None

    last_calculated: datetime = Field(default_factory=datetime.utcnow)


class HerbCombination(BaseModel):
    """Detected herb combination with synergy data"""
    combination_id: UUID = Field(default_factory=uuid4)
    herb_ids: List[UUID]
    herb_names: List[str]
    condition_id: Optional[UUID] = None
    condition_name: Optional[str] = None

    # Synergy metrics
    synergy_score: int = Field(ge=0, le=100)
    mean_improvement: float
    expected_improvement: float  # From individual herbs
    synergy_boost: float  # Calculated: mean - expected

    # Optimal dosages
    optimal_dosages: Dict[str, float]  # herb_name: dosage_mg
    optimal_ratio: Optional[str] = None

    # Evidence
    sample_size: int
    lift: float  # From association rules

    last_calculated: datetime = Field(default_factory=datetime.utcnow)


class TreatmentModalityScore(BaseModel):
    """SANA Treatment Modality Index (STMI) score"""
    modality: TreatmentModality
    modality_name: str

    # Overall score (0-100)
    overall_score: int = Field(ge=0, le=100)

    # Component scores
    clinical_effectiveness_score: int = Field(ge=0, le=45)
    evidence_maturity_score: int = Field(ge=0, le=25)
    safety_tolerability_score: int = Field(ge=0, le=20)
    cost_effectiveness_score: int = Field(ge=0, le=10)

    # Metadata
    total_sessions: int
    unique_practitioners: int
    conditions_treated: int

    # Best for conditions
    top_conditions: List[str]

    last_calculated: datetime = Field(default_factory=datetime.utcnow)


# API Input/Output Models
class HerbSearchInput(BaseModel):
    """Input for herb search"""
    query: Optional[str] = None
    condition_id: Optional[UUID] = None
    min_score: int = 0
    min_evidence_level: Optional[EvidenceLevel] = None
    limit: int = 20


class HerbSearchResult(BaseModel):
    """Search result for herbs"""
    herbs: List[HerbIndexScore]
    total_count: int
    query: Optional[str] = None
    filters_applied: Dict[str, str] = Field(default_factory=dict)


class HerbComparisonInput(BaseModel):
    """Input for comparing herbs"""
    herb_ids: List[UUID]
    condition_id: Optional[UUID] = None


class HerbComparisonResult(BaseModel):
    """Result of herb comparison"""
    herbs: List[HerbIndexScore]
    condition_efficacies: Optional[List[ConditionHerbEfficacy]] = None
    comparison_metrics: Dict[str, Dict[str, float]]  # metric -> herb_id -> value


class HerbRankingInput(BaseModel):
    """Input for herb rankings"""
    condition_id: UUID
    metric: str = "efficacy"  # efficacy, safety, overall
    limit: int = 10


class HerbRankingResult(BaseModel):
    """Ranked list of herbs for a condition"""
    condition_id: UUID
    condition_name: str
    metric: str
    rankings: List[ConditionHerbEfficacy]


class SynergySearchInput(BaseModel):
    """Input for synergy search"""
    min_synergy_score: int = 70
    condition_id: Optional[UUID] = None
    min_sample_size: int = 30
    limit: int = 20


class SynergySearchResult(BaseModel):
    """Result of synergy search"""
    combinations: List[HerbCombination]
    total_found: int


class HerbDetailResponse(BaseModel):
    """Full herb details response"""
    herb: Herb
    index_score: HerbIndexScore
    top_conditions: List[ConditionHerbEfficacy]
    common_combinations: List[HerbCombination]
    safety_summary: Dict[str, Any]
    usage_guidelines: Dict[str, str]


class ResearchExportRequest(BaseModel):
    """Request for research data export"""
    herb_ids: Optional[List[UUID]] = None
    condition_ids: Optional[List[UUID]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    min_sample_size: int = 30
    include_demographics: bool = False
    format: str = "parquet"  # parquet, csv


class ResearchExportResponse(BaseModel):
    """Response for research data export"""
    export_id: UUID = Field(default_factory=uuid4)
    download_url: str
    record_count: int
    file_size_mb: float
    expiry_time: datetime
    anonymization_applied: List[str]
