"""
Wearable data synchronization service.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import random
import logging

logger = logging.getLogger(__name__)

from .integrations import WearableProvider, DataType


class HealthDataPoint(BaseModel):
    """A single health data point."""
    id: UUID
    user_id: UUID
    provider: WearableProvider
    data_type: DataType

    # Value
    value: float
    unit: str

    # Time
    timestamp: datetime
    duration_seconds: Optional[int] = None

    # Metadata
    source_id: Optional[str] = None


class DailySummary(BaseModel):
    """Daily health summary."""
    date: date
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    resting_heart_rate: Optional[float] = None
    hrv_average: Optional[float] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[float] = None
    stress_score: Optional[float] = None


class WearableDataSync:
    """
    Synchronizes and stores wearable health data.

    Features:
    - Multi-provider data normalization
    - Historical data import
    - Real-time sync
    - Aggregations and summaries
    """

    def __init__(self):
        self.data_points: Dict[UUID, HealthDataPoint] = {}
        self.daily_summaries: Dict[str, DailySummary] = {}  # "user_date" key
        logger.info("WearableDataSync initialized")

    def sync_data(
        self,
        user_id: UUID,
        provider: WearableProvider,
        access_token: str,
        data_types: List[DataType],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Sync data from a wearable provider.

        In production, this would call the provider's API.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=7)
        if not end_date:
            end_date = date.today()

        # Simulate fetching and storing data
        points_synced = 0
        days_synced = 0

        current = start_date
        while current <= end_date:
            for dt in data_types:
                point = self._generate_data_point(user_id, provider, dt, current)
                self.data_points[point.id] = point
                points_synced += 1

            # Update daily summary
            self._update_daily_summary(user_id, current)
            days_synced += 1
            current += timedelta(days=1)

        logger.info(
            f"Synced {points_synced} data points from {provider.value} for user {user_id}"
        )

        return {
            "provider": provider.value,
            "data_types": [dt.value for dt in data_types],
            "points_synced": points_synced,
            "days_synced": days_synced,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    def _generate_data_point(
        self,
        user_id: UUID,
        provider: WearableProvider,
        data_type: DataType,
        data_date: date
    ) -> HealthDataPoint:
        """Generate a sample data point."""
        # Sample values and units based on data type
        values = {
            DataType.STEPS: (random.randint(5000, 12000), "steps"),
            DataType.HEART_RATE: (random.randint(60, 80), "bpm"),
            DataType.HRV: (random.randint(30, 70), "ms"),
            DataType.SLEEP: (random.uniform(6, 8), "hours"),
            DataType.ACTIVITY: (random.randint(30, 90), "minutes"),
            DataType.CALORIES: (random.randint(1800, 2500), "kcal"),
            DataType.STRESS: (random.randint(20, 60), "score"),
            DataType.SPO2: (random.uniform(95, 99), "%"),
            DataType.RESPIRATORY_RATE: (random.randint(12, 18), "breaths/min"),
            DataType.BODY_TEMPERATURE: (random.uniform(36.0, 37.0), "°C")
        }

        value, unit = values.get(data_type, (0, "unknown"))

        return HealthDataPoint(
            id=uuid4(),
            user_id=user_id,
            provider=provider,
            data_type=data_type,
            value=value,
            unit=unit,
            timestamp=datetime.combine(data_date, datetime.min.time())
        )

    def _update_daily_summary(self, user_id: UUID, summary_date: date) -> None:
        """Update daily summary with latest data."""
        key = f"{user_id}_{summary_date.isoformat()}"

        # Get all data points for this day
        day_points = [
            p for p in self.data_points.values()
            if p.user_id == user_id and p.timestamp.date() == summary_date
        ]

        summary = DailySummary(date=summary_date)

        for point in day_points:
            if point.data_type == DataType.STEPS:
                summary.steps = int(point.value)
            elif point.data_type == DataType.ACTIVITY:
                summary.active_minutes = int(point.value)
            elif point.data_type == DataType.CALORIES:
                summary.calories_burned = int(point.value)
            elif point.data_type == DataType.HEART_RATE:
                summary.resting_heart_rate = point.value
            elif point.data_type == DataType.HRV:
                summary.hrv_average = point.value
            elif point.data_type == DataType.SLEEP:
                summary.sleep_hours = point.value
                summary.sleep_quality = random.uniform(60, 90)
            elif point.data_type == DataType.STRESS:
                summary.stress_score = point.value

        self.daily_summaries[key] = summary

    def get_user_data(
        self,
        user_id: UUID,
        data_type: Optional[DataType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider: Optional[WearableProvider] = None
    ) -> List[HealthDataPoint]:
        """Get health data for a user."""
        points = [
            p for p in self.data_points.values()
            if p.user_id == user_id
        ]

        if data_type:
            points = [p for p in points if p.data_type == data_type]

        if provider:
            points = [p for p in points if p.provider == provider]

        if start_date:
            points = [p for p in points if p.timestamp.date() >= start_date]

        if end_date:
            points = [p for p in points if p.timestamp.date() <= end_date]

        return sorted(points, key=lambda x: x.timestamp)

    def get_daily_summaries(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[DailySummary]:
        """Get daily summaries for a date range."""
        summaries = []
        current = start_date

        while current <= end_date:
            key = f"{user_id}_{current.isoformat()}"
            if key in self.daily_summaries:
                summaries.append(self.daily_summaries[key])
            current += timedelta(days=1)

        return summaries

    def get_aggregates(
        self,
        user_id: UUID,
        data_type: DataType,
        period: str = "week"
    ) -> Dict[str, Any]:
        """Get aggregated statistics."""
        if period == "week":
            days = 7
        elif period == "month":
            days = 30
        else:
            days = 7

        start = date.today() - timedelta(days=days)
        points = self.get_user_data(user_id, data_type, start)

        if not points:
            return {"count": 0}

        values = [p.value for p in points]

        return {
            "data_type": data_type.value,
            "period": period,
            "count": len(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "total": sum(values) if data_type in [DataType.STEPS, DataType.CALORIES] else None
        }

    def get_health_score_inputs(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get wearable data inputs for health score calculation.

        Used by HealthScoreCalculator.
        """
        # Get last 7 days of summaries
        summaries = self.get_daily_summaries(
            user_id,
            date.today() - timedelta(days=7),
            date.today()
        )

        if not summaries:
            return {}

        # Calculate averages
        steps = [s.steps for s in summaries if s.steps]
        sleep = [s.sleep_hours for s in summaries if s.sleep_hours]
        hrv = [s.hrv_average for s in summaries if s.hrv_average]
        activity = [s.active_minutes for s in summaries if s.active_minutes]

        return {
            "average_steps": sum(steps) / len(steps) if steps else None,
            "average_sleep_hours": sum(sleep) / len(sleep) if sleep else None,
            "average_hrv": sum(hrv) / len(hrv) if hrv else None,
            "average_active_minutes": sum(activity) / len(activity) if activity else None,
            "data_completeness": len(summaries) / 7
        }
