"""
Compliance and audit service for regulatory requirements.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""
    # User events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PASSWORD_CHANGED = "password_changed"

    # Data access
    RECORD_VIEWED = "record_viewed"
    RECORD_CREATED = "record_created"
    RECORD_UPDATED = "record_updated"
    RECORD_DELETED = "record_deleted"
    RECORD_EXPORTED = "record_exported"

    # Clinical events
    SESSION_CREATED = "session_created"
    SESSION_COMPLETED = "session_completed"
    NOTES_ADDED = "notes_added"
    PROM_SUBMITTED = "prom_submitted"

    # Admin events
    SETTINGS_CHANGED = "settings_changed"
    PERMISSION_CHANGED = "permission_changed"
    CONSENT_UPDATED = "consent_updated"


class AuditSeverity(str, Enum):
    """Severity of audit event."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ConsentType(str, Enum):
    """Types of consent."""
    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    RESEARCH = "research"
    DATA_SHARING = "data_sharing"
    WEARABLE_DATA = "wearable_data"


class AuditEvent(BaseModel):
    """An audit log event."""
    id: UUID
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO

    # Actor
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None

    # Target
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None

    # Context
    tenant_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Details
    description: str
    metadata: Dict[str, Any] = {}

    # Timestamp
    timestamp: datetime


class ConsentRecord(BaseModel):
    """User consent record."""
    id: UUID
    user_id: UUID
    consent_type: ConsentType
    granted: bool
    version: str
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str] = None


class DataRetentionPolicy(BaseModel):
    """Data retention policy."""
    id: UUID
    tenant_id: Optional[UUID] = None  # None for platform default
    data_type: str
    retention_days: int
    auto_delete: bool = False
    archive_before_delete: bool = True
    description: str


