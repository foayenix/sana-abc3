"""
Pydantic models for engagement algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime


class EngagementInput(BaseModel):
    """Input model for engagement prediction."""
    user_id: UUID
    activity_history: Dict


class EngagementOutput(BaseModel):
    """Output model for engagement prediction."""
    user_id: UUID
    engagement_score: float
    churn_probability: float
    risk_factors: List[str]
    retention_recommendations: List[str]


class FollowUpInput(BaseModel):
    """Input model for follow-up generation."""
    user_id: UUID
    current_plan: Dict
    progress_data: Dict


class FollowUpOutput(BaseModel):
    """Output model for follow-up generation."""
    user_id: UUID
    next_actions: List[str]
    reminders: List[Dict]
    progress_summary: str
    adjustments: List[str]


class OutcomeInput(BaseModel):
    """Input model for outcome prediction."""
    user_id: UUID
    intervention_id: UUID
    baseline_scores: Dict[str, float]


class OutcomeOutput(BaseModel):
    """Output model for outcome prediction."""
    user_id: UUID
    predicted_uplift: Dict[str, float]
    confidence_intervals: Dict[str, tuple]
    contributing_factors: List[str]
    time_to_effect_days: int
