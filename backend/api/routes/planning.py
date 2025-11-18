"""
API routes for SHAM planning endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from uuid import UUID
from datetime import date

from algorithms.planning.sham import SHAMAlgorithm
from algorithms.planning.models import (
    UserConstraints,
    UserGoals,
    SHAMOutput
)
from algorithms.scoring.models import SISMOutput
from algorithms.scoring.sism import SISMAlgorithm
from algorithms.evidence.health_graph import HealthGraph
from utils.health_graph_data import seed_health_graph
from utils.dummy_data import DummyDataGenerator

router = APIRouter()

# Initialize dependencies
health_graph = HealthGraph()
seed_health_graph(health_graph)
sism_algo = SISMAlgorithm()
sham = SHAMAlgorithm(health_graph, sism_algo)

@router.post("/generate", response_model=SHAMOutput)
async def generate_wellness_plan(
    sism_output: SISMOutput,
    constraints: UserConstraints,
    goals: Optional[UserGoals] = None
):
    """
    Generate personalized wellness plan from SISM scores

    **Input**: SISM output + user constraints + optional goals
    **Output**: Complete weekly schedule with activities
    """
    try:
        plan = sham.generate_plan(
            sism_output.user_id,
            sism_output,
            constraints,
            goals
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning error: {str(e)}")

@router.get("/test-full-flow")
async def test_complete_flow(
    profile: str = Query(default="balanced", description="SISM profile: balanced, struggling, thriving, physical_weak, emotional_weak"),
    time_per_day: int = Query(default=60, ge=15, le=180, description="Minutes per day"),
    budget_per_week: float = Query(default=50.0, ge=0, le=500, description="Budget in pounds per week")
):
    """
    Complete end-to-end test: Generate questionnaire -> SISM -> SHAM plan

    **Perfect for demo and testing**
    """
    try:
        # Step 1: Generate questionnaire
        questionnaire = DummyDataGenerator.generate_questionnaire(profile=profile)

        # Step 2: Calculate SISM
        sism_output = sism_algo.calculate(questionnaire)

        # Step 3: Create constraints
        constraints = UserConstraints(
            time_available_minutes_per_day=time_per_day,
            time_available_minutes_per_week=time_per_day * 7,
            budget_pounds_per_week=budget_per_week,
            medical_conditions=[],
            medications=[]
        )

        # Step 4: Generate SHAM plan
        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            constraints
        )

        return {
            "sism_output": sism_output,
            "sham_plan": plan,
            "message": "Complete flow executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flow error: {str(e)}")

@router.post("/generate-with-safety-checks")
async def generate_with_safety(
    sism_output: SISMOutput,
    constraints: UserConstraints,
    goals: Optional[UserGoals] = None
):
    """
    Generate plan with explicit safety checking and warnings

    Returns plan + detailed safety analysis
    """
    try:
        plan = sham.generate_plan(
            sism_output.user_id,
            sism_output,
            constraints,
            goals
        )

        # Additional safety analysis
        safety_warnings = []
        if not plan.fits_time_budget:
            safety_warnings.append("Plan exceeds time budget - consider reducing activities")
        if not plan.fits_cost_budget:
            safety_warnings.append("Plan exceeds cost budget - consider free alternatives")

        return {
            "plan": plan,
            "safety_warnings": safety_warnings,
            "constraints_met": plan.fits_time_budget and plan.fits_cost_budget
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning error: {str(e)}")

@router.get("/constraints-info")
async def get_constraints_info():
    """Get information about available constraint parameters"""
    return {
        "time_per_day": {
            "min": 15,
            "max": 180,
            "default": 60,
            "unit": "minutes"
        },
        "budget_per_week": {
            "min": 0,
            "max": 500,
            "default": 50,
            "unit": "pounds"
        },
        "profiles": ["balanced", "struggling", "thriving", "physical_weak", "emotional_weak"],
        "time_slots": ["morning", "midday", "afternoon", "evening", "night"],
        "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    }


# Legacy endpoints for backwards compatibility
from algorithms.planning import generate_habit_plan, generate_timetable, optimize_allocation

@router.post("/habits")
async def create_habit_plan(
    user_id: UUID,
    health_goals: List[str],
    available_time_minutes: int,
    preferences: Dict
):
    """Legacy: Generate a personalized habit and activity plan."""
    try:
        result = generate_habit_plan(
            user_id=user_id,
            health_goals=health_goals,
            available_time_minutes=available_time_minutes,
            preferences=preferences
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/timetable")
async def create_timetable(
    user_id: UUID,
    target_date: date,
    activities: List[Dict],
    constraints: Dict
):
    """Legacy: Generate an optimized daily timetable."""
    try:
        result = generate_timetable(
            user_id=user_id,
            target_date=target_date,
            activities=activities,
            constraints=constraints
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize(
    user_id: UUID,
    interventions: List[Dict],
    budget: float,
    time_available_minutes: int,
    priorities: Dict[str, float]
):
    """Legacy: Optimize intervention allocation."""
    try:
        result = optimize_allocation(
            user_id=user_id,
            interventions=interventions,
            budget=budget,
            time_available_minutes=time_available_minutes,
            priorities=priorities
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
