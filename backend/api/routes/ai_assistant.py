"""
AI Clinical Assistant API Routes
================================
API endpoints for the SANA AI Clinical Assistant.
Free forever tool for practitioners with premium features available.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from services.ai_assistant import AIAssistantService

router = APIRouter()

# Initialize service
ai_service = AIAssistantService()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GenerateSOAPRequest(BaseModel):
    """Request for SOAP note generation"""
    chief_complaint: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    free_text_notes: Optional[str] = None
    voice_transcription: Optional[str] = None
    vitals: Optional[Dict[str, Any]] = None
    physical_exam_notes: Optional[str] = None
    lab_results: Optional[Dict[str, Any]] = None
    patient_history: Optional[str] = None
    current_medications: List[str] = Field(default_factory=list)
    current_supplements: List[str] = Field(default_factory=list)
    tradition: str = Field(default="general")
    session_id: Optional[UUID] = None


class SymptomInput(BaseModel):
    """Individual symptom input"""
    name: str
    duration: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=10)


class SuggestDiagnosisRequest(BaseModel):
    """Request for diagnosis suggestions"""
    symptoms: List[SymptomInput]
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    patient_sex: Optional[str] = None
    medical_history: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    tradition: str = Field(default="general")


class RecommendProtocolRequest(BaseModel):
    """Request for treatment protocol recommendation"""
    condition: str = Field(..., min_length=2)
    tradition: str = Field(default="western_herbalism")
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    severity: str = Field(default="moderate")


class TranscribeVoiceRequest(BaseModel):
    """Request for voice transcription"""
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    audio_format: str = Field(default="mp3")
    language: str = Field(default="en")


class VoiceToSOAPRequest(BaseModel):
    """Request for voice-to-SOAP"""
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    audio_format: str = Field(default="mp3")
    tradition: str = Field(default="general")
    current_medications: List[str] = Field(default_factory=list)
    session_id: Optional[UUID] = None


class RedFlagCheckRequest(BaseModel):
    """Request for red flag check"""
    symptoms: List[str]


# ============================================================================
# SOAP NOTE ENDPOINTS
# ============================================================================

@router.post("/generate-soap", summary="Generate SOAP note")
async def generate_soap(request: GenerateSOAPRequest):
    """
    Generate a SOAP note from clinical information.

    Accepts:
    - Chief complaint and symptoms
    - Free-text clinical notes
    - Voice transcription (pre-transcribed)
    - Vitals and physical exam findings
    - Lab results
    - Patient history and medications

    Returns a structured SOAP note with:
    - Subjective, Objective, Assessment, Plan sections
    - Extracted diagnoses and recommendations
    - AI confidence score
    """
    try:
        result = ai_service.generate_soap_note(
            chief_complaint=request.chief_complaint,
            symptoms=request.symptoms,
            free_text_notes=request.free_text_notes,
            voice_transcription=request.voice_transcription,
            vitals=request.vitals,
            physical_exam_notes=request.physical_exam_notes,
            lab_results=request.lab_results,
            patient_history=request.patient_history,
            current_medications=request.current_medications,
            current_supplements=request.current_supplements,
            tradition=request.tradition,
            session_id=request.session_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SOAP generation failed: {str(e)}")


# ============================================================================
# DIAGNOSIS ENDPOINTS
# ============================================================================

@router.post("/suggest-diagnosis", summary="Suggest differential diagnoses")
async def suggest_diagnosis(request: SuggestDiagnosisRequest):
    """
    Suggest differential diagnoses based on symptoms.

    Analyzes symptoms and patient history to provide:
    - Ranked differential diagnoses
    - Confidence levels
    - Supporting and contradicting symptoms
    - Red flags to watch for
    - Recommended diagnostic tests

    Note: This is a decision support tool. Clinical judgment required.
    """
    try:
        symptoms_dict = [
            {"name": s.name, "duration": s.duration, "severity": s.severity}
            for s in request.symptoms
        ]

        result = ai_service.suggest_diagnoses(
            symptoms=symptoms_dict,
            patient_age=request.patient_age,
            patient_sex=request.patient_sex,
            medical_history=request.medical_history,
            family_history=request.family_history,
            current_medications=request.current_medications,
            tradition=request.tradition,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis suggestion failed: {str(e)}")


@router.post("/check-red-flags", summary="Check for red flag symptoms")
async def check_red_flags(request: RedFlagCheckRequest):
    """
    Quick check for red flag symptoms that require urgent attention.

    Returns:
    - Whether red flags were found
    - List of specific warnings
    - Whether urgent action is needed
    """
    result = ai_service.check_red_flags(request.symptoms)
    return result


# ============================================================================
# PROTOCOL ENDPOINTS
# ============================================================================

@router.post("/recommend-protocol", summary="Recommend treatment protocol")
async def recommend_protocol(request: RecommendProtocolRequest):
    """
    Recommend treatment protocol for a condition.

    Provides tradition-specific recommendations:
    - Herbal formulas with dosages
    - Supplement suggestions
    - Lifestyle modifications
    - Follow-up recommendations

    Traditions supported:
    - western_herbalism
    - traditional_chinese_medicine
    - ayurveda
    - naturopathy
    - functional_medicine
    """
    try:
        result = ai_service.recommend_protocol(
            condition=request.condition,
            tradition=request.tradition,
            patient_age=request.patient_age,
            patient_sex=request.patient_sex,
            contraindications=request.contraindications,
            current_medications=request.current_medications,
            severity=request.severity,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protocol recommendation failed: {str(e)}")


@router.get("/traditions", summary="Get supported clinical traditions")
async def get_traditions():
    """Get list of supported clinical traditions"""
    return {
        "traditions": [
            {"value": "western_herbalism", "label": "Western Herbalism"},
            {"value": "traditional_chinese_medicine", "label": "Traditional Chinese Medicine"},
            {"value": "ayurveda", "label": "Ayurveda"},
            {"value": "naturopathy", "label": "Naturopathy"},
            {"value": "functional_medicine", "label": "Functional Medicine"},
            {"value": "homeopathy", "label": "Homeopathy"},
            {"value": "nutrition", "label": "Clinical Nutrition"},
            {"value": "general", "label": "General Integrative"},
        ]
    }


# ============================================================================
# VOICE ENDPOINTS
# ============================================================================

@router.post("/voice-to-text", summary="Transcribe voice to text")
async def voice_to_text(request: TranscribeVoiceRequest):
    """
    Transcribe clinical voice notes to text.

    Supports audio formats: mp3, mp4, wav, m4a, webm

    Returns:
    - Transcription text
    - Confidence score
    - Audio duration
    - Processing time
    """
    if not request.audio_base64 and not request.audio_url:
        raise HTTPException(
            status_code=400,
            detail="Either audio_base64 or audio_url must be provided"
        )

    try:
        result = ai_service.transcribe_voice(
            audio_base64=request.audio_base64,
            audio_url=request.audio_url,
            audio_format=request.audio_format,
            language=request.language,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/voice-to-soap", summary="Voice to SOAP note (combined)")
async def voice_to_soap(request: VoiceToSOAPRequest):
    """
    Combined voice transcription and SOAP note generation.

    One-step workflow:
    1. Transcribes voice audio
    2. Generates SOAP note from transcription

    Returns both transcription and SOAP note.
    """
    if not request.audio_base64 and not request.audio_url:
        raise HTTPException(
            status_code=400,
            detail="Either audio_base64 or audio_url must be provided"
        )

    try:
        result = ai_service.voice_to_soap(
            audio_base64=request.audio_base64,
            audio_url=request.audio_url,
            audio_format=request.audio_format,
            tradition=request.tradition,
            current_medications=request.current_medications,
            session_id=request.session_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice-to-SOAP failed: {str(e)}")


# ============================================================================
# INFO ENDPOINTS
# ============================================================================

@router.get("/test-scenarios", summary="Get test scenarios")
async def get_test_scenarios():
    """Get test scenarios for exploring the AI Assistant API"""
    return {
        "scenarios": [
            {
                "name": "Generate SOAP note",
                "endpoint": "POST /ai/generate-soap",
                "request": {
                    "chief_complaint": "Chronic anxiety and sleep difficulties",
                    "symptoms": ["anxiety", "insomnia", "racing thoughts", "fatigue"],
                    "patient_history": "History of work-related stress",
                    "current_medications": [],
                    "tradition": "western_herbalism",
                },
            },
            {
                "name": "Suggest diagnoses",
                "endpoint": "POST /ai/suggest-diagnosis",
                "request": {
                    "symptoms": [
                        {"name": "fatigue", "duration": "3 months", "severity": 7},
                        {"name": "brain fog", "severity": 6},
                        {"name": "weight gain", "duration": "6 months"},
                        {"name": "cold intolerance"},
                    ],
                    "patient_age": 45,
                    "patient_sex": "female",
                },
            },
            {
                "name": "Recommend protocol",
                "endpoint": "POST /ai/recommend-protocol",
                "request": {
                    "condition": "anxiety",
                    "tradition": "western_herbalism",
                    "severity": "moderate",
                },
            },
            {
                "name": "Check red flags",
                "endpoint": "POST /ai/check-red-flags",
                "request": {
                    "symptoms": ["severe headache", "neck stiffness", "fever"],
                },
            },
        ]
    }


@router.get("/usage", summary="Get AI usage limits")
async def get_usage_limits():
    """Get current AI usage limits and quotas"""
    return {
        "free_tier": {
            "ai_generations_per_month": 100,
            "voice_minutes_per_month": 30,
            "features": [
                "SOAP note generation",
                "Basic diagnosis suggestions",
                "Protocol recommendations",
                "Voice transcription",
            ],
        },
        "professional_tier": {
            "ai_generations_per_month": "unlimited",
            "voice_minutes_per_month": "unlimited",
            "additional_features": [
                "Advanced AI models",
                "Custom protocol templates",
                "Integration with EMR",
                "Priority processing",
            ],
        },
        "disclaimer": "AI features require professional oversight. Not a replacement for clinical judgment.",
    }
