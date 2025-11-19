"""
Wearable device integration service.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WearableProvider(str, Enum):
    """Supported wearable providers."""
    APPLE_HEALTH = "apple_health"
    FITBIT = "fitbit"
    OURA = "oura"
    WHOOP = "whoop"
    GARMIN = "garmin"
    GOOGLE_FIT = "google_fit"


class ConnectionStatus(str, Enum):
    """Connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ERROR = "error"


class DataType(str, Enum):
    """Types of health data from wearables."""
    STEPS = "steps"
    HEART_RATE = "heart_rate"
    HRV = "hrv"
    SLEEP = "sleep"
    ACTIVITY = "activity"
    CALORIES = "calories"
    STRESS = "stress"
    SPO2 = "spo2"
    RESPIRATORY_RATE = "respiratory_rate"
    BODY_TEMPERATURE = "body_temperature"


class WearableConnection(BaseModel):
    """A user's wearable connection."""
    id: UUID
    user_id: UUID
    provider: WearableProvider
    status: ConnectionStatus

    # OAuth tokens (encrypted in production)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

    # Sync settings
    data_types_enabled: List[DataType] = []
    last_sync: Optional[datetime] = None
    sync_frequency_hours: int = 1

    # Metadata
    device_name: Optional[str] = None
    connected_at: datetime
    updated_at: datetime


