"""
Pydantic models for planning algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID
from datetime import date, time


class ActivityPlan(BaseModel):
    """Single activity in a plan."""
    activity_id: str
    name: str
    duration_minutes: int
    time_of_day: Optional[str] = None
    frequency: str  # daily, weekly, etc.


class HabitInput(BaseModel):
    """Input model for habit planning."""
    user_id: UUID
    health_goals: List[str]
    available_time_minutes: int
    preferences: Dict


class HabitOutput(BaseModel):
    """Output model for habit planning."""
    user_id: UUID
    daily_plan: List[ActivityPlan]
    weekly_summary: Dict
    adherence_prediction: float


class ScheduleSlot(BaseModel):
    """Time slot in a schedule."""
    start_time: time
    end_time: time
    activity: str
    category: str
    is_flexible: bool = True


class TimetableInput(BaseModel):
    """Input model for timetable generation."""
    user_id: UUID
    date: date
    activities: List[Dict]
    constraints: Dict


class TimetableOutput(BaseModel):
    """Output model for timetable generation."""
    user_id: UUID
    date: date
    slots: List[ScheduleSlot]
    utilization_score: float
    conflicts: List[str]


class AllocationResult(BaseModel):
    """Single allocation in optimization result."""
    intervention_id: UUID
    frequency: str
    cost: float
    time_minutes: int
    expected_impact: Dict[str, float]


class OptimizationInput(BaseModel):
    """Input model for optimization."""
    user_id: UUID
    interventions: List[Dict]
    budget: float
    time_available_minutes: int
    priorities: Dict[str, float]


class OptimizationOutput(BaseModel):
    """Output model for optimization."""
    user_id: UUID
    allocations: List[AllocationResult]
    total_cost: float
    total_time_minutes: int
    expected_outcome_improvement: Dict[str, float]
    optimization_score: float
