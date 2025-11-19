"""
Multi-tenant service for enterprise deployments.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TenantType(str, Enum):
    """Types of tenants."""
    CORPORATE = "corporate"
    CLINIC = "clinic"
    NHS_TRUST = "nhs_trust"
    UNIVERSITY = "university"
    INSURANCE = "insurance"


class TenantStatus(str, Enum):
    """Tenant status."""
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class SSOProvider(str, Enum):
    """SSO providers."""
    SAML = "saml"
    OIDC = "oidc"
    AZURE_AD = "azure_ad"
    OKTA = "okta"
    NHS_LOGIN = "nhs_login"


class Tenant(BaseModel):
    """An enterprise tenant."""
    id: UUID
    name: str
    slug: str  # URL-safe identifier
    tenant_type: TenantType
    status: TenantStatus = TenantStatus.TRIAL

    # Contact
    admin_email: str
    billing_email: Optional[str] = None

    # Branding
    logo_url: Optional[str] = None
    primary_color: str = "#6366f1"
    secondary_color: str = "#8b5cf6"
    custom_domain: Optional[str] = None

    # SSO Configuration
    sso_enabled: bool = False
    sso_provider: Optional[SSOProvider] = None
    sso_config: Dict[str, Any] = {}

    # Limits
    max_users: int = 100
    max_practitioners: int = 10

    # Features
    features_enabled: List[str] = []

    # Metadata
    created_at: datetime
    updated_at: datetime


class TenantUser(BaseModel):
    """A user belonging to a tenant."""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    role: str = "member"  # admin, manager, member
    department: Optional[str] = None
    employee_id: Optional[str] = None
    joined_at: datetime


class MultiTenantService:
    """
    Multi-tenant management for enterprise deployments.

    Features:
    - Tenant provisioning
    - User management
    - SSO configuration
    - Custom branding
    - Feature gating
    """

    def __init__(self):
        self.tenants: Dict[UUID, Tenant] = {}
        self.tenant_users: Dict[UUID, TenantUser] = {}
        self.slug_to_id: Dict[str, UUID] = {}
        logger.info("MultiTenantService initialized")

    def create_tenant(
        self,
        name: str,
        tenant_type: TenantType,
        admin_email: str,
        slug: Optional[str] = None,
        max_users: int = 100,
        max_practitioners: int = 10
    ) -> Tenant:
        """
        Create a new tenant.

        Args:
            name: Organization name
            tenant_type: Type of tenant
            admin_email: Admin contact email
            slug: URL-safe identifier (generated if not provided)
            max_users: Maximum users allowed
            max_practitioners: Maximum practitioners allowed

        Returns:
            Created tenant
        """
        # Generate slug if not provided
        if not slug:
            slug = name.lower().replace(" ", "-").replace("'", "")[:50]

        # Ensure unique slug
        if slug in self.slug_to_id:
            slug = f"{slug}-{uuid4().hex[:6]}"

        now = datetime.utcnow()

        tenant = Tenant(
            id=uuid4(),
            name=name,
            slug=slug,
            tenant_type=tenant_type,
            admin_email=admin_email,
            max_users=max_users,
            max_practitioners=max_practitioners,
            created_at=now,
            updated_at=now
        )

        self.tenants[tenant.id] = tenant
        self.slug_to_id[slug] = tenant.id

        logger.info(f"Created tenant {name} ({slug})")

        return tenant

    def get_tenant(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        tenant_id = self.slug_to_id.get(slug)
        if tenant_id:
            return self.tenants.get(tenant_id)
        return None

    def update_tenant(
        self,
        tenant_id: UUID,
        updates: Dict[str, Any]
    ) -> Tenant:
        """Update tenant settings."""
        if tenant_id not in self.tenants:
            raise ValueError("Tenant not found")

        tenant = self.tenants[tenant_id]

        for key, value in updates.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        tenant.updated_at = datetime.utcnow()
        return tenant

    def configure_sso(
        self,
        tenant_id: UUID,
        provider: SSOProvider,
        config: Dict[str, Any]
    ) -> Tenant:
        """
        Configure SSO for a tenant.

        Args:
            tenant_id: Tenant ID
            provider: SSO provider
            config: Provider-specific configuration

        Returns:
            Updated tenant
        """
        if tenant_id not in self.tenants:
            raise ValueError("Tenant not found")

        tenant = self.tenants[tenant_id]
        tenant.sso_enabled = True
        tenant.sso_provider = provider
        tenant.sso_config = config
        tenant.updated_at = datetime.utcnow()

        logger.info(f"Configured {provider.value} SSO for tenant {tenant.name}")

        return tenant

    def set_branding(
        self,
        tenant_id: UUID,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        custom_domain: Optional[str] = None
    ) -> Tenant:
        """Set custom branding for tenant."""
        if tenant_id not in self.tenants:
            raise ValueError("Tenant not found")

        tenant = self.tenants[tenant_id]

        if logo_url:
            tenant.logo_url = logo_url
        if primary_color:
            tenant.primary_color = primary_color
        if secondary_color:
            tenant.secondary_color = secondary_color
        if custom_domain:
            tenant.custom_domain = custom_domain

        tenant.updated_at = datetime.utcnow()
        return tenant

    def add_user_to_tenant(
        self,
        tenant_id: UUID,
        user_id: UUID,
        role: str = "member",
        department: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> TenantUser:
        """Add a user to a tenant."""
        if tenant_id not in self.tenants:
            raise ValueError("Tenant not found")

        tenant = self.tenants[tenant_id]

        # Check user limit
        current_users = len([
            u for u in self.tenant_users.values()
            if u.tenant_id == tenant_id
        ])

        if current_users >= tenant.max_users:
            raise ValueError("Tenant user limit reached")

        tenant_user = TenantUser(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            department=department,
            employee_id=employee_id,
            joined_at=datetime.utcnow()
        )

        self.tenant_users[tenant_user.id] = tenant_user

        logger.info(f"Added user {user_id} to tenant {tenant.name}")

        return tenant_user

    def remove_user_from_tenant(self, tenant_user_id: UUID) -> bool:
        """Remove a user from a tenant."""
        if tenant_user_id in self.tenant_users:
            del self.tenant_users[tenant_user_id]
            return True
        return False

    def get_tenant_users(self, tenant_id: UUID) -> List[TenantUser]:
        """Get all users in a tenant."""
        return [
            u for u in self.tenant_users.values()
            if u.tenant_id == tenant_id
        ]

    def get_user_tenant(self, user_id: UUID) -> Optional[Tenant]:
        """Get the tenant a user belongs to."""
        for tenant_user in self.tenant_users.values():
            if tenant_user.user_id == user_id:
                return self.tenants.get(tenant_user.tenant_id)
        return None

    def enable_features(self, tenant_id: UUID, features: List[str]) -> Tenant:
        """Enable features for a tenant."""
        if tenant_id not in self.tenants:
            raise ValueError("Tenant not found")

        tenant = self.tenants[tenant_id]
        tenant.features_enabled = list(set(tenant.features_enabled + features))
        tenant.updated_at = datetime.utcnow()

        return tenant

    def check_feature_access(self, tenant_id: UUID, feature: str) -> bool:
        """Check if tenant has access to a feature."""
        if tenant_id not in self.tenants:
            return False

        tenant = self.tenants[tenant_id]
        return feature in tenant.features_enabled

    def get_tenant_statistics(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get usage statistics for a tenant."""
        if tenant_id not in self.tenants:
            raise ValueError("Tenant not found")

        tenant = self.tenants[tenant_id]
        users = self.get_tenant_users(tenant_id)

        by_role = {}
        by_department = {}

        for user in users:
            by_role[user.role] = by_role.get(user.role, 0) + 1
            if user.department:
                by_department[user.department] = by_department.get(user.department, 0) + 1

        return {
            "tenant_id": str(tenant_id),
            "tenant_name": tenant.name,
            "total_users": len(users),
            "max_users": tenant.max_users,
            "utilization": len(users) / tenant.max_users if tenant.max_users > 0 else 0,
            "by_role": by_role,
            "by_department": by_department,
            "features_enabled": tenant.features_enabled,
            "sso_enabled": tenant.sso_enabled
        }

    def list_tenants(
        self,
        tenant_type: Optional[TenantType] = None,
        status: Optional[TenantStatus] = None
    ) -> List[Tenant]:
        """List all tenants with optional filtering."""
        tenants = list(self.tenants.values())

        if tenant_type:
            tenants = [t for t in tenants if t.tenant_type == tenant_type]

        if status:
            tenants = [t for t in tenants if t.status == status]

        return tenants
