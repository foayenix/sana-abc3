"""
Analytics API routes for SANA Platform.

Endpoints for practitioner, client, and platform analytics.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from uuid import UUID
from datetime import date

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.analytics.practitioner import PractitionerAnalytics
from services.analytics.client import ClientAnalytics
from services.analytics.platform import PlatformAnalytics

router = APIRouter()

# Initialize services
practitioner_analytics = PractitionerAnalytics()
client_analytics = ClientAnalytics()
platform_analytics = PlatformAnalytics()


# ============================================================================
# PRACTITIONER ANALYTICS
# ============================================================================

@router.get("/practitioner/{practitioner_id}/dashboard")
async def get_practitioner_dashboard(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get complete analytics dashboard for a practitioner."""
    return practitioner_analytics.get_dashboard(
        practitioner_id,
        start_date,
        end_date
    )


@router.get("/practitioner/{practitioner_id}/revenue")
async def get_practitioner_revenue(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get revenue metrics for a practitioner."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return practitioner_analytics.get_revenue_metrics(
        practitioner_id,
        start_date,
        end_date
    ).dict()


@router.get("/practitioner/{practitioner_id}/clients")
async def get_practitioner_client_metrics(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get client metrics for a practitioner."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return practitioner_analytics.get_client_metrics(
        practitioner_id,
        start_date,
        end_date
    ).dict()


@router.get("/practitioner/{practitioner_id}/sessions")
async def get_practitioner_session_metrics(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get session metrics for a practitioner."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return practitioner_analytics.get_session_metrics(
        practitioner_id,
        start_date,
        end_date
    ).dict()


@router.get("/practitioner/{practitioner_id}/outcomes")
async def get_practitioner_outcome_metrics(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get outcome metrics for a practitioner."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return practitioner_analytics.get_outcome_metrics(
        practitioner_id,
        start_date,
        end_date
    ).dict()


@router.get("/practitioner/{practitioner_id}/comparison")
async def get_practitioner_comparison(
    practitioner_id: UUID,
    metric: str = "revenue"
):
    """Get comparison with platform benchmarks."""
    return practitioner_analytics.get_comparison(practitioner_id, metric)


@router.get("/practitioner/{practitioner_id}/export")
async def export_practitioner_report(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    format: str = "json"
):
    """Export analytics report."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return practitioner_analytics.export_report(
        practitioner_id,
        start_date,
        end_date,
        format
    )


# ============================================================================
# CLIENT ANALYTICS
# ============================================================================

@router.get("/client/{client_id}/dashboard")
async def get_client_dashboard(
    client_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get complete analytics dashboard for a client."""
    return client_analytics.get_dashboard(client_id, start_date, end_date)


@router.get("/client/{client_id}/health-progress")
async def get_client_health_progress(
    client_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get health progress metrics for a client."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return client_analytics.get_health_progress(
        client_id,
        start_date,
        end_date
    ).dict()


@router.get("/client/{client_id}/engagement")
async def get_client_engagement(
    client_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get engagement metrics for a client."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return client_analytics.get_engagement_metrics(
        client_id,
        start_date,
        end_date
    ).dict()


@router.get("/client/{client_id}/wellness")
async def get_client_wellness(
    client_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get wellness metrics for a client."""
    if not start_date:
        from datetime import timedelta
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    return client_analytics.get_wellness_metrics(
        client_id,
        start_date,
        end_date
    ).dict()


@router.get("/client/{client_id}/treatment-summary")
async def get_client_treatment_summary(client_id: UUID):
    """Get treatment summary for a client."""
    return client_analytics.get_treatment_summary(client_id)


# ============================================================================
# PLATFORM ANALYTICS
# ============================================================================

@router.get("/platform/overview")
async def get_platform_overview(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get platform-wide overview metrics."""
    return platform_analytics.get_overview(start_date, end_date)


@router.get("/platform/growth")
async def get_platform_growth(period_days: int = 30):
    """Get platform growth metrics."""
    return platform_analytics.get_growth_metrics(period_days)


@router.get("/platform/top-practitioners")
async def get_top_practitioners(limit: int = 10):
    """Get top performing practitioners."""
    return platform_analytics.get_top_practitioners(limit)


@router.get("/platform/specialties")
async def get_specialty_breakdown():
    """Get breakdown by specialty."""
    return platform_analytics.get_specialty_breakdown()


@router.get("/platform/geography")
async def get_geographic_distribution():
    """Get geographic distribution of users."""
    return platform_analytics.get_geographic_distribution()
