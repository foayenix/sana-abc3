"""
Pydantic models for safety algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyInput(BaseModel):
    """Input model for safety assessment."""
    user_id: UUID
    health_data: Dict
    recent_responses: List[Dict] = []


class SafetyOutput(BaseModel):
    """Output model for safety assessment."""
    user_id: UUID
    risk_level: RiskLevel
    risk_score: float
    flags: List[str]
    recommendations: List[str]
    requires_immediate_action: bool
    escalation_contact: Optional[str] = None
