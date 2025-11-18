"""
Scoring API Routes

Endpoints for health scoring algorithms.
"""

from fastapi import APIRouter, HTTPException
from uuid import UUID

from algorithms.scoring import SISMCalculator
from algorithms.scoring.models import ScoreRequest, ScoreResponse, SISMInput

router = APIRouter()


@router.post("/sism", response_model=ScoreResponse)
async def calculate_sism_score(request: ScoreRequest):
    """
    Calculate SISM (Intake Scoring Model) score.

    Processes questionnaire responses to generate a comprehensive
    health assessment across five domains.
    """
    try:
        calculator = SISMCalculator(request.custom_weights)
        input_data = SISMInput(
            user_id=request.user_id,
            domain_responses=request.domain_responses
        )
        result = calculator.calculate(input_data)

        return ScoreResponse(
            user_id=result.user_id,
            overall_score=result.overall_score,
            domain_scores={ds.domain: ds.score for ds in result.domain_scores},
            interpretation=_get_score_interpretation(result.overall_score)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
