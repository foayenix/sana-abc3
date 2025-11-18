"""
API routes for SPRM practitioner matching
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from uuid import UUID

from algorithms.matching.sprm import SPRMAlgorithm, recommend_practitioners
from algorithms.matching.models import (
    UserMatchingPreferences,
    SPRMOutput,
    TreatmentPhilosophy,
    PractitionerMatchOutput
)
from algorithms.scoring.sism import SISMAlgorithm
from utils.practitioner_data import generate_sample_practitioners
from utils.dummy_data import DummyDataGenerator

router = APIRouter()

# Initialize algorithms
sprm = SPRMAlgorithm()
sism_algo = SISMAlgorithm()

# Load sample practitioners
sample_practitioners = generate_sample_practitioners()


@router.get("/test-matching")
async def test_matching(
    profile: str = Query(default="struggling", description="User health profile"),
    max_budget: float = Query(default=80.0, description="Max budget per session"),
    max_distance: float = Query(default=10.0, description="Max travel distance (km)")
):
    """
    Complete test: Generate user -> SISM -> Match practitioners

    **Perfect for demo and testing**
    """
    try:
        # Step 1: Generate questionnaire
        questionnaire = DummyDataGenerator.generate_questionnaire(profile=profile)

        # Step 2: Calculate SISM
        sism_output = sism_algo.calculate(questionnaire)

        # Step 3: Create preferences
        preferences = UserMatchingPreferences(
            user_id=questionnaire.user_id,
            location_latitude=51.5074,
            location_longitude=-0.1278,
            max_travel_distance_km=max_distance,
            willing_to_do_virtual=True,
            max_budget_per_session=max_budget,
            preferred_philosophies=[TreatmentPhilosophy.INTEGRATIVE, TreatmentPhilosophy.EVIDENCE_BASED],
            prioritize_experience=True,
            prioritize_credentials=True
        )

        # Step 4: Find matches
        matches = sprm.find_best_matches(
            questionnaire.user_id,
            sism_output,
            preferences,
            sample_practitioners
        )

        return {
            "sism_output": sism_output,
            "user_preferences": preferences,
            "matches": matches,
            "message": "Complete matching flow executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test flow error: {str(e)}")


@router.get("/practitioners")
async def list_practitioners():
    """List all available practitioners"""
    return {
        "total_practitioners": len(sample_practitioners),
        "practitioners": sample_practitioners
    }


@router.get("/practitioner/{practitioner_id}")
async def get_practitioner(practitioner_id: UUID):
    """Get detailed practitioner profile"""
    practitioner = next(
        (p for p in sample_practitioners if p.practitioner_id == practitioner_id),
        None
    )

    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    return practitioner


@router.get("/specialties")
async def get_available_specialties():
    """Get list of available specialties across practitioners"""
    all_specialties = set()
    for p in sample_practitioners:
        all_specialties.update(p.specialties)

    return {
        "specialties": sorted(list(all_specialties)),
        "total": len(all_specialties)
    }


@router.get("/modalities")
async def get_available_modalities():
    """Get list of available treatment modalities"""
    all_modalities = set()
    for p in sample_practitioners:
        all_modalities.update(p.primary_modalities)

    return {
        "modalities": sorted(list(all_modalities)),
        "total": len(all_modalities)
    }


# Legacy endpoints for backwards compatibility
@router.post("/recommend")
async def recommend(
    user_id: UUID,
    health_goals: List[str],
    preferences: Dict,
    top_k: int = 5
):
    """Legacy: Get practitioner recommendations for a user."""
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
