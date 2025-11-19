"""
Data models for SIRM (SANA Insight & Reflection Model).
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class Persona(str, Enum):
    """Available AI reflection personas."""
    PHILOSOPHER = "philosopher"
    THERAPIST = "therapist"
    POET = "poet"
    SCIENTIST = "scientist"
    COACH = "coach"
    FRIEND = "friend"
    STOIC = "stoic"
    SPIRITUAL = "spiritual"


class EmotionalTone(str, Enum):
    """Detected emotional tones."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    ANXIOUS = "anxious"
    HOPEFUL = "hopeful"
    REFLECTIVE = "reflective"
    FRUSTRATED = "frustrated"
    GRATEFUL = "grateful"
    SAD = "sad"


class JournalEntry(BaseModel):
    """Input journal entry for analysis."""
    user_id: UUID
    content: str = Field(..., min_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Optional context
    mood_rating: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)

    # User's current health context
    health_score: Optional[float] = None
    weak_domains: Optional[List[str]] = None


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results."""
    overall_score: float = Field(..., ge=-1, le=1)  # -1 negative to 1 positive
    emotional_tone: EmotionalTone
    confidence: float = Field(..., ge=0, le=100)

    # Emotion breakdown
    emotions_detected: Dict[str, float] = {}  # {emotion: intensity 0-1}

    # Key phrases
    positive_phrases: List[str] = []
    negative_phrases: List[str] = []

    # Patterns
    cognitive_distortions: List[str] = []  # e.g., "catastrophizing", "black-and-white thinking"


class ThemeDetection(BaseModel):
    """Detected themes and patterns in journal."""
    primary_themes: List[str] = []  # Main topics discussed
    wellness_domains: List[str] = []  # Which health domains are mentioned

    # Patterns
    recurring_concerns: List[str] = []
    growth_indicators: List[str] = []
    stress_triggers: List[str] = []

    # Keywords
    keywords: List[str] = []

    # Temporal patterns (if analyzing multiple entries)
    mood_trend: Optional[str] = None  # improving, declining, stable


class WellnessSuggestion(BaseModel):
    """Evidence-based wellness suggestion."""
    suggestion: str
    rationale: str  # Why this suggestion
    evidence_base: str  # What research supports this
    domain: str  # Which wellness domain this addresses
    difficulty: str = "easy"  # easy, moderate, challenging
    time_required: str = "5-10 minutes"

    # Link to interventions
    related_intervention_ids: List[UUID] = []


class PersonaReflection(BaseModel):
    """Reflection from a specific persona."""
    persona: Persona
    reflection: str
    tone: str  # The tone/style of this reflection
    key_insight: str  # The main takeaway


class SIRMOutput(BaseModel):
    """Complete SIRM analysis output."""
    user_id: UUID
    entry_id: Optional[UUID] = None

    # Sentiment
    sentiment: SentimentAnalysis

    # Themes
    themes: ThemeDetection

    # AI Reflections
    primary_reflection: PersonaReflection
    alternative_reflections: List[PersonaReflection] = []

    # Wellness Suggestions
    suggestions: List[WellnessSuggestion] = []

    # Pattern insights (from historical analysis)
    historical_patterns: Dict[str, Any] = {}

    # Connection to health
    health_insights: List[str] = []  # How this relates to their health score

    # Timestamps
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class JournalHistory(BaseModel):
    """Historical journal data for pattern analysis."""
    entries: List[JournalEntry]
    sentiment_history: List[float] = []  # Timeline of sentiment scores
    theme_frequency: Dict[str, int] = {}  # How often themes appear
