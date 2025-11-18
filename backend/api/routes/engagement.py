"""
Engagement API Routes

Endpoints for engagement prediction and follow-up coaching.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from uuid import UUID

from algorithms.engagement import predict_engagement, generate_followup, predict_outcome_uplift

router = APIRouter()


@router.post("/predict")
async def predict(user_id: UUID, activity_history: Dict):
    """
    Predict user engagement and churn risk.

    Returns engagement score and retention recommendations.
    """
    try:
        result = predict_engagement(
            user_id=user_id,
            activity_history=activity_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/followup")
async def get_followup(user_id: UUID, current_plan: Dict, progress_data: Dict):
    """
    Generate follow-up recommendations.

    Returns next actions and reminders based on progress.
    """
    try:
        result = generate_followup(
            user_id=user_id,
            current_plan=current_plan,
            progress_data=progress_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outcome-uplift")
async def get_outcome_uplift(
    user_id: UUID,
    intervention_id: UUID,
    baseline_scores: Dict[str, float]
):
    """
    Predict outcome uplift for an intervention.

    Returns expected health improvements.
    """
    try:
        result = predict_outcome_uplift(
            user_id=user_id,
            intervention_id=intervention_id,
            baseline_scores=baseline_scores
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