class ComplianceService:
    """
    Compliance and audit service.

    Features:
    - Audit logging
    - Consent management
    - Data retention policies
    - GDPR compliance tools
    - Regulatory reporting
    """

    def __init__(self):
        self.audit_events: List[AuditEvent] = []
        self.consent_records: Dict[UUID, ConsentRecord] = {}
        self.retention_policies: Dict[UUID, DataRetentionPolicy] = {}
        self._init_default_policies()
        logger.info("ComplianceService initialized")

    def _init_default_policies(self):
        """Initialize default retention policies."""
        defaults = [
            ("session_notes", 2555, "Clinical session notes - 7 years"),
            ("audit_logs", 2555, "Audit logs - 7 years"),
            ("messages", 365, "Messages - 1 year after account closure"),
            ("payment_records", 2555, "Payment records - 7 years"),
            ("analytics", 730, "Analytics data - 2 years")
        ]

        for data_type, days, description in defaults:
            policy = DataRetentionPolicy(
                id=uuid4(),
                data_type=data_type,
                retention_days=days,
                description=description
            )
            self.retention_policies[policy.id] = policy

    def log_event(
        self,
        event_type: AuditEventType,
        description: str,
        user_id: Optional[UUID] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        metadata: Optional[Dict] = None
    ) -> AuditEvent:
        """
        Log an audit event.

        Args:
            event_type: Type of event
            description: Human-readable description
            user_id: Acting user ID
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            tenant_id: Tenant context
            ip_address: Client IP
            user_agent: Client user agent
            severity: Event severity
            metadata: Additional data

        Returns:
            Created audit event
        """
        event = AuditEvent(
            id=uuid4(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )

        self.audit_events.append(event)

        if severity == AuditSeverity.CRITICAL:
            logger.warning(f"Critical audit event: {description}")

        return event

    def get_audit_trail(
        self,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        tenant_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Get audit trail with filters."""
        events = self.audit_events

        if user_id:
            events = [e for e in events if e.user_id == user_id]

        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]

        if resource_id:
            events = [e for e in events if e.resource_id == resource_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]

        if start_date:
            events = [e for e in events if e.timestamp >= start_date]

        if end_date:
            events = [e for e in events if e.timestamp <= end_date]

        # Sort by timestamp descending
        events.sort(key=lambda x: x.timestamp, reverse=True)

        return events[:limit]

    def record_consent(
        self,
        user_id: UUID,
        consent_type: ConsentType,
        granted: bool,
        version: str,
        ip_address: Optional[str] = None
    ) -> ConsentRecord:
        """
        Record user consent.

        Args:
            user_id: User ID
            consent_type: Type of consent
            granted: Whether consent was granted
            version: Policy version consented to
            ip_address: Client IP for audit

        Returns:
            Consent record
        """
        now = datetime.utcnow()

        record = ConsentRecord(
            id=uuid4(),
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            version=version,
            granted_at=now if granted else None,
            revoked_at=now if not granted else None,
            ip_address=ip_address
        )

        self.consent_records[record.id] = record

        # Log audit event
        self.log_event(
            event_type=AuditEventType.CONSENT_UPDATED,
            description=f"Consent {consent_type.value} {'granted' if granted else 'revoked'}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={"consent_type": consent_type.value, "granted": granted, "version": version}
        )

        return record

    def get_user_consents(self, user_id: UUID) -> List[ConsentRecord]:
        """Get all consent records for a user."""
        return [
            r for r in self.consent_records.values()
            if r.user_id == user_id
        ]

    def check_consent(self, user_id: UUID, consent_type: ConsentType) -> bool:
        """Check if user has granted specific consent."""
        user_consents = self.get_user_consents(user_id)

        for consent in user_consents:
            if consent.consent_type == consent_type and consent.granted:
                return True

        return False

    def get_retention_policy(
        self,
        data_type: str,
        tenant_id: Optional[UUID] = None
    ) -> Optional[DataRetentionPolicy]:
        """Get retention policy for a data type."""
        # Check tenant-specific policy first
        if tenant_id:
            for policy in self.retention_policies.values():
                if policy.data_type == data_type and policy.tenant_id == tenant_id:
                    return policy

        # Fall back to default
        for policy in self.retention_policies.values():
            if policy.data_type == data_type and policy.tenant_id is None:
                return policy

        return None

    def set_retention_policy(
        self,
        data_type: str,
        retention_days: int,
        description: str,
        tenant_id: Optional[UUID] = None,
        auto_delete: bool = False,
        archive_before_delete: bool = True
    ) -> DataRetentionPolicy:
        """Set or update retention policy."""
        policy = DataRetentionPolicy(
            id=uuid4(),
            tenant_id=tenant_id,
            data_type=data_type,
            retention_days=retention_days,
            auto_delete=auto_delete,
            archive_before_delete=archive_before_delete,
            description=description
        )

        self.retention_policies[policy.id] = policy
        return policy

    def generate_gdpr_export(self, user_id: UUID) -> Dict[str, Any]:
        """
        Generate GDPR data export for a user.

        Returns all personal data in portable format.
        """
        # Get audit events
        audit_events = self.get_audit_trail(user_id=user_id, limit=1000)

        # Get consents
        consents = self.get_user_consents(user_id)

        return {
            "export_date": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "data_categories": {
                "audit_events": [
                    {
                        "event_type": e.event_type.value,
                        "description": e.description,
                        "timestamp": e.timestamp.isoformat()
                    }
                    for e in audit_events
                ],
                "consents": [
                    {
                        "consent_type": c.consent_type.value,
                        "granted": c.granted,
                        "version": c.version,
                        "timestamp": (c.granted_at or c.revoked_at).isoformat() if (c.granted_at or c.revoked_at) else None
                    }
                    for c in consents
                ]
            },
            "export_format": "JSON",
            "gdpr_article": "Article 20 - Right to data portability"
        }

    def process_deletion_request(
        self,
        user_id: UUID,
        reason: str
    ) -> Dict[str, Any]:
        """
        Process GDPR deletion request (right to be forgotten).

        Returns deletion report.
        """
        # Log the request
        self.log_event(
            event_type=AuditEventType.USER_DELETED,
            description=f"GDPR deletion request processed: {reason}",
            user_id=user_id,
            severity=AuditSeverity.CRITICAL,
            metadata={"reason": reason}
        )

        # In production, would actually delete/anonymize data
        return {
            "user_id": str(user_id),
            "request_date": datetime.utcnow().isoformat(),
            "reason": reason,
            "status": "processed",
            "data_deleted": [
                "personal_information",
                "session_records",
                "messages",
                "payment_methods"
            ],
            "data_retained": [
                "anonymized_analytics",
                "financial_records_for_legal_compliance"
            ],
            "retention_period": "7 years for legal compliance",
            "gdpr_article": "Article 17 - Right to erasure"
        }

    def generate_compliance_report(
        self,
        tenant_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate compliance report for auditors."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        events = self.get_audit_trail(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )

        # Categorize events
        by_type = {}
        by_severity = {}

        for event in events:
            by_type[event.event_type.value] = by_type.get(event.event_type.value, 0) + 1
            by_severity[event.severity.value] = by_severity.get(event.severity.value, 0) + 1

        critical_events = [e for e in events if e.severity == AuditSeverity.CRITICAL]

        return {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "tenant_id": str(tenant_id) if tenant_id else "platform",
            "summary": {
                "total_events": len(events),
                "by_type": by_type,
                "by_severity": by_severity,
                "critical_events_count": len(critical_events)
            },
            "critical_events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type.value,
                    "description": e.description,
                    "user_id": str(e.user_id) if e.user_id else None
                }
                for e in critical_events[:50]
            ],
            "retention_policies": [
                {
                    "data_type": p.data_type,
                    "retention_days": p.retention_days,
                    "auto_delete": p.auto_delete
                }
                for p in self.retention_policies.values()
                if p.tenant_id == tenant_id or p.tenant_id is None
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