class WearableIntegrationService:
    """
    Manages wearable device integrations.

    Features:
    - OAuth connection flow
    - Multi-provider support
    - Data type configuration
    - Token refresh
    """

    # Provider configurations
    PROVIDER_CONFIG = {
        WearableProvider.APPLE_HEALTH: {
            "name": "Apple Health",
            "data_types": [
                DataType.STEPS, DataType.HEART_RATE, DataType.HRV,
                DataType.SLEEP, DataType.ACTIVITY
            ],
            "oauth_required": False,  # Uses HealthKit
            "icon": "apple"
        },
        WearableProvider.FITBIT: {
            "name": "Fitbit",
            "data_types": [
                DataType.STEPS, DataType.HEART_RATE, DataType.SLEEP,
                DataType.ACTIVITY, DataType.CALORIES
            ],
            "oauth_required": True,
            "auth_url": "https://www.fitbit.com/oauth2/authorize",
            "icon": "fitbit"
        },
        WearableProvider.OURA: {
            "name": "Oura Ring",
            "data_types": [
                DataType.SLEEP, DataType.HRV, DataType.ACTIVITY,
                DataType.BODY_TEMPERATURE, DataType.RESPIRATORY_RATE
            ],
            "oauth_required": True,
            "auth_url": "https://cloud.ouraring.com/oauth/authorize",
            "icon": "ring"
        },
        WearableProvider.WHOOP: {
            "name": "WHOOP",
            "data_types": [
                DataType.SLEEP, DataType.HRV, DataType.STRAIN,
                DataType.RECOVERY
            ],
            "oauth_required": True,
            "auth_url": "https://api.whoop.com/oauth/authorize",
            "icon": "whoop"
        },
        WearableProvider.GARMIN: {
            "name": "Garmin",
            "data_types": [
                DataType.STEPS, DataType.HEART_RATE, DataType.SLEEP,
                DataType.ACTIVITY, DataType.STRESS, DataType.SPO2
            ],
            "oauth_required": True,
            "auth_url": "https://connect.garmin.com/oauthConfirm",
            "icon": "garmin"
        }
    }

    def __init__(self):
        self.connections: Dict[UUID, WearableConnection] = {}
        logger.info("WearableIntegrationService initialized")

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available wearable providers."""
        return [
            {
                "provider": provider.value,
                "name": config["name"],
                "data_types": [dt.value for dt in config["data_types"]],
                "icon": config["icon"]
            }
            for provider, config in self.PROVIDER_CONFIG.items()
        ]

    def initiate_connection(
        self,
        user_id: UUID,
        provider: WearableProvider,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Initiate OAuth connection flow.

        Returns authorization URL for user to complete.
        """
        config = self.PROVIDER_CONFIG.get(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")

        if not config.get("oauth_required"):
            # Direct connection (Apple Health)
            return self._create_direct_connection(user_id, provider)

        # Generate OAuth URL
        state = f"{user_id}:{uuid4().hex[:8]}"

        auth_url = (
            f"{config['auth_url']}?"
            f"client_id=sana_{provider.value}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}&"
            f"response_type=code&"
            f"scope=read"
        )

        return {
            "auth_url": auth_url,
            "state": state,
            "provider": provider.value
        }

    def complete_connection(
        self,
        user_id: UUID,
        provider: WearableProvider,
        auth_code: str
    ) -> WearableConnection:
        """
        Complete OAuth connection with authorization code.

        Exchanges code for tokens and creates connection.
        """
        # In production, exchange code for tokens
        now = datetime.utcnow()

        connection = WearableConnection(
            id=uuid4(),
            user_id=user_id,
            provider=provider,
            status=ConnectionStatus.CONNECTED,
            access_token=f"token_{uuid4().hex}",
            refresh_token=f"refresh_{uuid4().hex}",
            token_expires_at=now + timedelta(hours=1),
            data_types_enabled=self.PROVIDER_CONFIG[provider]["data_types"],
            connected_at=now,
            updated_at=now
        )

        self.connections[connection.id] = connection

        logger.info(f"Connected {provider.value} for user {user_id}")

        return connection

    def _create_direct_connection(
        self,
        user_id: UUID,
        provider: WearableProvider
    ) -> Dict[str, Any]:
        """Create direct connection (no OAuth needed)."""
        now = datetime.utcnow()

        connection = WearableConnection(
            id=uuid4(),
            user_id=user_id,
            provider=provider,
            status=ConnectionStatus.CONNECTED,
            data_types_enabled=self.PROVIDER_CONFIG[provider]["data_types"],
            connected_at=now,
            updated_at=now
        )

        self.connections[connection.id] = connection

        return {
            "connection_id": str(connection.id),
            "status": "connected",
            "message": f"{provider.value} connected successfully"
        }

    def get_user_connections(self, user_id: UUID) -> List[WearableConnection]:
        """Get all wearable connections for a user."""
        return [
            c for c in self.connections.values()
            if c.user_id == user_id
        ]

    def get_connection(self, connection_id: UUID) -> Optional[WearableConnection]:
        """Get a specific connection."""
        return self.connections.get(connection_id)

    def disconnect(self, connection_id: UUID) -> bool:
        """Disconnect a wearable."""
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]
        connection.status = ConnectionStatus.DISCONNECTED
        connection.access_token = None
        connection.refresh_token = None
        connection.updated_at = datetime.utcnow()

        logger.info(f"Disconnected {connection.provider.value}")

        return True

    def update_data_types(
        self,
        connection_id: UUID,
        data_types: List[DataType]
    ) -> WearableConnection:
        """Update which data types to sync."""
        if connection_id not in self.connections:
            raise ValueError("Connection not found")

        connection = self.connections[connection_id]

        # Verify data types are valid for provider
        valid_types = self.PROVIDER_CONFIG[connection.provider]["data_types"]
        for dt in data_types:
            if dt not in valid_types:
                raise ValueError(f"{dt} not supported by {connection.provider}")

        connection.data_types_enabled = data_types
        connection.updated_at = datetime.utcnow()

        return connection

    def refresh_token(self, connection_id: UUID) -> bool:
        """Refresh OAuth token for a connection."""
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]

        if not connection.refresh_token:
            return False

        # In production, call provider's token refresh endpoint
        connection.access_token = f"token_{uuid4().hex}"
        connection.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        connection.updated_at = datetime.utcnow()

        logger.info(f"Refreshed token for {connection.provider.value}")

        return True

    def get_connection_status(self, user_id: UUID) -> Dict[str, Any]:
        """Get status of all connections for a user."""
        connections = self.get_user_connections(user_id)

        status = {}
        for provider in WearableProvider:
            conn = next(
                (c for c in connections if c.provider == provider),
                None
            )
            status[provider.value] = {
                "connected": conn is not None and conn.status == ConnectionStatus.CONNECTED,
                "last_sync": conn.last_sync.isoformat() if conn and conn.last_sync else None,
                "data_types": [dt.value for dt in conn.data_types_enabled] if conn else []
            }

        return status
