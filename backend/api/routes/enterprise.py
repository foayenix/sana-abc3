"""
Enterprise API routes for SANA Platform.

Endpoints for FHIR, NHS integration, multi-tenancy, and compliance.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.enterprise.fhir import FHIRIntegrationService, FHIRResourceType
from services.enterprise.nhs import NHSConnectService, NHSReferralStatus
from services.enterprise.tenant import MultiTenantService, TenantType, TenantStatus, SSOProvider
from services.enterprise.compliance import ComplianceService, AuditEventType, AuditSeverity, ConsentType

router = APIRouter()

# Initialize services
fhir_service = FHIRIntegrationService()
nhs_service = NHSConnectService()
tenant_service = MultiTenantService()
compliance_service = ComplianceService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class MapClientRequest(BaseModel):
    """Map client to FHIR Patient."""
    id: str
    first_name: str
    last_name: str
    email: str
    gender: str = "unknown"
    date_of_birth: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None


class MapPractitionerRequest(BaseModel):
    """Map practitioner to FHIR."""
    id: str
    name: str
    title: str
    email: str
    credentials: List[Dict[str, str]] = []


class CreateReferralRequest(BaseModel):
    """Create NHS referral."""
    patient_nhs_number: str
    patient_name: str
    gp_practice_code: str
    gp_name: str
    condition: str
    clinical_notes: str
    urgency: str = "routine"


class CreateTenantRequest(BaseModel):
    """Create a tenant."""
    name: str
    tenant_type: str
    admin_email: str
    slug: Optional[str] = None
    max_users: int = 100
    max_practitioners: int = 10


class ConfigureSSORequest(BaseModel):
    """Configure SSO."""
    provider: str
    config: Dict[str, Any]


class SetBrandingRequest(BaseModel):
    """Set tenant branding."""
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    custom_domain: Optional[str] = None


class AddTenantUserRequest(BaseModel):
    """Add user to tenant."""
    user_id: UUID
    role: str = "member"
    department: Optional[str] = None
    employee_id: Optional[str] = None


class RecordConsentRequest(BaseModel):
    """Record consent."""
    user_id: UUID
    consent_type: str
    granted: bool
    version: str
    ip_address: Optional[str] = None


class LogAuditRequest(BaseModel):
    """Log audit event."""
    event_type: str
    description: str
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    tenant_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    severity: str = "info"
    metadata: Optional[Dict] = None


# ============================================================================
# FHIR ENDPOINTS
# ============================================================================

@router.post("/fhir/patient")
async def map_client_to_patient(request: MapClientRequest):
    """Map SANA client to FHIR Patient resource."""
    resource = fhir_service.map_client_to_patient(request.dict())

    return {
        "resource_id": resource.id,
        "resource_type": resource.resourceType,
        "identifier": resource.identifier
    }


@router.post("/fhir/practitioner")
async def map_practitioner_to_fhir(request: MapPractitionerRequest):
    """Map SANA practitioner to FHIR Practitioner resource."""
    resource = fhir_service.map_practitioner_to_fhir(request.dict())

    return {
        "resource_id": resource.id,
        "resource_type": resource.resourceType,
        "identifier": resource.identifier
    }


@router.get("/fhir/resource/{resource_id}")
async def get_fhir_resource(resource_id: str):
    """Get a FHIR resource."""
    resource = fhir_service.get_resource(resource_id)

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return {
        "resourceType": resource.resourceType,
        "id": resource.id,
        "meta": resource.meta,
        "identifier": resource.identifier,
        **resource.data
    }


@router.get("/fhir/patient/{patient_id}/export")
async def export_patient_record(
    patient_id: str,
    include_observations: bool = True,
    include_encounters: bool = True
):
    """Export complete patient record as FHIR Bundle."""
    bundle = fhir_service.export_patient_record(
        patient_id,
        include_observations,
        include_encounters
    )

    return bundle


@router.post("/fhir/validate")
async def validate_fhir_resource(resource_id: str):
    """Validate a FHIR resource."""
    resource = fhir_service.get_resource(resource_id)

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return fhir_service.validate_resource(resource)


# ============================================================================
# NHS ENDPOINTS
# ============================================================================

@router.get("/nhs/validate/{nhs_number}")
async def validate_nhs_number(nhs_number: str):
    """Validate an NHS number."""
    return nhs_service.validate_nhs_number(nhs_number)


@router.get("/nhs/pds/{nhs_number}")
async def lookup_patient_demographics(nhs_number: str):
    """Look up patient demographics from PDS."""
    return nhs_service.lookup_patient_demographics(nhs_number)


@router.post("/nhs/referrals")
async def create_referral(request: CreateReferralRequest):
    """Create an NHS referral."""
    referral = nhs_service.create_referral(
        patient_nhs_number=request.patient_nhs_number,
        patient_name=request.patient_name,
        gp_practice_code=request.gp_practice_code,
        gp_name=request.gp_name,
        condition=request.condition,
        clinical_notes=request.clinical_notes,
        urgency=request.urgency
    )

    return {
        "id": str(referral.id),
        "nhs_reference": referral.nhs_reference,
        "status": referral.status.value
    }


@router.get("/nhs/referrals/{referral_id}")
async def get_referral(referral_id: UUID):
    """Get a referral."""
    referral = nhs_service.get_referral(referral_id)

    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    return {
        "id": str(referral.id),
        "nhs_reference": referral.nhs_reference,
        "patient_name": referral.patient_name,
        "condition": referral.condition,
        "urgency": referral.urgency,
        "status": referral.status.value,
        "matched_practitioner_id": str(referral.matched_practitioner_id) if referral.matched_practitioner_id else None
    }


@router.post("/nhs/referrals/{referral_id}/match")
async def match_referral(referral_id: UUID, practitioner_id: UUID, specialty: str):
    """Match referral to a practitioner."""
    try:
        referral = nhs_service.match_referral_to_practitioner(
            referral_id,
            practitioner_id,
            specialty
        )

        return {
            "id": str(referral.id),
            "matched_practitioner_id": str(referral.matched_practitioner_id),
            "matched_specialty": referral.matched_specialty
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nhs/referrals/{referral_id}/accept")
async def accept_referral(referral_id: UUID):
    """Accept a referral."""
    try:
        referral = nhs_service.accept_referral(referral_id)
        return {"status": referral.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nhs/referrals/{referral_id}/complete")
async def complete_referral(referral_id: UUID):
    """Complete a referral."""
    try:
        referral = nhs_service.complete_referral(referral_id)
        return {"status": referral.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nhs/referrals/status/{status}")
async def get_referrals_by_status(status: str):
    """Get all referrals with a given status."""
    try:
        referral_status = NHSReferralStatus(status)
        referrals = nhs_service.get_referrals_by_status(referral_status)

        return {
            "count": len(referrals),
            "referrals": [
                {
                    "id": str(r.id),
                    "nhs_reference": r.nhs_reference,
                    "patient_name": r.patient_name,
                    "condition": r.condition
                }
                for r in referrals
            ]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")


@router.get("/nhs/statistics")
async def get_referral_statistics():
    """Get referral statistics."""
    return nhs_service.get_referral_statistics()


# ============================================================================
# TENANT ENDPOINTS
# ============================================================================

@router.post("/tenants")
async def create_tenant(request: CreateTenantRequest):
    """Create a new tenant."""
    try:
        tenant_type = TenantType(request.tenant_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tenant type")

    tenant = tenant_service.create_tenant(
        name=request.name,
        tenant_type=tenant_type,
        admin_email=request.admin_email,
        slug=request.slug,
        max_users=request.max_users,
        max_practitioners=request.max_practitioners
    )

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "status": tenant.status.value
    }


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: UUID):
    """Get tenant details."""
    tenant = tenant_service.get_tenant(tenant_id)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "tenant_type": tenant.tenant_type.value,
        "status": tenant.status.value,
        "admin_email": tenant.admin_email,
        "max_users": tenant.max_users,
        "sso_enabled": tenant.sso_enabled,
        "features_enabled": tenant.features_enabled
    }


@router.get("/tenants/slug/{slug}")
async def get_tenant_by_slug(slug: str):
    """Get tenant by slug."""
    tenant = tenant_service.get_tenant_by_slug(slug)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "branding": {
            "logo_url": tenant.logo_url,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color
        }
    }


@router.post("/tenants/{tenant_id}/sso")
async def configure_sso(tenant_id: UUID, request: ConfigureSSORequest):
    """Configure SSO for a tenant."""
    try:
        provider = SSOProvider(request.provider)
        tenant = tenant_service.configure_sso(tenant_id, provider, request.config)

        return {
            "sso_enabled": tenant.sso_enabled,
            "sso_provider": tenant.sso_provider.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tenants/{tenant_id}/branding")
async def set_branding(tenant_id: UUID, request: SetBrandingRequest):
    """Set tenant branding."""
    try:
        tenant = tenant_service.set_branding(
            tenant_id,
            request.logo_url,
            request.primary_color,
            request.secondary_color,
            request.custom_domain
        )

        return {
            "logo_url": tenant.logo_url,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "custom_domain": tenant.custom_domain
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tenants/{tenant_id}/users")
async def add_tenant_user(tenant_id: UUID, request: AddTenantUserRequest):
    """Add user to tenant."""
    try:
        tenant_user = tenant_service.add_user_to_tenant(
            tenant_id,
            request.user_id,
            request.role,
            request.department,
            request.employee_id
        )

        return {
            "id": str(tenant_user.id),
            "user_id": str(tenant_user.user_id),
            "role": tenant_user.role
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tenants/{tenant_id}/users")
async def get_tenant_users(tenant_id: UUID):
    """Get all users in a tenant."""
    users = tenant_service.get_tenant_users(tenant_id)

    return {
        "count": len(users),
        "users": [
            {
                "id": str(u.id),
                "user_id": str(u.user_id),
                "role": u.role,
                "department": u.department
            }
            for u in users
        ]
    }


@router.get("/tenants/{tenant_id}/statistics")
async def get_tenant_statistics(tenant_id: UUID):
    """Get tenant usage statistics."""
    try:
        return tenant_service.get_tenant_statistics(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tenants/{tenant_id}/features")
async def enable_features(tenant_id: UUID, features: List[str]):
    """Enable features for a tenant."""
    try:
        tenant = tenant_service.enable_features(tenant_id, features)
        return {"features_enabled": tenant.features_enabled}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tenants")
async def list_tenants(
    tenant_type: Optional[str] = None,
    status: Optional[str] = None
):
    """List all tenants."""
    t_type = TenantType(tenant_type) if tenant_type else None
    t_status = TenantStatus(status) if status else None

    tenants = tenant_service.list_tenants(t_type, t_status)

    return {
        "count": len(tenants),
        "tenants": [
            {
                "id": str(t.id),
                "name": t.name,
                "slug": t.slug,
                "tenant_type": t.tenant_type.value,
                "status": t.status.value
            }
            for t in tenants
        ]
    }


# ============================================================================
# COMPLIANCE ENDPOINTS
# ============================================================================

@router.post("/compliance/audit")
async def log_audit_event(request: LogAuditRequest):
    """Log an audit event."""
    try:
        event_type = AuditEventType(request.event_type)
        severity = AuditSeverity(request.severity)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event type or severity")

    event = compliance_service.log_event(
        event_type=event_type,
        description=request.description,
        user_id=request.user_id,
        user_email=request.user_email,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        tenant_id=request.tenant_id,
        ip_address=request.ip_address,
        severity=severity,
        metadata=request.metadata
    )

    return {
        "id": str(event.id),
        "event_type": event.event_type.value,
        "timestamp": event.timestamp.isoformat()
    }


@router.get("/compliance/audit")
async def get_audit_trail(
    user_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    event_type: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
):
    """Get audit trail."""
    e_type = AuditEventType(event_type) if event_type else None

    events = compliance_service.get_audit_trail(
        user_id=user_id,
        resource_type=resource_type,
        event_type=e_type,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    return {
        "count": len(events),
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type.value,
                "severity": e.severity.value,
                "description": e.description,
                "user_id": str(e.user_id) if e.user_id else None,
                "timestamp": e.timestamp.isoformat()
            }
            for e in events
        ]
    }


@router.post("/compliance/consent")
async def record_consent(request: RecordConsentRequest):
    """Record user consent."""
    try:
        consent_type = ConsentType(request.consent_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid consent type")

    record = compliance_service.record_consent(
        user_id=request.user_id,
        consent_type=consent_type,
        granted=request.granted,
        version=request.version,
        ip_address=request.ip_address
    )

    return {
        "id": str(record.id),
        "consent_type": record.consent_type.value,
        "granted": record.granted
    }


@router.get("/compliance/consent/{user_id}")
async def get_user_consents(user_id: UUID):
    """Get all consent records for a user."""
    consents = compliance_service.get_user_consents(user_id)

    return {
        "user_id": str(user_id),
        "consents": [
            {
                "consent_type": c.consent_type.value,
                "granted": c.granted,
                "version": c.version,
                "timestamp": (c.granted_at or c.revoked_at).isoformat() if (c.granted_at or c.revoked_at) else None
            }
            for c in consents
        ]
    }


@router.get("/compliance/consent/{user_id}/check/{consent_type}")
async def check_consent(user_id: UUID, consent_type: str):
    """Check if user has granted specific consent."""
    try:
        c_type = ConsentType(consent_type)
        has_consent = compliance_service.check_consent(user_id, c_type)
        return {"has_consent": has_consent}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid consent type")


@router.get("/compliance/gdpr/export/{user_id}")
async def generate_gdpr_export(user_id: UUID):
    """Generate GDPR data export for a user."""
    return compliance_service.generate_gdpr_export(user_id)


@router.post("/compliance/gdpr/delete/{user_id}")
async def process_deletion_request(user_id: UUID, reason: str = "User request"):
    """Process GDPR deletion request."""
    return compliance_service.process_deletion_request(user_id, reason)


@router.get("/compliance/report")
async def generate_compliance_report(
    tenant_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Generate compliance report."""
    return compliance_service.generate_compliance_report(
        tenant_id,
        start_date,
        end_date
    )


@router.get("/compliance/retention-policies")
async def get_retention_policies():
    """Get all retention policies."""
    policies = list(compliance_service.retention_policies.values())

    return {
        "count": len(policies),
        "policies": [
            {
                "id": str(p.id),
                "data_type": p.data_type,
                "retention_days": p.retention_days,
                "auto_delete": p.auto_delete,
                "description": p.description
            }
            for p in policies
        ]
    }
