"""
Matching API Routes

Endpoints for practitioner matching and recommendations.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from uuid import UUID

from algorithms.matching import recommend_practitioners, calculate_match_score
from algorithms.matching.models import PractitionerMatchOutput, MatchingOutput

router = APIRouter()


@router.post("/recommend")
async def recommend(
    user_id: UUID,
    health_goals: List[str],
    preferences: Dict,
    top_k: int = 5
):
    """
    Get practitioner recommendations for a user.

    Returns ranked practitioners based on user needs and preferences.
    """
    try:
        recommendations = recommend_practitioners(
            user_id=user_id,
            health_goals=health_goals,
            preferences=preferences,
            top_k=top_k
        )
        return {"user_id": user_id, "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score")
async def get_match_score(
    user_id: UUID,
    practitioner_id: UUID,
    user_profile: Dict,
    practitioner_profile: Dict
):
    """
    Calculate match score between user and practitioner.

    Returns detailed compatibility analysis.
    """
    try:
        result = calculate_match_score(
            user_id=user_id,
            practitioner_id=practitioner_id,
            user_profile=user_profile,
            practitioner_profile=practitioner_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
