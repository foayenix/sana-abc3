"""
Platform-wide analytics service.
"""

from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class PlatformAnalytics:
    """
    Platform-wide analytics for SANA admin.

    Provides insights on:
    - User growth
    - Revenue metrics
    - Engagement
    - Treatment effectiveness
    """

    def __init__(self):
        logger.info("PlatformAnalytics initialized")

    def get_overview(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """Get platform overview metrics."""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "users": {
                "total_clients": 1250,
                "total_practitioners": 180,
                "new_clients": 145,
                "new_practitioners": 12,
                "growth_rate": 0.12
            },
            "sessions": {
                "total": 4500,
                "completed": 4150,
                "average_per_day": 150
            },
            "revenue": {
                "gmv": 382500.0,
                "platform_revenue": 38250.0,
                "average_order_value": 85.0
            },
            "engagement": {
                "daily_active_users": 420,
                "weekly_active_users": 890,
                "monthly_active_users": 1100
            },
            "outcomes": {
                "average_improvement": 27.5,
                "clients_improved": 890,
                "average_sana_score": 62.0
            }
        }

    def get_growth_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get growth metrics."""
        # Generate trend data
        trend = []
        current = date.today() - timedelta(days=period_days)
        users = 1000

        while current <= date.today():
            users += 5  # Daily growth
            trend.append({
                "date": current.isoformat(),
                "users": users
            })
            current += timedelta(days=1)

        return {
            "user_growth": trend,
            "growth_rate": 0.15,
            "projected_users_30d": int(users * 1.15)
        }

    def get_top_practitioners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing practitioners."""
        return [
            {
                "rank": i + 1,
                "name": f"Practitioner {i + 1}",
                "sana_index": 95 - (i * 2),
                "total_sessions": 150 - (i * 10),
                "revenue": 12000 - (i * 800),
                "rating": 5.0 - (i * 0.1)
            }
            for i in range(limit)
        ]

    def get_specialty_breakdown(self) -> List[Dict[str, Any]]:
        """Get breakdown by specialty."""
        return [
            {"specialty": "Acupuncture", "practitioners": 45, "sessions": 1200, "revenue": 102000},
            {"specialty": "Herbalism", "practitioners": 35, "sessions": 800, "revenue": 64000},
            {"specialty": "Naturopathy", "practitioners": 28, "sessions": 650, "revenue": 58500},
            {"specialty": "Massage Therapy", "practitioners": 32, "sessions": 900, "revenue": 63000},
            {"specialty": "Nutrition", "practitioners": 20, "sessions": 450, "revenue": 36000}
        ]

    def get_geographic_distribution(self) -> Dict[str, Any]:
        """Get geographic distribution of users."""
        return {
            "by_city": [
                {"city": "London", "clients": 450, "practitioners": 65},
                {"city": "Manchester", "clients": 180, "practitioners": 28},
                {"city": "Birmingham", "clients": 120, "practitioners": 18},
                {"city": "Bristol", "clients": 95, "practitioners": 15},
                {"city": "Leeds", "clients": 85, "practitioners": 12}
            ],
            "coverage": {
                "cities_with_practitioners": 42,
                "average_practitioners_per_city": 4.3
            }
        }
