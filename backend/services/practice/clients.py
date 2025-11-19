"""
Client management service for practitioners.
"""

from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class PractitionerClient(BaseModel):
    """A client associated with a practitioner."""
    id: UUID
    practitioner_id: UUID
    client_id: UUID

    # Client info (would come from user profile)
    name: str
    email: str
    phone: Optional[str] = None

    # Relationship
    first_session_date: Optional[datetime] = None
    last_session_date: Optional[datetime] = None
    total_sessions: int = 0
    status: str = "active"  # active, inactive, discharged

    # Health summary
    presenting_concerns: List[str] = []
    goals: List[str] = []
    current_treatments: List[str] = []
    notes: str = ""

    # Tags
    tags: List[str] = []

    created_at: datetime
    updated_at: datetime


class ClientManagementService:
    """
    Manages practitioner's client relationships.

    Features:
    - Add/remove clients
    - Track session history
    - Store client notes and concerns
    - Tag and filter clients
    """

    def __init__(self):
        self.clients: Dict[UUID, PractitionerClient] = {}
        logger.info("ClientManagementService initialized")

    def add_client(
        self,
        practitioner_id: UUID,
        client_id: UUID,
        name: str,
        email: str,
        phone: Optional[str] = None,
        presenting_concerns: List[str] = None,
        goals: List[str] = None
    ) -> PractitionerClient:
        """Add a new client to practitioner's roster."""
        now = datetime.utcnow()

        client = PractitionerClient(
            id=uuid4(),
            practitioner_id=practitioner_id,
            client_id=client_id,
            name=name,
            email=email,
            phone=phone,
            presenting_concerns=presenting_concerns or [],
            goals=goals or [],
            created_at=now,
            updated_at=now
        )

        self.clients[client.id] = client
        logger.info(f"Added client {client.id} for practitioner {practitioner_id}")

        return client

    def get_practitioner_clients(
        self,
        practitioner_id: UUID,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> List[PractitionerClient]:
        """
        Get all clients for a practitioner with optional filters.

        Args:
            practitioner_id: Practitioner UUID
            status: Filter by status (active, inactive, discharged)
            tags: Filter by tags
            search: Search name/email

        Returns:
            Filtered list of clients
        """
        clients = [
            c for c in self.clients.values()
            if c.practitioner_id == practitioner_id
        ]

        if status:
            clients = [c for c in clients if c.status == status]

        if tags:
            clients = [c for c in clients if any(t in c.tags for t in tags)]

        if search:
            search_lower = search.lower()
            clients = [
                c for c in clients
                if search_lower in c.name.lower() or search_lower in c.email.lower()
            ]

        return sorted(clients, key=lambda x: x.name)

    def get_client(self, client_record_id: UUID) -> Optional[PractitionerClient]:
        """Get a specific client record."""
        return self.clients.get(client_record_id)

    def update_client(
        self,
        client_record_id: UUID,
        updates: Dict
    ) -> Optional[PractitionerClient]:
        """Update client information."""
        if client_record_id not in self.clients:
            return None

        client = self.clients[client_record_id]

        for key, value in updates.items():
            if hasattr(client, key):
                setattr(client, key, value)

        client.updated_at = datetime.utcnow()
        return client

    def record_session(
        self,
        client_record_id: UUID,
        session_date: datetime
    ) -> bool:
        """Record that a session occurred with this client."""
        if client_record_id not in self.clients:
            return False

        client = self.clients[client_record_id]
        client.total_sessions += 1
        client.last_session_date = session_date

        if not client.first_session_date:
            client.first_session_date = session_date

        client.updated_at = datetime.utcnow()
        return True

    def discharge_client(
        self,
        client_record_id: UUID,
        reason: str = ""
    ) -> bool:
        """Mark a client as discharged."""
        if client_record_id not in self.clients:
            return False

        client = self.clients[client_record_id]
        client.status = "discharged"
        client.notes += f"\n[Discharged {datetime.utcnow().isoformat()}]: {reason}"
        client.updated_at = datetime.utcnow()

        return True

    def get_client_stats(self, practitioner_id: UUID) -> Dict:
        """Get statistics about practitioner's client base."""
        clients = [
            c for c in self.clients.values()
            if c.practitioner_id == practitioner_id
        ]

        active = len([c for c in clients if c.status == "active"])
        inactive = len([c for c in clients if c.status == "inactive"])
        discharged = len([c for c in clients if c.status == "discharged"])

        total_sessions = sum(c.total_sessions for c in clients)

        return {
            "total_clients": len(clients),
            "active": active,
            "inactive": inactive,
            "discharged": discharged,
            "total_sessions": total_sessions,
            "avg_sessions_per_client": total_sessions / len(clients) if clients else 0
        }
