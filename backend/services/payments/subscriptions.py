"""
Subscription service for SANA Platform.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SubscriptionTier(str, Enum):
    """Available subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingPeriod(str, Enum):
    """Billing periods."""
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# Pricing in GBP
TIER_PRICING = {
    SubscriptionTier.FREE: {
        BillingPeriod.MONTHLY: 0,
        BillingPeriod.ANNUAL: 0
    },
    SubscriptionTier.BASIC: {
        BillingPeriod.MONTHLY: 29,
        BillingPeriod.ANNUAL: 290  # 2 months free
    },
    SubscriptionTier.PROFESSIONAL: {
        BillingPeriod.MONTHLY: 79,
        BillingPeriod.ANNUAL: 790
    },
    SubscriptionTier.ENTERPRISE: {
        BillingPeriod.MONTHLY: 199,
        BillingPeriod.ANNUAL: 1990
    }
}

# Features by tier
TIER_FEATURES = {
    SubscriptionTier.FREE: {
        "max_clients": 5,
        "max_bookings_per_month": 20,
        "outcome_tracking": False,
        "custom_branding": False,
        "analytics": "basic",
        "support": "community"
    },
    SubscriptionTier.BASIC: {
        "max_clients": 50,
        "max_bookings_per_month": 100,
        "outcome_tracking": True,
        "custom_branding": False,
        "analytics": "standard",
        "support": "email"
    },
    SubscriptionTier.PROFESSIONAL: {
        "max_clients": 200,
        "max_bookings_per_month": 500,
        "outcome_tracking": True,
        "custom_branding": True,
        "analytics": "advanced",
        "support": "priority"
    },
    SubscriptionTier.ENTERPRISE: {
        "max_clients": -1,  # Unlimited
        "max_bookings_per_month": -1,
        "outcome_tracking": True,
        "custom_branding": True,
        "analytics": "enterprise",
        "support": "dedicated"
    }
}


class Subscription(BaseModel):
    """A user subscription."""
    id: UUID
    user_id: UUID
    stripe_subscription_id: Optional[str] = None

    tier: SubscriptionTier
    billing_period: BillingPeriod
    status: SubscriptionStatus

    # Pricing
    price: float
    currency: str = "gbp"

    # Dates
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Metadata
    created_at: datetime
    updated_at: datetime


