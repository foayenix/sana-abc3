"""
API routes for SISM scoring endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from uuid import UUID

from algorithms.scoring.sism import SISMAlgorithm
from algorithms.scoring.models import (
    QuestionnaireInput,
    SISMOutput,
    DomainWeights
)
from utils.dummy_data import DummyDataGenerator

router = APIRouter()

# Initialize SISM with default weights
sism = SISMAlgorithm()


@router.post("/calculate", response_model=SISMOutput)
async def calculate_sism_score(questionnaire: QuestionnaireInput):
    """
    Calculate SISM health score from questionnaire responses

    **Input**: Complete questionnaire with responses across all 5 domains

    **Output**: Overall health score, domain breakdowns, and weak domain identification
    """
    try:
        result = sism.calculate(questionnaire)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/calculate-with-weights", response_model=SISMOutput)
async def calculate_with_custom_weights(
    questionnaire: QuestionnaireInput,
    weights: DomainWeights
):
    """
    Calculate SISM score with custom domain weights

    Useful for testing different weighting strategies or
    creating personalized scoring for specific conditions
    """
    try:
        weights.validate_sum()
        result = sism.recalculate_with_weights(questionnaire, weights)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/generate-dummy", response_model=QuestionnaireInput)
async def generate_dummy_questionnaire(
    profile: str = Query(
        default="balanced",
        description="Response profile: balanced, struggling, thriving, mixed, physical_weak, emotional_weak"
    )
):
    """
    Generate a dummy questionnaire for testing

    **Profiles**:
    - **balanced**: Generally healthy (scores 6-8)
    - **struggling**: Low scores across domains (3-5)
    - **thriving**: High scores everywhere (8-10)
    - **mixed**: Random realistic mix (2-9)
    - **physical_weak**: Strong except physical domain
    - **emotional_weak**: Strong except emotional domain
    """
    valid_profiles = ["balanced", "struggling", "thriving", "mixed", "physical_weak", "emotional_weak"]
    if profile not in valid_profiles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile. Must be one of: {', '.join(valid_profiles)}"
        )

    return DummyDataGenerator.generate_questionnaire(profile=profile)


@router.get("/test-full-flow", response_model=SISMOutput)
async def test_full_flow(
    profile: str = Query(default="balanced")
):
    """
    Complete test: Generate dummy questionnaire and calculate score

    Perfect for quick testing and demonstration
    """
    valid_profiles = ["balanced", "struggling", "thriving", "mixed", "physical_weak", "emotional_weak"]
    if profile not in valid_profiles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile. Must be one of: {', '.join(valid_profiles)}"
        )

    # Generate dummy data
    questionnaire = DummyDataGenerator.generate_questionnaire(profile=profile)

    # Calculate score
    result = sism.calculate(questionnaire)

    return result


@router.get("/domains/weights", response_model=DomainWeights)
async def get_current_weights():
    """Get the current domain weights being used by SISM"""
    return sism.weights


@router.get("/domains/list")
async def get_domain_list():
    """Get list of all domains and their question counts"""
    return {
        "domains": list(DummyDataGenerator.QUESTIONS.keys()),
        "question_counts": {
            domain: len(questions)
            for domain, questions in DummyDataGenerator.QUESTIONS.items()
        },
        "total_questions": sum(
            len(questions) for questions in DummyDataGenerator.QUESTIONS.values()
        )
    }


@router.get("/user/{user_id}/history")
async def get_score_history(user_id: UUID):
    """
    Get scoring history for a user.

    Returns historical health scores for trend analysis.
    """
    # TODO: Implement with database
    return {"user_id": user_id, "scores": []}


def _get_score_interpretation(score: float) -> str:
    """Generate interpretation text for a health score."""
    if score >= 80:
        return "Excellent overall health status"
    elif score >= 60:
        return "Good health status with some areas for improvement"
    elif score >= 40:
        return "Moderate health status - consider targeted interventions"
    else:
        return "Health status needs attention - recommend comprehensive assessment"
