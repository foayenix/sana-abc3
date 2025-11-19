"""
Client analytics service.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class HealthProgress(BaseModel):
    """Health progress metrics."""
    sana_score: float = 0.0
    sana_status: str = "balanced"
    score_change: float = 0.0
    score_trend: List[Dict[str, Any]] = []
    top_improvements: List[Dict[str, Any]] = []


class EngagementMetrics(BaseModel):
    """Engagement metrics."""
    sessions_completed: int = 0
    journal_entries: int = 0
    proms_completed: int = 0
    streak_days: int = 0
    engagement_score: float = 0.0


class WellnessMetrics(BaseModel):
    """Wellness tracking metrics."""
    sleep_quality: float = 0.0
    stress_level: float = 0.0
    energy_level: float = 0.0
    mood_average: float = 0.0
    trends: Dict[str, List[Dict[str, Any]]] = {}


class ClientAnalytics:
    """
    Analytics dashboard for clients.

    Provides insights on:
    - Health progress over time
    - Treatment effectiveness
    - Wellness tracking
    - Engagement metrics
    """

    def __init__(self):
        logger.info("ClientAnalytics initialized")

    def get_dashboard(
        self,
        client_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get complete client dashboard."""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        return {
            "client_id": str(client_id),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "health_progress": self.get_health_progress(client_id, start_date, end_date).dict(),
            "engagement": self.get_engagement_metrics(client_id, start_date, end_date).dict(),
            "wellness": self.get_wellness_metrics(client_id, start_date, end_date).dict(),
            "achievements": self._get_achievements(client_id),
            "recommendations": self._get_recommendations(client_id)
        }

    def get_health_progress(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date
    ) -> HealthProgress:
        """Get health progress metrics."""
        # Generate trend data
        trend = []
        current = start_date
        base_score = 55.0
        while current <= end_date:
            days_elapsed = (current - start_date).days
            score = base_score + (days_elapsed * 0.3)
            trend.append({
                "date": current.isoformat(),
                "score": min(score, 100)
            })
            current += timedelta(days=7)  # Weekly data points

        current_score = trend[-1]["score"] if trend else base_score

        return HealthProgress(
            sana_score=current_score,
            sana_status="balanced" if current_score < 61 else "thriving",
            score_change=current_score - base_score,
            score_trend=trend,
            top_improvements=[
                {"area": "Sleep Quality", "improvement": 35, "unit": "%"},
                {"area": "Stress Management", "improvement": 28, "unit": "%"},
                {"area": "Energy Levels", "improvement": 22, "unit": "%"}
            ]
        )

    def get_engagement_metrics(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date
    ) -> EngagementMetrics:
        """Get engagement metrics."""
        days = (end_date - start_date).days

        return EngagementMetrics(
            sessions_completed=4,
            journal_entries=days // 3,  # Every 3 days
            proms_completed=2,
            streak_days=7,
            engagement_score=72.0
        )

    def get_wellness_metrics(
        self,
        client_id: UUID,
        start_date: date,
        end_date: date
    ) -> WellnessMetrics:
        """Get wellness tracking metrics."""
        # Generate trend data for each metric
        trends = {}
        for metric in ["sleep", "stress", "energy", "mood"]:
            trend = []
            current = start_date
            while current <= end_date:
                trend.append({
                    "date": current.isoformat(),
                    "value": 50 + (current.day % 30)  # Sample variation
                })
                current += timedelta(days=1)
            trends[metric] = trend

        return WellnessMetrics(
            sleep_quality=72.0,
            stress_level=35.0,
            energy_level=68.0,
            mood_average=75.0,
            trends=trends
        )

    def _get_achievements(self, client_id: UUID) -> List[Dict[str, Any]]:
        """Get client achievements."""
        return [
            {
                "id": "streak_7",
                "title": "7-Day Streak",
                "description": "Logged wellness data for 7 consecutive days",
                "earned_at": datetime.utcnow().isoformat(),
                "icon": "fire"
            },
            {
                "id": "first_prom",
                "title": "First Check-in",
                "description": "Completed your first outcome measure",
                "earned_at": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                "icon": "clipboard"
            },
            {
                "id": "improvement_20",
                "title": "Rising Star",
                "description": "Improved SANA Score by 20%",
                "earned_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "icon": "star"
            }
        ]

    def _get_recommendations(self, client_id: UUID) -> List[Dict[str, Any]]:
        """Get personalized recommendations."""
        return [
            {
                "type": "action",
                "title": "Schedule Follow-up",
                "message": "It's been 3 weeks since your last session",
                "priority": "high"
            },
            {
                "type": "insight",
                "title": "Sleep Pattern",
                "message": "Your sleep quality improves on days you journal",
                "priority": "medium"
            },
            {
                "type": "suggestion",
                "title": "Try Meditation",
                "message": "Based on your stress levels, guided meditation may help",
                "priority": "low"
            }
        ]

    def get_treatment_summary(self, client_id: UUID) -> Dict[str, Any]:
        """Get summary of treatments and their effectiveness."""
        return {
            "total_sessions": 12,
            "practitioners_seen": 2,
            "treatments": [
                {
                    "type": "Acupuncture",
                    "sessions": 8,
                    "effectiveness": 78,
                    "primary_condition": "Chronic Pain"
                },
                {
                    "type": "Herbal Medicine",
                    "sessions": 4,
                    "effectiveness": 65,
                    "primary_condition": "Sleep Issues"
                }
            ],
            "conditions_addressed": [
                {"name": "Chronic Pain", "improvement": 35},
                {"name": "Sleep Issues", "improvement": 28},
                {"name": "Stress", "improvement": 22}
            ]
        }
