"""
Planning API Routes

Endpoints for treatment planning and scheduling.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from uuid import UUID
from datetime import date

from algorithms.planning import generate_habit_plan, generate_timetable, optimize_allocation

router = APIRouter()


@router.post("/habits")
async def create_habit_plan(
    user_id: UUID,
    health_goals: List[str],
    available_time_minutes: int,
    preferences: Dict
):
    """
    Generate a personalized habit and activity plan.

    Returns daily activities optimized for health goals.
    """
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
    """
    Generate an optimized daily timetable.

    Returns scheduled activities for the target date.
    """
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
    """
    Optimize intervention allocation.

    Returns optimal allocation considering constraints.
    """
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
