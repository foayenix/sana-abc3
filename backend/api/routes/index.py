"""
Index API Routes

Endpoints for SANA Index scoring.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from uuid import UUID

from algorithms.index import calculate_sana_index

router = APIRouter()


@router.post("/calculate")
async def calculate(
    practitioner_id: UUID,
    credentials: List[str],
    outcome_data: Dict,
    reviews: List[Dict],
    verification_status: bool
):
    """
    Calculate SANA Index score for a practitioner.

    Returns overall score and component breakdown.
    """
    try:
        result = calculate_sana_index(
            practitioner_id=practitioner_id,
            credentials=credentials,
            outcome_data=outcome_data,
            reviews=reviews,
            verification_status=verification_status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/practitioner/{practitioner_id}")
async def get_practitioner_index(practitioner_id: UUID):
    """
    Get current SANA Index for a practitioner.

    Returns cached score and last update time.
    """
    # TODO: Implement with database
    return {
        "practitioner_id": practitioner_id,
        "score": None,
        "last_updated": None
    }


@router.get("/leaderboard")
async def get_leaderboard(specialty: str = None, top_k: int = 10):
    """
    Get top practitioners by SANA Index.

    Returns ranked list of practitioners.
    """
    # TODO: Implement with database
    return {"specialty": specialty, "practitioners": []}
