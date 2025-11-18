"""
Evidence API Routes

Endpoints for evidence-based recommendations.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from uuid import UUID

from algorithms.evidence import recommend_interventions
from algorithms.evidence.health_graph import health_graph

router = APIRouter()


@router.post("/recommend")
async def recommend(
    user_id: UUID,
    health_goals: List[str],
    domain_scores: Dict[str, float],
    contraindications: List[str] = None,
    top_k: int = 5
):
    """
    Get evidence-based intervention recommendations.

    Returns ranked interventions with evidence ratings.
    """
    try:
        result = recommend_interventions(
            user_id=user_id,
            health_goals=health_goals,
            domain_scores=domain_scores,
            contraindications=contraindications,
            top_k=top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intervention/{intervention_id}")
async def get_intervention_evidence(intervention_id: str):
    """
    Get evidence summary for an intervention.

    Returns research citations and evidence ratings.
    """
    try:
        evidence = health_graph.get_evidence_for_intervention(intervention_id)
        return {"intervention_id": intervention_id, "evidence": evidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/condition/{condition}")
async def get_interventions_for_condition(condition: str):
    """
    Get interventions for a specific condition.

    Returns interventions that address the condition.
    """
    try:
        interventions = health_graph.get_interventions_for_condition(condition)
        return {"condition": condition, "interventions": interventions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
