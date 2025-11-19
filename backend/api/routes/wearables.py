"""
Wearables API routes for SANA Platform.

Endpoints for wearable device integration and health data sync.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import date

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.wearables.integrations import WearableIntegrationService, WearableProvider, DataType
from services.wearables.data_sync import WearableDataSync

router = APIRouter()

# Initialize services
integration_service = WearableIntegrationService()
data_sync = WearableDataSync()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class InitiateConnectionRequest(BaseModel):
    """Initiate wearable connection."""
    user_id: UUID
    provider: str
    redirect_uri: str


class CompleteConnectionRequest(BaseModel):
    """Complete wearable connection."""
    user_id: UUID
    provider: str
    auth_code: str


class UpdateDataTypesRequest(BaseModel):
    """Update data types to sync."""
    data_types: List[str]


class SyncDataRequest(BaseModel):
    """Sync data from wearable."""
    user_id: UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# ============================================================================
# CONNECTION ENDPOINTS
# ============================================================================

@router.get("/providers")
async def get_available_providers():
    """Get list of available wearable providers."""
    return integration_service.get_available_providers()


@router.post("/connect")
async def initiate_connection(request: InitiateConnectionRequest):
    """Initiate OAuth connection flow."""
    try:
        provider = WearableProvider(request.provider)
        return integration_service.initiate_connection(
            request.user_id,
            provider,
            request.redirect_uri
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/connect/complete")
async def complete_connection(request: CompleteConnectionRequest):
    """Complete OAuth connection with authorization code."""
    try:
        provider = WearableProvider(request.provider)
        connection = integration_service.complete_connection(
            request.user_id,
            provider,
            request.auth_code
        )

        return {
            "connection_id": str(connection.id),
            "provider": connection.provider.value,
            "status": connection.status.value,
            "data_types": [dt.value for dt in connection.data_types_enabled]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/connections/{user_id}")
async def get_user_connections(user_id: UUID):
    """Get all wearable connections for a user."""
    connections = integration_service.get_user_connections(user_id)

    return {
        "count": len(connections),
        "connections": [
            {
                "id": str(c.id),
                "provider": c.provider.value,
                "status": c.status.value,
                "data_types": [dt.value for dt in c.data_types_enabled],
                "last_sync": c.last_sync.isoformat() if c.last_sync else None,
                "connected_at": c.connected_at.isoformat()
            }
            for c in connections
        ]
    }


@router.get("/connections/status/{user_id}")
async def get_connection_status(user_id: UUID):
    """Get status of all connections for a user."""
    return integration_service.get_connection_status(user_id)


@router.delete("/connections/{connection_id}")
async def disconnect_wearable(connection_id: UUID):
    """Disconnect a wearable."""
    success = integration_service.disconnect(connection_id)

    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")

    return {"message": "Wearable disconnected"}


@router.put("/connections/{connection_id}/data-types")
async def update_data_types(connection_id: UUID, request: UpdateDataTypesRequest):
    """Update which data types to sync."""
    try:
        data_types = [DataType(dt) for dt in request.data_types]
        connection = integration_service.update_data_types(connection_id, data_types)

        return {
            "connection_id": str(connection.id),
            "data_types": [dt.value for dt in connection.data_types_enabled]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# DATA SYNC ENDPOINTS
# ============================================================================

@router.post("/sync/{connection_id}")
async def sync_wearable_data(connection_id: UUID, request: SyncDataRequest):
    """Sync data from a wearable connection."""
    connection = integration_service.get_connection(connection_id)

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    result = data_sync.sync_data(
        user_id=request.user_id,
        provider=connection.provider,
        access_token=connection.access_token or "",
        data_types=connection.data_types_enabled,
        start_date=request.start_date,
        end_date=request.end_date
    )

    # Update last sync time
    connection.last_sync = data_sync.daily_summaries.get(
        f"{request.user_id}_{date.today().isoformat()}"
    )

    return result


@router.get("/data/{user_id}")
async def get_user_health_data(
    user_id: UUID,
    data_type: Optional[str] = None,
    provider: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get health data for a user."""
    dt = DataType(data_type) if data_type else None
    prov = WearableProvider(provider) if provider else None

    points = data_sync.get_user_data(
        user_id,
        dt,
        start_date,
        end_date,
        prov
    )

    return {
        "count": len(points),
        "data": [
            {
                "id": str(p.id),
                "data_type": p.data_type.value,
                "value": p.value,
                "unit": p.unit,
                "timestamp": p.timestamp.isoformat(),
                "provider": p.provider.value
            }
            for p in points
        ]
    }


@router.get("/summaries/{user_id}")
async def get_daily_summaries(
    user_id: UUID,
    start_date: date,
    end_date: date
):
    """Get daily health summaries."""
    summaries = data_sync.get_daily_summaries(user_id, start_date, end_date)

    return {
        "count": len(summaries),
        "summaries": [
            {
                "date": s.date.isoformat(),
                "steps": s.steps,
                "active_minutes": s.active_minutes,
                "calories_burned": s.calories_burned,
                "resting_heart_rate": s.resting_heart_rate,
                "hrv_average": s.hrv_average,
                "sleep_hours": s.sleep_hours,
                "sleep_quality": s.sleep_quality,
                "stress_score": s.stress_score
            }
            for s in summaries
        ]
    }


@router.get("/aggregates/{user_id}")
async def get_aggregates(
    user_id: UUID,
    data_type: str,
    period: str = "week"
):
    """Get aggregated statistics for a data type."""
    try:
        dt = DataType(data_type)
        return data_sync.get_aggregates(user_id, dt, period)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid data type")


@router.get("/health-score-inputs/{user_id}")
async def get_health_score_inputs(user_id: UUID):
    """Get wearable data inputs for health score calculation."""
    return data_sync.get_health_score_inputs(user_id)


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@router.get("/test-setup/{user_id}")
async def test_wearables(user_id: UUID):
    """Set up test wearable data."""
    from datetime import timedelta

    # Create a test Fitbit connection
    connection = integration_service.complete_connection(
        user_id,
        WearableProvider.FITBIT,
        "test_auth_code"
    )

    # Sync 7 days of data
    result = data_sync.sync_data(
        user_id=user_id,
        provider=WearableProvider.FITBIT,
        access_token=connection.access_token or "",
        data_types=connection.data_types_enabled,
        start_date=date.today() - timedelta(days=7),
        end_date=date.today()
    )

    return {
        "connection_id": str(connection.id),
        "provider": "fitbit",
        "sync_result": result,
        "message": "Test wearable data created"
    }
