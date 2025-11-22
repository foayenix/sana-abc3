"""
Clinical AI Models
==================
Pydantic models for the AI Clinical Assistant.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ClinicalTradition(str, Enum):
    """Clinical modality/tradition"""
    WESTERN_HERBALISM = "western_herbalism"
    TRADITIONAL_CHINESE_MEDICINE = "traditional_chinese_medicine"
    AYURVEDA = "ayurveda"
    NATUROPATHY = "naturopathy"
    FUNCTIONAL_MEDICINE = "functional_medicine"
    HOMEOPATHY = "homeopathy"
    NUTRITION = "nutrition"
    GENERAL = "general"


class DiagnosisConfidence(str, Enum):
    """Confidence level for diagnosis suggestions"""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNCERTAIN = "uncertain"


class ProtocolType(str, Enum):
    """Type of treatment protocol"""
    HERBAL = "herbal"
    NUTRITIONAL = "nutritional"
    LIFESTYLE = "lifestyle"
    COMBINATION = "combination"


class SOAPSection(str, Enum):
    """SOAP note sections"""
    SUBJECTIVE = "subjective"
    OBJECTIVE = "objective"
    ASSESSMENT = "assessment"
    PLAN = "plan"


# ============================================================================
# SOAP NOTE MODELS
# ============================================================================

class SOAPNoteInput(BaseModel):
    """Input for SOAP note generation"""
    session_id: Optional[UUID] = None
    practitioner_id: Optional[UUID] = None
    client_id: Optional[UUID] = None

    # Raw input (at least one required)
    voice_note_url: Optional[str] = None
    voice_transcription: Optional[str] = None
    free_text_notes: Optional[str] = None

    # Structured input (optional, supplements free text)
    chief_complaint: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    symptom_duration: Optional[str] = None
    symptom_severity: Optional[int] = Field(None, ge=1, le=10)

    # Objective findings
    vitals: Optional[Dict[str, Any]] = None  # BP, pulse, temp, etc.
    physical_exam_notes: Optional[str] = None
    lab_results: Optional[Dict[str, Any]] = None

    # Context
    patient_history: Optional[str] = None
    current_medications: List[str] = Field(default_factory=list)
    current_supplements: List[str] = Field(default_factory=list)
    tradition: ClinicalTradition = ClinicalTradition.GENERAL


class SOAPNote(BaseModel):
    """Generated SOAP note"""
    id: UUID = Field(default_factory=uuid4)
    session_id: Optional[UUID] = None

    # SOAP sections
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""

    # Extracted/structured data
    diagnoses: List[str] = Field(default_factory=list)
    icd_codes: List[str] = Field(default_factory=list)
    recommended_herbs: List[str] = Field(default_factory=list)
    recommended_supplements: List[str] = Field(default_factory=list)
    lifestyle_recommendations: List[str] = Field(default_factory=list)
    follow_up: Optional[str] = None

    # Metadata
    tradition: ClinicalTradition = ClinicalTradition.GENERAL
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    ai_model_used: str = "gpt-4"
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Source tracking
    source_voice_transcription: Optional[str] = None
    source_free_text: Optional[str] = None


class SOAPNoteEdit(BaseModel):
    """Edit to a SOAP note section"""
    section: SOAPSection
    original_text: str
    edited_text: str
    edited_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# DIAGNOSIS MODELS
# ============================================================================

class Symptom(BaseModel):
    """Individual symptom with details"""
    name: str
    duration: Optional[str] = None  # "2 weeks", "chronic"
    severity: Optional[int] = Field(None, ge=1, le=10)
    frequency: Optional[str] = None  # "daily", "occasional"
    aggravating_factors: List[str] = Field(default_factory=list)
    relieving_factors: List[str] = Field(default_factory=list)


class DiagnosisSuggestionInput(BaseModel):
    """Input for diagnosis suggestion"""
    symptoms: List[Symptom]
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None  # "male", "female", "other"
    medical_history: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    lifestyle_factors: Optional[Dict[str, Any]] = None  # diet, exercise, stress
    tradition: ClinicalTradition = ClinicalTradition.GENERAL


class DifferentialDiagnosis(BaseModel):
    """Single differential diagnosis suggestion"""
    condition: str
    icd_code: Optional[str] = None
    confidence: DiagnosisConfidence
    confidence_score: float = Field(ge=0, le=1)
    supporting_symptoms: List[str] = Field(default_factory=list)
    against_symptoms: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    recommended_tests: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class DiagnosisSuggestionResult(BaseModel):
    """Result of diagnosis suggestion"""
    id: UUID = Field(default_factory=uuid4)
    differential_diagnoses: List[DifferentialDiagnosis]
    primary_impression: Optional[str] = None
    red_flags: List[str] = Field(default_factory=list)
    recommended_referrals: List[str] = Field(default_factory=list)
    disclaimer: str = "This is an AI-assisted suggestion. Clinical judgment is required."
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# PROTOCOL MODELS
# ============================================================================

class ProtocolRecommendationInput(BaseModel):
    """Input for treatment protocol recommendation"""
    condition: str
    tradition: ClinicalTradition = ClinicalTradition.WESTERN_HERBALISM
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)  # Allergies, conditions
    current_medications: List[str] = Field(default_factory=list)
    preferences: Optional[Dict[str, Any]] = None  # vegan, alcohol-free, etc.
    severity: str = "moderate"  # mild, moderate, severe


class HerbRecommendation(BaseModel):
    """Individual herb recommendation"""
    herb_name: str
    botanical_name: Optional[str] = None
    dosage: str
    form: str  # tincture, capsule, tea, etc.
    frequency: str  # "3x daily", "as needed"
    duration: str  # "4-6 weeks"
    rationale: str
    cautions: List[str] = Field(default_factory=list)
    evidence_level: str = "traditional"  # traditional, moderate, strong


class SupplementRecommendation(BaseModel):
    """Individual supplement recommendation"""
    name: str
    dosage: str
    form: str
    frequency: str
    duration: str
    rationale: str
    cautions: List[str] = Field(default_factory=list)


class LifestyleRecommendation(BaseModel):
    """Lifestyle recommendation"""
    category: str  # diet, exercise, sleep, stress
    recommendation: str
    rationale: str
    priority: str = "medium"  # low, medium, high


class TreatmentProtocol(BaseModel):
    """Complete treatment protocol"""
    id: UUID = Field(default_factory=uuid4)
    condition: str
    tradition: ClinicalTradition

    # Recommendations
    herbs: List[HerbRecommendation] = Field(default_factory=list)
    supplements: List[SupplementRecommendation] = Field(default_factory=list)
    lifestyle: List[LifestyleRecommendation] = Field(default_factory=list)

    # Traditional references
    traditional_pattern: Optional[str] = None  # TCM pattern, Ayurvedic dosha, etc.
    classical_formula: Optional[str] = None
    classical_references: List[str] = Field(default_factory=list)

    # Evidence
    evidence_references: List[str] = Field(default_factory=list)

    # Follow-up
    expected_timeline: str = "4-8 weeks"
    follow_up_recommendations: List[str] = Field(default_factory=list)
    monitoring_parameters: List[str] = Field(default_factory=list)

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    disclaimer: str = "Treatment recommendations require professional oversight."


# ============================================================================
# VOICE PROCESSING MODELS
# ============================================================================

class VoiceTranscriptionInput(BaseModel):
    """Input for voice transcription"""
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    audio_format: str = "mp3"  # mp3, wav, m4a, webm
    language: str = "en"


class VoiceTranscriptionResult(BaseModel):
    """Result of voice transcription"""
    id: UUID = Field(default_factory=uuid4)
    transcription: str
    confidence: float = Field(ge=0, le=1)
    duration_seconds: float = 0
    language_detected: str = "en"
    timestamps: Optional[List[Dict[str, Any]]] = None  # Word-level timestamps
    processing_time_ms: int = 0
    transcribed_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# HERB DATABASE QUERY MODELS
# ============================================================================

class HerbQuery(BaseModel):
    """Query for herb information"""
    herb_name: Optional[str] = None
    condition: Optional[str] = None
    tradition: ClinicalTradition = ClinicalTradition.GENERAL
    action: Optional[str] = None  # "anti-inflammatory", "adaptogen"


class HerbInfo(BaseModel):
    """Herb information from database"""
    common_name: str
    botanical_name: str
    family: Optional[str] = None
    parts_used: List[str] = Field(default_factory=list)

    # Actions & Indications
    primary_actions: List[str] = Field(default_factory=list)
    secondary_actions: List[str] = Field(default_factory=list)
    indications: List[str] = Field(default_factory=list)

    # Dosage
    typical_dosage: Dict[str, str] = Field(default_factory=dict)  # form -> dosage

    # Safety
    contraindications: List[str] = Field(default_factory=list)
    drug_interactions: List[str] = Field(default_factory=list)
    cautions: List[str] = Field(default_factory=list)
    pregnancy_safety: str = "unknown"  # safe, caution, avoid, unknown

    # Traditional info
    traditional_uses: Dict[str, List[str]] = Field(default_factory=dict)  # tradition -> uses
    energetics: Optional[Dict[str, str]] = None  # taste, temperature, etc.

    # Evidence
    evidence_summary: Optional[str] = None
    key_references: List[str] = Field(default_factory=list)


# ============================================================================
# AI GENERATION CONFIG
# ============================================================================

class AIGenerationConfig(BaseModel):
    """Configuration for AI generation"""
    model: str = "gpt-4"
    temperature: float = Field(default=0.3, ge=0, le=1)
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    include_references: bool = True
    include_icd_codes: bool = True
    formality_level: str = "professional"  # casual, professional, academic
    tradition_specific: bool = True
