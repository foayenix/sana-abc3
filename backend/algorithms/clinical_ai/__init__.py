"""
Clinical AI Algorithm Package
=============================

SANA AI Clinical Assistant

Provides AI-powered clinical tools including:
- SOAP note generation from voice/text
- Differential diagnosis suggestions
- Treatment protocol recommendations
- Voice-to-text transcription

Usage:
------
    from algorithms.clinical_ai import (
        SOAPGenerator,
        DiagnosisSuggester,
        ProtocolRecommender,
        VoiceProcessor,
    )

    # Generate SOAP note
    generator = SOAPGenerator(api_key="...")
    soap_note = generator.generate_soap_note(input_data)

    # Suggest diagnoses
    suggester = DiagnosisSuggester(api_key="...")
    diagnoses = suggester.suggest_diagnoses(symptoms_input)

    # Get treatment protocol
    recommender = ProtocolRecommender(api_key="...")
    protocol = recommender.recommend_protocol(protocol_input)

    # Transcribe voice
    processor = VoiceProcessor(api_key="...")
    transcription = processor.transcribe(voice_input)
"""

# Models
from .models import (
    # Enums
    ClinicalTradition,
    DiagnosisConfidence,
    ProtocolType,
    SOAPSection,

    # SOAP Models
    SOAPNoteInput,
    SOAPNote,
    SOAPNoteEdit,

    # Diagnosis Models
    Symptom,
    DiagnosisSuggestionInput,
    DifferentialDiagnosis,
    DiagnosisSuggestionResult,

    # Protocol Models
    ProtocolRecommendationInput,
    HerbRecommendation,
    SupplementRecommendation,
    LifestyleRecommendation,
    TreatmentProtocol,

    # Voice Models
    VoiceTranscriptionInput,
    VoiceTranscriptionResult,

    # Herb Models
    HerbQuery,
    HerbInfo,

    # Config
    AIGenerationConfig,
)

# Algorithms
from .soap_generator import SOAPGenerator
from .diagnosis_suggester import DiagnosisSuggester
from .protocol_recommender import ProtocolRecommender
from .voice_processor import VoiceProcessor

__all__ = [
    # Enums
    "ClinicalTradition",
    "DiagnosisConfidence",
    "ProtocolType",
    "SOAPSection",

    # SOAP Models
    "SOAPNoteInput",
    "SOAPNote",
    "SOAPNoteEdit",

    # Diagnosis Models
    "Symptom",
    "DiagnosisSuggestionInput",
    "DifferentialDiagnosis",
    "DiagnosisSuggestionResult",

    # Protocol Models
    "ProtocolRecommendationInput",
    "HerbRecommendation",
    "SupplementRecommendation",
    "LifestyleRecommendation",
    "TreatmentProtocol",

    # Voice Models
    "VoiceTranscriptionInput",
    "VoiceTranscriptionResult",

    # Herb Models
    "HerbQuery",
    "HerbInfo",

    # Config
    "AIGenerationConfig",

    # Algorithms
    "SOAPGenerator",
    "DiagnosisSuggester",
    "ProtocolRecommender",
    "VoiceProcessor",
]
