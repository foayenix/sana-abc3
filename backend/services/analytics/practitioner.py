"""
Practitioner analytics service.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class RevenueMetrics(BaseModel):
    """Revenue analytics."""
    total_revenue: float = 0.0
    net_revenue: float = 0.0
    average_session_value: float = 0.0
    revenue_by_service: Dict[str, float] = {}
    revenue_trend: List[Dict[str, Any]] = []
    growth_rate: float = 0.0


class ClientMetrics(BaseModel):
    """Client analytics."""
    total_clients: int = 0
    active_clients: int = 0
    new_clients: int = 0
    retention_rate: float = 0.0
    churn_rate: float = 0.0
    average_client_value: float = 0.0
    client_acquisition: List[Dict[str, Any]] = []


class SessionMetrics(BaseModel):
    """Session analytics."""
    total_sessions: int = 0
    completed_sessions: int = 0
    cancelled_sessions: int = 0
    no_shows: int = 0
    average_duration: float = 0.0
    sessions_by_type: Dict[str, int] = {}
    sessions_trend: List[Dict[str, Any]] = []
    utilization_rate: float = 0.0


class OutcomeMetrics(BaseModel):
    """Outcome analytics."""
    average_improvement: float = 0.0
    clients_improved: int = 0
    improvement_rate: float = 0.0
    outcome_by_condition: Dict[str, float] = {}
    sana_index: float = 0.0
    sana_index_trend: List[Dict[str, Any]] = []


class PractitionerAnalytics:
    """
    Analytics dashboard for practitioners.

    Provides insights on:
    - Revenue and financial performance
    - Client metrics and retention
    - Session utilization
    - Treatment outcomes
    """

    def __init__(self):
        # In production, would connect to database
        self._mock_data: Dict[UUID, Dict] = {}
        logger.info("PractitionerAnalytics initialized")

    def get_dashboard(
        self,
        practitioner_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get complete analytics dashboard.

        Args:
            practitioner_id: Practitioner UUID
            start_date: Start of period
            end_date: End of period

        Returns:
            Complete dashboard data
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        return {
            "practitioner_id": str(practitioner_id),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "revenue": self.get_revenue_metrics(practitioner_id, start_date, end_date).dict(),
            "clients": self.get_client_metrics(practitioner_id, start_date, end_date).dict(),
            "sessions": self.get_session_metrics(practitioner_id, start_date, end_date).dict(),
            "outcomes": self.get_outcome_metrics(practitioner_id, start_date, end_date).dict(),
            "insights": self._generate_insights(practitioner_id)
        }

    def get_revenue_metrics(
        self,
        practitioner_id: UUID,
        start_date: date,
        end_date: date
    ) -> RevenueMetrics:
        """Get revenue analytics."""
        # Generate sample data
        days = (end_date - start_date).days
        daily_revenue = 150.0  # Average daily revenue

        total = daily_revenue * days
        net = total * 0.85  # After fees

        # Revenue trend
        trend = []
        current = start_date
        while current <= end_date:
            trend.append({
                "date": current.isoformat(),
                "revenue": daily_revenue * (0.8 + 0.4 * (current.weekday() < 5))
            })
            current += timedelta(days=1)

        return RevenueMetrics(
            total_revenue=total,
            net_revenue=net,
            average_session_value=85.0,
            revenue_by_service={
                "Initial Consultation": total * 0.3,
                "Follow-up": total * 0.5,
                "Treatment Package": total * 0.2
            },
            revenue_trend=trend,
            growth_rate=0.12
        )

    def get_client_metrics(
        self,
        practitioner_id: UUID,
        start_date: date,
        end_date: date
    ) -> ClientMetrics:
        """Get client analytics."""
        return ClientMetrics(
            total_clients=45,
            active_clients=32,
            new_clients=8,
            retention_rate=0.85,
            churn_rate=0.05,
            average_client_value=450.0,
            client_acquisition=[
                {"source": "Marketplace", "count": 4},
                {"source": "Referral", "count": 3},
                {"source": "Direct", "count": 1}
            ]
        )

    def get_session_metrics(
        self,
        practitioner_id: UUID,
        start_date: date,
        end_date: date
    ) -> SessionMetrics:
        """Get session analytics."""
        days = (end_date - start_date).days
        sessions_per_day = 4

        total = sessions_per_day * days
        completed = int(total * 0.92)
        cancelled = int(total * 0.05)
        no_shows = total - completed - cancelled

        # Sessions trend
        trend = []
        current = start_date
        while current <= end_date:
            trend.append({
                "date": current.isoformat(),
                "sessions": sessions_per_day if current.weekday() < 5 else 1
            })
            current += timedelta(days=1)

        return SessionMetrics(
            total_sessions=total,
            completed_sessions=completed,
            cancelled_sessions=cancelled,
            no_shows=no_shows,
            average_duration=55.0,
            sessions_by_type={
                "Initial Consultation": int(total * 0.2),
                "Follow-up": int(total * 0.7),
                "Review": int(total * 0.1)
            },
            sessions_trend=trend,
            utilization_rate=0.75
        )

    def get_outcome_metrics(
        self,
        practitioner_id: UUID,
        start_date: date,
        end_date: date
    ) -> OutcomeMetrics:
        """Get outcome analytics."""
        return OutcomeMetrics(
            average_improvement=28.5,
            clients_improved=28,
            improvement_rate=0.78,
            outcome_by_condition={
                "Chronic Pain": 32.0,
                "Anxiety": 25.0,
                "Insomnia": 35.0,
                "Fatigue": 22.0
            },
            sana_index=82.5,
            sana_index_trend=[
                {"month": "Aug", "score": 78.0},
                {"month": "Sep", "score": 80.0},
                {"month": "Oct", "score": 81.5},
                {"month": "Nov", "score": 82.5}
            ]
        )

    def _generate_insights(self, practitioner_id: UUID) -> List[Dict[str, Any]]:
        """Generate actionable insights."""
        return [
            {
                "type": "success",
                "title": "Strong Client Retention",
                "message": "Your 85% retention rate is above the platform average of 72%.",
                "action": None
            },
            {
                "type": "opportunity",
                "title": "Booking Gap Detected",
                "message": "Tuesdays have 40% lower bookings than other weekdays.",
                "action": "Consider promoting Tuesday availability"
            },
            {
                "type": "milestone",
                "title": "SANA Index Milestone",
                "message": "Your SANA Index increased 5.8% this quarter.",
                "action": None
            }
        ]

    def get_comparison(
        self,
        practitioner_id: UUID,
        metric: str = "revenue"
    ) -> Dict[str, Any]:
        """Get comparison with platform benchmarks."""
        benchmarks = {
            "revenue": {"you": 4500, "average": 3800, "top_10": 7200},
            "clients": {"you": 32, "average": 25, "top_10": 55},
            "retention": {"you": 0.85, "average": 0.72, "top_10": 0.92},
            "outcomes": {"you": 28.5, "average": 22.0, "top_10": 38.0}
        }

        if metric not in benchmarks:
            metric = "revenue"

        data = benchmarks[metric]
        percentile = 75 if data["you"] > data["average"] else 50

        return {
            "metric": metric,
            "your_value": data["you"],
            "platform_average": data["average"],
            "top_10_percent": data["top_10"],
            "percentile": percentile
        }

    def export_report(
        self,
        practitioner_id: UUID,
        start_date: date,
        end_date: date,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export analytics report."""
        dashboard = self.get_dashboard(practitioner_id, start_date, end_date)

        return {
            "report_id": f"report_{practitioner_id}_{datetime.utcnow().timestamp()}",
            "generated_at": datetime.utcnow().isoformat(),
            "format": format,
            "data": dashboard
        }