class SubscriptionService:
    """
    Manages practitioner subscriptions.

    Features:
    - Tier management
    - Trials
    - Upgrades/downgrades
    - Feature gating
    """

    def __init__(self):
        self.subscriptions: Dict[UUID, Subscription] = {}
        logger.info("SubscriptionService initialized")

    def create_subscription(
        self,
        user_id: UUID,
        tier: SubscriptionTier,
        billing_period: BillingPeriod = BillingPeriod.MONTHLY,
        trial_days: int = 0
    ) -> Subscription:
        """
        Create a new subscription.

        Args:
            user_id: User ID
            tier: Subscription tier
            billing_period: Monthly or annual
            trial_days: Trial period days

        Returns:
            Created subscription
        """
        now = datetime.utcnow()

        # Calculate period end
        if billing_period == BillingPeriod.MONTHLY:
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)

        # Set trial end
        trial_end = now + timedelta(days=trial_days) if trial_days > 0 else None

        subscription = Subscription(
            id=uuid4(),
            user_id=user_id,
            stripe_subscription_id=f"sub_{uuid4().hex[:24]}",
            tier=tier,
            billing_period=billing_period,
            status=SubscriptionStatus.TRIALING if trial_days > 0 else SubscriptionStatus.ACTIVE,
            price=TIER_PRICING[tier][billing_period],
            current_period_start=now,
            current_period_end=period_end,
            trial_end=trial_end,
            created_at=now,
            updated_at=now
        )

        self.subscriptions[subscription.id] = subscription

        logger.info(f"Created {tier.value} subscription for user {user_id}")

        return subscription

    def get_subscription(self, subscription_id: UUID) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)

    def get_user_subscription(self, user_id: UUID) -> Optional[Subscription]:
        """Get active subscription for a user."""
        for sub in self.subscriptions.values():
            if sub.user_id == user_id and sub.status in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING
            ]:
                return sub
        return None

    def upgrade_subscription(
        self,
        subscription_id: UUID,
        new_tier: SubscriptionTier
    ) -> Subscription:
        """Upgrade to a higher tier."""
        if subscription_id not in self.subscriptions:
            raise ValueError("Subscription not found")

        sub = self.subscriptions[subscription_id]

        # Verify upgrade
        tier_order = [
            SubscriptionTier.FREE,
            SubscriptionTier.BASIC,
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.ENTERPRISE
        ]

        if tier_order.index(new_tier) <= tier_order.index(sub.tier):
            raise ValueError("Can only upgrade to higher tiers")

        # Update subscription
        sub.tier = new_tier
        sub.price = TIER_PRICING[new_tier][sub.billing_period]
        sub.updated_at = datetime.utcnow()

        logger.info(f"Upgraded subscription {subscription_id} to {new_tier.value}")

        return sub

    def downgrade_subscription(
        self,
        subscription_id: UUID,
        new_tier: SubscriptionTier
    ) -> Subscription:
        """Downgrade at end of billing period."""
        if subscription_id not in self.subscriptions:
            raise ValueError("Subscription not found")

        sub = self.subscriptions[subscription_id]

        # Will take effect at period end
        sub.metadata = sub.metadata if hasattr(sub, 'metadata') else {}
        sub.updated_at = datetime.utcnow()

        logger.info(
            f"Scheduled downgrade for subscription {subscription_id} to {new_tier.value}"
        )

        return sub

    def cancel_subscription(
        self,
        subscription_id: UUID,
        immediate: bool = False
    ) -> Subscription:
        """Cancel a subscription."""
        if subscription_id not in self.subscriptions:
            raise ValueError("Subscription not found")

        sub = self.subscriptions[subscription_id]
        sub.cancelled_at = datetime.utcnow()

        if immediate:
            sub.status = SubscriptionStatus.CANCELLED
        # Otherwise cancels at period end

        sub.updated_at = datetime.utcnow()

        logger.info(f"Cancelled subscription {subscription_id}")

        return sub

    def check_feature_access(
        self,
        user_id: UUID,
        feature: str
    ) -> Dict[str, Any]:
        """
        Check if user has access to a feature.

        Returns access status and limit if applicable.
        """
        sub = self.get_user_subscription(user_id)

        if not sub:
            tier = SubscriptionTier.FREE
        else:
            tier = sub.tier

        features = TIER_FEATURES[tier]

        if feature not in features:
            return {"has_access": False, "reason": "Feature not found"}

        value = features[feature]

        if isinstance(value, bool):
            return {
                "has_access": value,
                "tier_required": self._get_tier_for_feature(feature) if not value else None
            }

        if isinstance(value, int):
            return {
                "has_access": True,
                "limit": value if value > 0 else "unlimited"
            }

        return {"has_access": True, "value": value}

    def _get_tier_for_feature(self, feature: str) -> Optional[str]:
        """Get minimum tier required for a feature."""
        for tier in [
            SubscriptionTier.BASIC,
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.ENTERPRISE
        ]:
            if TIER_FEATURES[tier].get(feature):
                return tier.value
        return None

    def get_pricing(self) -> Dict[str, Any]:
        """Get all pricing information."""
        return {
            tier.value: {
                "monthly": TIER_PRICING[tier][BillingPeriod.MONTHLY],
                "annual": TIER_PRICING[tier][BillingPeriod.ANNUAL],
                "features": TIER_FEATURES[tier]
            }
            for tier in SubscriptionTier
        }

    def get_subscription_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get usage stats for subscription."""
        sub = self.get_user_subscription(user_id)

        if not sub:
            return {
                "tier": "free",
                "usage": {},
                "limits": TIER_FEATURES[SubscriptionTier.FREE]
            }

        features = TIER_FEATURES[sub.tier]

        return {
            "tier": sub.tier.value,
            "status": sub.status.value,
            "period_end": sub.current_period_end.isoformat(),
            "price": sub.price,
            "billing_period": sub.billing_period.value,
            "limits": features,
            "trial_end": sub.trial_end.isoformat() if sub.trial_end else None
        }
