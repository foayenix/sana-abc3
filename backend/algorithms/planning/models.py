"""
Data models for SHAM (Habit & Activity Model) and planning algorithms
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime, time
from uuid import UUID, uuid4
from enum import Enum

class TimeOfDay(str, Enum):
    """Time slots for scheduling"""
    MORNING = "morning"      # 6am-10am
    MIDDAY = "midday"        # 10am-2pm
    AFTERNOON = "afternoon"  # 2pm-6pm
    EVENING = "evening"      # 6pm-10pm
    NIGHT = "night"          # 10pm-12am

class DayOfWeek(str, Enum):
    """Days of the week"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class UserConstraints(BaseModel):
    """User's real-world constraints"""
    time_available_minutes_per_day: int = Field(..., ge=0, le=1440)
    time_available_minutes_per_week: int = Field(..., ge=0, le=10080)
    budget_pounds_per_week: float = Field(..., ge=0)

    # Availability by time of day
    available_morning: bool = True
    available_midday: bool = True
    available_afternoon: bool = True
    available_evening: bool = True
    available_night: bool = False

    # Days available
    available_days: List[DayOfWeek] = Field(
        default=[DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY,
                 DayOfWeek.THURSDAY, DayOfWeek.FRIDAY, DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]
    )

    # Constraints
    medical_conditions: List[str] = []
    medications: List[str] = []

    # Preferences
    preferred_categories: List[str] = []  # e.g., "movement", "mind_body"
    disliked_categories: List[str] = []

class UserGoals(BaseModel):
    """User's wellness goals"""
    primary_goal: str  # "reduce_anxiety", "improve_sleep", "increase_energy"
    target_domains: List[str] = []  # Domains user wants to focus on
    timeline_weeks: int = Field(default=12, ge=1, le=52)

class ScheduledActivity(BaseModel):
    """A scheduled intervention in the timetable"""
    id: UUID = Field(default_factory=uuid4)
    intervention_id: UUID
    intervention_name: str
    category: str

    # Scheduling
    day_of_week: Optional[DayOfWeek] = None
    time_of_day: TimeOfDay
    start_time: Optional[time] = None
    duration_minutes: int

    # Details
    instructions: str
    dosage_info: Optional[str] = None

    # Metadata
    target_domains: List[str]
    evidence_strength: str
    expected_benefit_score: float  # 0-100
    cost_pounds: float = 0.0

class DailySchedule(BaseModel):
    """Activities scheduled for one day"""
    day: DayOfWeek
    activities: List[ScheduledActivity]
    total_time_minutes: int
    total_cost_pounds: float

    def get_activities_by_time_slot(self) -> Dict[TimeOfDay, List[ScheduledActivity]]:
        """Group activities by time of day"""
        grouped = {slot: [] for slot in TimeOfDay}
        for activity in self.activities:
            grouped[activity.time_of_day].append(activity)
        return grouped

class WeeklySchedule(BaseModel):
    """Complete weekly plan"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    week_start_date: datetime

    daily_schedules: Dict[DayOfWeek, DailySchedule]

    # Summary
    total_activities: int
    total_time_minutes_per_week: int
    total_cost_pounds_per_week: float

    # Target tracking
    domains_addressed: Dict[str, int]  # domain -> number of activities
    evidence_distribution: Dict[str, int]  # strength -> count

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sism_score_at_creation: Optional[float] = None
    weak_domains_at_creation: List[str] = []

class InterventionScore(BaseModel):
    """Scored intervention for optimization"""
    intervention_id: UUID
    intervention_name: str

    # Scoring components
    evidence_score: float  # 0-100 based on strength
    domain_gap_score: float  # How much this helps weak domains
    time_efficiency_score: float  # Benefit per minute
    cost_efficiency_score: float  # Benefit per pound

    # Combined score
    total_score: float

    # Practical info
    duration_minutes: int
    cost_pounds: float
    target_domains: List[str]

    def calculate_total_score(
        self,
        evidence_weight: float = 0.3,
        gap_weight: float = 0.4,
        time_weight: float = 0.2,
        cost_weight: float = 0.1
    ) -> float:
        """Calculate weighted total score"""
        return (
            evidence_weight * self.evidence_score +
            gap_weight * self.domain_gap_score +
            time_weight * self.time_efficiency_score +
            cost_weight * self.cost_efficiency_score
        )

class SHAMOutput(BaseModel):
    """Complete output from SHAM algorithm"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    weekly_schedule: WeeklySchedule

    # Recommendations
    priority_interventions: List[str]  # Top 3-5 interventions
    quick_wins: List[str]  # Low-effort, high-impact activities

    # Insights
    expected_improvements: Dict[str, str]  # domain -> expected outcome
    timeline_expectations: Dict[str, int]  # intervention -> weeks to results

    # Constraints check
    fits_time_budget: bool
    fits_cost_budget: bool
    constraints_used: UserConstraints

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sism_input_id: Optional[UUID] = None
    algorithm_version: str = "1.0"


# Legacy models for backwards compatibility
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


# Timetable models
class ScheduleSlot(BaseModel):
    """A single time slot in a timetable."""
    start_time: time
    end_time: time
    duration_minutes: int
    activity: Optional[ScheduledActivity] = None
    is_available: bool = True


class TimetableInput(BaseModel):
    """Input for timetable generation."""
    user_id: UUID
    date: datetime
    constraints: UserConstraints
    goals: UserGoals
    existing_activities: List[ScheduledActivity] = []


class TimetableOutput(BaseModel):
    """Output from timetable generation."""
    user_id: UUID
    date: datetime
    schedule_slots: List[ScheduleSlot]
    daily_schedule: DailySchedule
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Optimizer models
class AllocationResult(BaseModel):
    """Result of resource allocation optimization."""
    activity_id: UUID
    activity_name: str
    allocated_time_minutes: int
    allocated_budget: float
    expected_benefit: float
    priority_score: float


class OptimizationInput(BaseModel):
    """Input for optimization algorithm."""
    user_id: UUID
    constraints: UserConstraints
    goals: UserGoals
    available_interventions: List[Dict] = []


class OptimizationOutput(BaseModel):
    """Output from optimization algorithm."""
    user_id: UUID
    allocations: List[AllocationResult]
    total_time_used: int
    total_budget_used: float
    expected_total_benefit: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)
