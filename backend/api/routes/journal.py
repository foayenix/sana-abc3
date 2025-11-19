"""
Journal API routes for SANA Platform.

Provides endpoints for journal analysis using SIRM (Insight & Reflection Model).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from algorithms.reflection.sirm import SIRMAlgorithm
from algorithms.reflection.models import (
    JournalEntry,
    Persona,
    SIRMOutput
)

router = APIRouter()

# Initialize algorithm
sirm = SIRMAlgorithm()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class JournalAnalysisRequest(BaseModel):
    """Request to analyze a journal entry."""
    content: str = Field(..., min_length=10, description="Journal entry text")
    preferred_persona: Optional[Persona] = None

    # Optional context
    mood_rating: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)

    # Health context
    health_score: Optional[float] = None
    weak_domains: Optional[List[str]] = None


class PersonaInfo(BaseModel):
    """Information about a reflection persona."""
    name: str
    description: str
    tone: str
    best_for: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/analyze", response_model=dict)
async def analyze_journal_entry(request: JournalAnalysisRequest):
    """
    Analyze a journal entry and get AI reflections.

    Returns sentiment analysis, theme detection, personalized reflections
    from AI personas, and evidence-based wellness suggestions.
    """
    # Create entry object
    entry = JournalEntry(
        user_id=uuid4(),  # Would come from auth in production
        content=request.content,
        mood_rating=request.mood_rating,
        energy_level=request.energy_level,
        sleep_quality=request.sleep_quality,
        health_score=request.health_score,
        weak_domains=request.weak_domains
    )

    # Analyze
    result = sirm.analyze(entry, request.preferred_persona)

    # Convert to dict for response
    return {
        "entry_id": str(result.entry_id),
        "sentiment": {
            "overall_score": result.sentiment.overall_score,
            "emotional_tone": result.sentiment.emotional_tone.value,
            "confidence": result.sentiment.confidence,
            "emotions_detected": result.sentiment.emotions_detected,
            "positive_phrases": result.sentiment.positive_phrases,
            "negative_phrases": result.sentiment.negative_phrases,
            "cognitive_distortions": result.sentiment.cognitive_distortions
        },
        "themes": {
            "primary_themes": result.themes.primary_themes,
            "wellness_domains": result.themes.wellness_domains,
            "recurring_concerns": result.themes.recurring_concerns,
            "growth_indicators": result.themes.growth_indicators,
            "stress_triggers": result.themes.stress_triggers,
            "keywords": result.themes.keywords
        },
        "primary_reflection": {
            "persona": result.primary_reflection.persona.value,
            "reflection": result.primary_reflection.reflection,
            "tone": result.primary_reflection.tone,
            "key_insight": result.primary_reflection.key_insight
        },
        "alternative_reflections": [
            {
                "persona": r.persona.value,
                "reflection": r.reflection,
                "tone": r.tone,
                "key_insight": r.key_insight
            }
            for r in result.alternative_reflections
        ],
        "suggestions": [
            {
                "suggestion": s.suggestion,
                "rationale": s.rationale,
                "evidence_base": s.evidence_base,
                "domain": s.domain,
                "difficulty": s.difficulty,
                "time_required": s.time_required
            }
            for s in result.suggestions
        ],
        "health_insights": result.health_insights,
        "analyzed_at": result.analyzed_at.isoformat()
    }


@router.get("/personas")
async def get_available_personas():
    """Get information about all available reflection personas."""
    personas = [
        {
            "id": "philosopher",
            "name": "The Philosopher",
            "description": "Explores deeper meaning and questions assumptions",
            "tone": "Contemplative and questioning",
            "best_for": "When you want to explore meaning and values"
        },
        {
            "id": "therapist",
            "name": "The Therapist",
            "description": "Validates feelings while gently exploring patterns",
            "tone": "Warm and validating",
            "best_for": "When you need emotional support and validation"
        },
        {
            "id": "poet",
            "name": "The Poet",
            "description": "Uses imagery and metaphor to illuminate feelings",
            "tone": "Metaphorical and evocative",
            "best_for": "When you want a creative perspective"
        },
        {
            "id": "scientist",
            "name": "The Scientist",
            "description": "Examines patterns and suggests research-backed strategies",
            "tone": "Analytical and evidence-based",
            "best_for": "When you want logical analysis and data"
        },
        {
            "id": "coach",
            "name": "The Coach",
            "description": "Focuses on goals, strengths, and next steps",
            "tone": "Motivating and action-oriented",
            "best_for": "When you need motivation and direction"
        },
        {
            "id": "friend",
            "name": "The Friend",
            "description": "Offers friendly support and practical perspective",
            "tone": "Casual and supportive",
            "best_for": "When you want relatable, casual support"
        },
        {
            "id": "stoic",
            "name": "The Stoic",
            "description": "Focuses on what can be controlled and acceptance",
            "tone": "Calm and accepting",
            "best_for": "When dealing with things outside your control"
        },
        {
            "id": "spiritual",
            "name": "The Spiritual Guide",
            "description": "Connects to larger meaning and inner wisdom",
            "tone": "Compassionate and transcendent",
            "best_for": "When seeking purpose and growth"
        }
    ]

    return {
        "personas": personas,
        "note": "You can specify preferred_persona in your analysis request"
    }


@router.get("/test-analysis")
async def test_journal_analysis():
    """Test the journal analysis with sample entries."""
    test_entries = [
        {
            "name": "Anxious Entry",
            "content": """
            I couldn't sleep last night because I keep worrying about the presentation
            tomorrow. My mind just won't stop racing. I feel like everything is going
            to go wrong and everyone will think I'm incompetent. I should have prepared
            more. I always do this - leave things until the last minute and then panic.
            """,
            "mood_rating": 2,
            "energy_level": 2
        },
        {
            "name": "Grateful Entry",
            "content": """
            Today was a really good day. I went for a morning walk and felt so grateful
            for the sunshine and fresh air. I've been making progress on my health goals
            and it feels great to see the improvement. My energy levels are better and
            I'm sleeping more soundly. I'm thankful for the support of my family.
            """,
            "mood_rating": 5,
            "energy_level": 4
        },
        {
            "name": "Reflective Entry",
            "content": """
            I've been thinking a lot about my career lately and where I want to be in
            five years. There's this constant tension between stability and growth.
            Part of me wants to take risks and pursue my passions, but another part
            is afraid of failure. I realize I need to better understand what truly
            matters to me before making any big decisions.
            """,
            "mood_rating": 3,
            "energy_level": 3
        },
        {
            "name": "Stressed Entry",
            "content": """
            I'm completely overwhelmed with work right now. The deadlines keep piling up
            and I don't know how I'm going to get everything done. I've been skipping
            lunches and staying late, but it's still not enough. My neck and shoulders
            are so tense from sitting at my desk all day. I feel like I'm drowning.
            """,
            "mood_rating": 1,
            "energy_level": 2,
            "health_score": 45.0,
            "weak_domains": ["physical", "emotional"]
        }
    ]

    results = []
    for test in test_entries:
        entry = JournalEntry(
            user_id=uuid4(),
            content=test["content"].strip(),
            mood_rating=test.get("mood_rating"),
            energy_level=test.get("energy_level"),
            health_score=test.get("health_score"),
            weak_domains=test.get("weak_domains")
        )

        analysis = sirm.analyze(entry)

        results.append({
            "name": test["name"],
            "input_preview": test["content"].strip()[:100] + "...",
            "sentiment": {
                "score": analysis.sentiment.overall_score,
                "tone": analysis.sentiment.emotional_tone.value,
                "distortions": analysis.sentiment.cognitive_distortions
            },
            "themes": analysis.themes.primary_themes,
            "domains": analysis.themes.wellness_domains,
            "primary_persona": analysis.primary_reflection.persona.value,
            "key_insight": analysis.primary_reflection.key_insight,
            "suggestion_count": len(analysis.suggestions)
        })

    return {
        "message": "Test analysis complete",
        "results": results,
        "note": "Use POST /analyze with your own journal entry"
    }


@router.get("/wellness-suggestions")
async def get_wellness_suggestions_info():
    """Get information about the evidence-based wellness suggestions."""
    categories = {
        "stress": "Techniques for managing acute and chronic stress",
        "sleep": "Strategies for improving sleep quality and duration",
        "anxiety": "Methods for reducing anxiety and worry",
        "loneliness": "Approaches for building social connections",
        "gratitude": "Practices to cultivate appreciation and positivity",
        "low_energy": "Quick interventions to boost energy levels",
        "rumination": "Techniques to break cycles of negative thinking"
    }

    return {
        "description": "SIRM provides evidence-based wellness suggestions based on journal analysis",
        "categories": categories,
        "methodology": "Suggestions are mapped to detected themes, emotions, and patterns",
        "evidence": "All suggestions are backed by peer-reviewed research"
    }
