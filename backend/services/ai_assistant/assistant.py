"""
AI Assistant Service
====================
Main service for the AI Clinical Assistant, orchestrating all AI features.
"""

import logging
import os
from typing import Optional, List, Dict
from uuid import UUID

from algorithms.clinical_ai import (
    SOAPGenerator,
    DiagnosisSuggester,
    ProtocolRecommender,
    VoiceProcessor,
    SOAPNoteInput,
    SOAPNote,
    DiagnosisSuggestionInput,
    DiagnosisSuggestionResult,
    ProtocolRecommendationInput,
    TreatmentProtocol,
    VoiceTranscriptionInput,
    VoiceTranscriptionResult,
    Symptom,
    ClinicalTradition,
)

logger = logging.getLogger(__name__)


class AIAssistantService:
    """
    AI Clinical Assistant Service

    Provides a unified interface for:
    - SOAP note generation
    - Differential diagnosis suggestions
    - Treatment protocol recommendations
    - Voice transcription

    Free tier includes 100 AI generations/month.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI assistant service

        Args:
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.soap_generator = SOAPGenerator(self.api_key)
        self.diagnosis_suggester = DiagnosisSuggester(self.api_key)
        self.protocol_recommender = ProtocolRecommender(self.api_key)
        self.voice_processor = VoiceProcessor(self.api_key)

    def generate_soap_note(
        self,
        chief_complaint: Optional[str] = None,
        symptoms: List[str] = None,
        free_text_notes: Optional[str] = None,
        voice_transcription: Optional[str] = None,
        vitals: Optional[Dict] = None,
        physical_exam_notes: Optional[str] = None,
        lab_results: Optional[Dict] = None,
        patient_history: Optional[str] = None,
        current_medications: List[str] = None,
        current_supplements: List[str] = None,
        tradition: str = "general",
        session_id: Optional[UUID] = None,
    ) -> Dict:
        """
        Generate a SOAP note from clinical information

        Args:
            chief_complaint: Primary reason for visit
            symptoms: List of symptoms
            free_text_notes: Free-form clinical notes
            voice_transcription: Transcribed voice notes
            vitals: Vital signs dict
            physical_exam_notes: Physical exam findings
            lab_results: Lab results dict
            patient_history: Medical history
            current_medications: Current medications
            current_supplements: Current supplements
            tradition: Clinical tradition (western_herbalism, tcm, etc.)
            session_id: Session ID for tracking

        Returns:
            Generated SOAP note as dictionary
        """
        # Map tradition string to enum
        try:
            tradition_enum = ClinicalTradition(tradition.lower())
        except ValueError:
            tradition_enum = ClinicalTradition.GENERAL

        input_data = SOAPNoteInput(
            session_id=session_id,
            chief_complaint=chief_complaint,
            symptoms=symptoms or [],
            free_text_notes=free_text_notes,
            voice_transcription=voice_transcription,
            vitals=vitals,
            physical_exam_notes=physical_exam_notes,
            lab_results=lab_results,
            patient_history=patient_history,
            current_medications=current_medications or [],
            current_supplements=current_supplements or [],
            tradition=tradition_enum,
        )

        soap_note = self.soap_generator.generate_soap_note(input_data)

        return {
            "id": str(soap_note.id),
            "session_id": str(soap_note.session_id) if soap_note.session_id else None,
            "subjective": soap_note.subjective,
            "objective": soap_note.objective,
            "assessment": soap_note.assessment,
            "plan": soap_note.plan,
            "diagnoses": soap_note.diagnoses,
            "recommended_herbs": soap_note.recommended_herbs,
            "recommended_supplements": soap_note.recommended_supplements,
            "lifestyle_recommendations": soap_note.lifestyle_recommendations,
            "follow_up": soap_note.follow_up,
            "tradition": soap_note.tradition.value,
            "confidence_score": soap_note.confidence_score,
            "ai_model_used": soap_note.ai_model_used,
            "generated_at": soap_note.generated_at.isoformat(),
        }

    def suggest_diagnoses(
        self,
        symptoms: List[Dict],
        patient_age: Optional[int] = None,
        patient_sex: Optional[str] = None,
        medical_history: List[str] = None,
        family_history: List[str] = None,
        current_medications: List[str] = None,
        tradition: str = "general",
    ) -> Dict:
        """
        Suggest differential diagnoses based on symptoms

        Args:
            symptoms: List of symptom dicts with name, duration, severity
            patient_age: Patient's age
            patient_sex: Patient's sex
            medical_history: Past medical history
            family_history: Family medical history
            current_medications: Current medications
            tradition: Clinical tradition

        Returns:
            Differential diagnosis suggestions
        """
        # Convert symptom dicts to Symptom objects
        symptom_objects = [
            Symptom(
                name=s.get("name", s) if isinstance(s, dict) else s,
                duration=s.get("duration") if isinstance(s, dict) else None,
                severity=s.get("severity") if isinstance(s, dict) else None,
            )
            for s in symptoms
        ]

        try:
            tradition_enum = ClinicalTradition(tradition.lower())
        except ValueError:
            tradition_enum = ClinicalTradition.GENERAL

        input_data = DiagnosisSuggestionInput(
            symptoms=symptom_objects,
            patient_age=patient_age,
            patient_sex=patient_sex,
            medical_history=medical_history or [],
            family_history=family_history or [],
            current_medications=current_medications or [],
            tradition=tradition_enum,
        )

        result = self.diagnosis_suggester.suggest_diagnoses(input_data)

        return {
            "id": str(result.id),
            "differential_diagnoses": [
                {
                    "condition": d.condition,
                    "icd_code": d.icd_code,
                    "confidence": d.confidence.value,
                    "confidence_score": d.confidence_score,
                    "supporting_symptoms": d.supporting_symptoms,
                    "against_symptoms": d.against_symptoms,
                    "red_flags": d.red_flags,
                    "recommended_tests": d.recommended_tests,
                    "notes": d.notes,
                }
                for d in result.differential_diagnoses
            ],
            "primary_impression": result.primary_impression,
            "red_flags": result.red_flags,
            "recommended_referrals": result.recommended_referrals,
            "disclaimer": result.disclaimer,
            "generated_at": result.generated_at.isoformat(),
        }

    def recommend_protocol(
        self,
        condition: str,
        tradition: str = "western_herbalism",
        patient_age: Optional[int] = None,
        patient_sex: Optional[str] = None,
        contraindications: List[str] = None,
        current_medications: List[str] = None,
        severity: str = "moderate",
    ) -> Dict:
        """
        Recommend treatment protocol for a condition

        Args:
            condition: Condition/diagnosis
            tradition: Clinical tradition
            patient_age: Patient's age
            patient_sex: Patient's sex
            contraindications: Allergies and contraindications
            current_medications: Current medications
            severity: Condition severity (mild, moderate, severe)

        Returns:
            Treatment protocol recommendations
        """
        try:
            tradition_enum = ClinicalTradition(tradition.lower())
        except ValueError:
            tradition_enum = ClinicalTradition.WESTERN_HERBALISM

        input_data = ProtocolRecommendationInput(
            condition=condition,
            tradition=tradition_enum,
            patient_age=patient_age,
            patient_sex=patient_sex,
            contraindications=contraindications or [],
            current_medications=current_medications or [],
            severity=severity,
        )

        protocol = self.protocol_recommender.recommend_protocol(input_data)

        return {
            "id": str(protocol.id),
            "condition": protocol.condition,
            "tradition": protocol.tradition.value,
            "herbs": [
                {
                    "herb_name": h.herb_name,
                    "botanical_name": h.botanical_name,
                    "dosage": h.dosage,
                    "form": h.form,
                    "frequency": h.frequency,
                    "duration": h.duration,
                    "rationale": h.rationale,
                    "cautions": h.cautions,
                }
                for h in protocol.herbs
            ],
            "supplements": [
                {
                    "name": s.name,
                    "dosage": s.dosage,
                    "form": s.form,
                    "frequency": s.frequency,
                    "duration": s.duration,
                    "rationale": s.rationale,
                }
                for s in protocol.supplements
            ],
            "lifestyle": [
                {
                    "category": l.category,
                    "recommendation": l.recommendation,
                    "rationale": l.rationale,
                    "priority": l.priority,
                }
                for l in protocol.lifestyle
            ],
            "traditional_pattern": protocol.traditional_pattern,
            "classical_formula": protocol.classical_formula,
            "expected_timeline": protocol.expected_timeline,
            "follow_up_recommendations": protocol.follow_up_recommendations,
            "disclaimer": protocol.disclaimer,
            "generated_at": protocol.generated_at.isoformat(),
        }

    def transcribe_voice(
        self,
        audio_base64: Optional[str] = None,
        audio_url: Optional[str] = None,
        audio_format: str = "mp3",
        language: str = "en",
    ) -> Dict:
        """
        Transcribe voice audio to text

        Args:
            audio_base64: Base64-encoded audio
            audio_url: URL to audio file
            audio_format: Audio format (mp3, wav, etc.)
            language: Language code

        Returns:
            Transcription result
        """
        input_data = VoiceTranscriptionInput(
            audio_base64=audio_base64,
            audio_url=audio_url,
            audio_format=audio_format,
            language=language,
        )

        result = self.voice_processor.transcribe(input_data)

        return {
            "id": str(result.id),
            "transcription": result.transcription,
            "confidence": result.confidence,
            "duration_seconds": result.duration_seconds,
            "language_detected": result.language_detected,
            "processing_time_ms": result.processing_time_ms,
            "transcribed_at": result.transcribed_at.isoformat(),
        }

    def voice_to_soap(
        self,
        audio_base64: Optional[str] = None,
        audio_url: Optional[str] = None,
        audio_format: str = "mp3",
        tradition: str = "general",
        current_medications: List[str] = None,
        session_id: Optional[UUID] = None,
    ) -> Dict:
        """
        Transcribe voice and generate SOAP note in one step

        Args:
            audio_base64: Base64-encoded audio
            audio_url: URL to audio file
            audio_format: Audio format
            tradition: Clinical tradition
            current_medications: Current medications
            session_id: Session ID

        Returns:
            Combined transcription and SOAP note
        """
        # First transcribe
        transcription_result = self.transcribe_voice(
            audio_base64=audio_base64,
            audio_url=audio_url,
            audio_format=audio_format,
        )

        if transcription_result["confidence"] < 0.5:
            return {
                "error": "Transcription quality too low",
                "transcription": transcription_result,
                "soap_note": None,
            }

        # Then generate SOAP
        soap_result = self.generate_soap_note(
            voice_transcription=transcription_result["transcription"],
            tradition=tradition,
            current_medications=current_medications,
            session_id=session_id,
        )

        return {
            "transcription": transcription_result,
            "soap_note": soap_result,
        }

    def check_red_flags(self, symptoms: List[str]) -> Dict:
        """
        Quick check for red flag symptoms

        Args:
            symptoms: List of symptom names

        Returns:
            Red flags found and recommendations
        """
        symptom_objects = [Symptom(name=s) for s in symptoms]
        red_flags = self.diagnosis_suggester.check_red_flags(symptom_objects)

        return {
            "red_flags_found": len(red_flags) > 0,
            "red_flags": red_flags,
            "urgent_action_needed": any(
                "emergency" in rf.lower() or "immediate" in rf.lower()
                for rf in red_flags
            ),
        }
