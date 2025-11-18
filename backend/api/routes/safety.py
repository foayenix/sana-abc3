"""
Safety API Routes

Endpoints for safety monitoring and triage.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from uuid import UUID

from algorithms.safety import assess_safety
from algorithms.safety.models import SafetyOutput

router = APIRouter()


@router.post("/assess")
async def assess(
    user_id: UUID,
    health_data: Dict,
    recent_responses: List[Dict] = None
):
    """
    Assess safety risk for a user.

    Returns risk level and recommendations.
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
    # TODO: Implement with database
    return {"user_id": user_id, "alerts": []}
