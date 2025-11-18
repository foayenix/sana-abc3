"""
API routes for SST safety & triage
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random

from algorithms.safety.sst import SSTAlgorithm, assess_safety
from algorithms.safety.models import (
    SSTInput,
    SSTOutput,
    HistoricalScore,
    SafetyOutput
)
from algorithms.scoring.sism import SISMAlgorithm
from utils.dummy_data import DummyDataGenerator

router = APIRouter()

# Initialize SST
sst = SSTAlgorithm()
sism_algo = SISMAlgorithm()


@router.post("/analyze", response_model=SSTOutput)
async def analyze_safety(sst_input: SSTInput):
    """
    Analyze user safety and determine risk level

    **Input**: Current and historical health data
    **Output**: Safety status, risk score, and recommended actions
    """
    try:
        result = sst.analyze_safety(sst_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety analysis error: {str(e)}")


@router.get("/test-scenarios")
async def test_safety_scenarios(
    scenario: str = Query(
        default="safe",
        description="Test scenario: safe, declining, chronic_low, crisis_keywords, urgent"
    )
):
    """
    Test SST with different safety scenarios

    **Scenarios**:
    - safe: Healthy user, no concerns
    - declining: Rapid score deterioration
    - chronic_low: Chronically low scores
    - crisis_keywords: Contains crisis language
    - urgent: Multiple critical indicators
    """
    try:
        # Generate base questionnaire
        if scenario == "safe":
            questionnaire = DummyDataGenerator.generate_questionnaire(profile="thriving")
        elif scenario == "declining":
            questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        elif scenario == "chronic_low":
            questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        elif scenario == "crisis_keywords":
            questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        elif scenario == "urgent":
            questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        else:
            raise HTTPException(status_code=400, detail="Invalid scenario")

        # Calculate SISM
        sism_output = sism_algo.calculate(questionnaire)

        # Create SST input
        sst_input = SSTInput(
            user_id=questionnaire.user_id,
            current_sism_score=sism_output.overall_score,
            current_domain_scores={
                name: score.normalized_score
                for name, score in sism_output.domain_scores.items()
            },
            current_sism_id=sism_output.id,
            historical_scores=[]
        )

        # Modify based on scenario
        if scenario == "declining":
            # Add historical data showing decline
            two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
            sst_input.historical_scores = [
                HistoricalScore(
                    score_id=uuid4(),
                    user_id=questionnaire.user_id,
                    overall_score=sism_output.overall_score + 25,  # Was much higher
                    domain_scores={
                        name: score.normalized_score + 25
                        for name, score in sism_output.domain_scores.items()
                    },
                    recorded_at=two_weeks_ago
                )
            ]

        elif scenario == "chronic_low":
            # Add historical data showing chronic low
            for weeks_ago in [4, 3, 2, 1]:
                date = datetime.utcnow() - timedelta(weeks=weeks_ago)
                sst_input.historical_scores.append(
                    HistoricalScore(
                        score_id=uuid4(),
                        user_id=questionnaire.user_id,
                        overall_score=sism_output.overall_score + random.uniform(-5, 5),
                        domain_scores={
                            name: score.normalized_score
                            for name, score in sism_output.domain_scores.items()
                        },
                        recorded_at=date
                    )
                )

        elif scenario == "crisis_keywords":
            # Add crisis text
            sst_input.recent_journal_entries = [
                "I can't go on like this anymore",
                "Feeling hopeless, no point to anything"
            ]

        elif scenario == "urgent":
            # Multiple critical indicators
            # Override SISM score to be critical
            sst_input.current_sism_score = 25
            sst_input.current_domain_scores = {
                "physical": 30,
                "emotional": 15,
                "social": 20,
                "cognitive": 25,
                "spiritual": 30
            }
            sst_input.recent_journal_entries = [
                "I want to hurt myself",
                "Can't see any way out"
            ]
            sst_input.days_since_last_activity = 21
            sst_input.missed_practitioner_appointments = 3

        # Analyze safety
        result = sst.analyze_safety(sst_input)

        return {
            "scenario": scenario,
            "sism_output": sism_output,
            "safety_analysis": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test scenario error: {str(e)}")


@router.get("/resources")
async def get_safety_resources():
    """Get list of safety resources"""
    return {
        "resources": [
            {
                "name": r.name,
                "description": r.description,
                "contact_method": r.contact_method,
                "contact_details": r.contact_details,
                "availability": r.availability,
                "appropriate_for": [c.value for c in r.appropriate_for]
            }
            for r in sst.SAFETY_RESOURCES
        ]
    }


@router.get("/crisis-keywords")
async def get_crisis_keywords():
    """Get list of monitored crisis keywords (for admin reference)"""
    return {
        "keywords": [
            {
                "keyword": k.keyword,
                "category": k.category.value,
                "severity": k.severity
            }
            for k in sst.CRISIS_KEYWORDS
        ],
        "warning": "This information is for administrative purposes only"
    }


@router.get("/thresholds")
async def get_safety_thresholds():
    """Get SST risk thresholds"""
    return {
        "risk_thresholds": {
            "safe": f"0-{sst.SAFE_THRESHOLD}",
            "monitor": f"{sst.SAFE_THRESHOLD}-{sst.MONITOR_THRESHOLD}",
            "escalate": f"{sst.MONITOR_THRESHOLD}-{sst.ESCALATE_THRESHOLD}",
            "urgent": f"{sst.ESCALATE_THRESHOLD}-100"
        },
        "score_thresholds": {
            "critical_score": sst.CRITICAL_SCORE,
            "low_score": sst.LOW_SCORE
        },
        "trend_thresholds": {
            "rapid_decline_points": sst.RAPID_DECLINE,
            "chronic_low_weeks": sst.CHRONIC_LOW_WEEKS
        }
    }


# Legacy endpoints for backwards compatibility
@router.post("/assess")
async def assess(
    user_id: UUID,
    health_data: Dict,
    recent_responses: List[Dict] = None
):
    """
    Legacy: Assess safety risk for a user.

    Returns risk level and recommendations.
    Use /analyze for comprehensive analysis.
    """
    try:
        result = assess_safety(
            user_id=user_id,
            health_data=health_data,
            recent_responses=recent_responses
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/alerts")
async def get_user_alerts(user_id: UUID):
    """
    Get active safety alerts for a user.

    Returns any current safety concerns or flags.
    """
    # In production, this would query the database
    return {"user_id": user_id, "alerts": []}
