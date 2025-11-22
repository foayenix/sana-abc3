"""
Usage Tracking Service
======================
Tracks feature usage per user for enforcing tier limits.
"""

import logging
from typing import Dict, Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from collections import defaultdict

from .tier_limits import FeatureName, SubscriptionTier, TierLimitService

logger = logging.getLogger(__name__)


class UsageRecord(BaseModel):
    """Individual usage record"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    feature: FeatureName
    amount: int = 1
    metadata: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserUsageSummary(BaseModel):
    """Summary of user's usage"""
    user_id: UUID
    tier: SubscriptionTier
    period_start: datetime
    period_end: datetime
    usage: Dict[str, int] = Field(default_factory=dict)
    limits: Dict[str, int] = Field(default_factory=dict)


class UsageTrackingService:
    """
    Usage Tracking Service

    Tracks and manages feature usage:
    - Records usage events
    - Calculates period usage
    - Checks against limits
    - Generates usage reports
    """

    def __init__(self):
        self.tier_service = TierLimitService()
        # In-memory storage (would be database in production)
        self._usage_records: List[UsageRecord] = []
        self._user_tiers: Dict[UUID, SubscriptionTier] = {}

    def set_user_tier(self, user_id: UUID, tier: SubscriptionTier):
        """Set user's subscription tier"""
        self._user_tiers[user_id] = tier

    def get_user_tier(self, user_id: UUID) -> SubscriptionTier:
        """Get user's subscription tier"""
        return self._user_tiers.get(user_id, SubscriptionTier.FREE)

    def record_usage(
        self,
        user_id: UUID,
        feature: FeatureName,
        amount: int = 1,
        metadata: Optional[Dict] = None
    ) -> UsageRecord:
        """
        Record a usage event

        Args:
            user_id: User ID
            feature: Feature being used
            amount: Amount of usage (default 1)
            metadata: Optional metadata

        Returns:
            Created usage record
        """
        record = UsageRecord(
            user_id=user_id,
            feature=feature,
            amount=amount,
            metadata=metadata,
        )

        self._usage_records.append(record)
        logger.debug(f"Recorded usage: {user_id} - {feature.value} x {amount}")

        return record

    def get_period_usage(
        self,
        user_id: UUID,
        feature: FeatureName,
        period: str = "monthly"
    ) -> int:
        """
        Get usage for current period

        Args:
            user_id: User ID
            feature: Feature to check
            period: "monthly", "daily", or "total"

        Returns:
            Total usage for the period
        """
        now = datetime.utcnow()

        if period == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # total
            period_start = datetime.min

        total = sum(
            r.amount for r in self._usage_records
            if r.user_id == user_id
            and r.feature == feature
            and r.timestamp >= period_start
        )

        return total

    def check_can_use_feature(
        self,
        user_id: UUID,
        feature: FeatureName,
        amount: int = 1
    ) -> Dict:
        """
        Check if user can use a feature

        Args:
            user_id: User ID
            feature: Feature to check
            amount: Amount to use

        Returns:
            Dict with allowed status and details
        """
        tier = self.get_user_tier(user_id)
        limit_config = self.tier_service.get_feature_limit(tier, feature)

        if not limit_config:
            return {
                "allowed": False,
                "reason": "Feature not available for your tier",
                "upgrade_required": True,
            }

        # Unlimited check
        if limit_config.limit == -1:
            return {
                "allowed": True,
                "unlimited": True,
            }

        # Get current usage
        current_usage = self.get_period_usage(user_id, feature, limit_config.period)

        # Check if would exceed limit
        would_exceed = (current_usage + amount) > limit_config.limit

        result = {
            "allowed": not would_exceed,
            "current_usage": current_usage,
            "limit": limit_config.limit,
            "remaining": max(0, limit_config.limit - current_usage),
            "requested": amount,
        }

        if would_exceed:
            result["reason"] = f"Would exceed {feature.value} limit ({limit_config.limit}/{limit_config.period})"
            result["upgrade_required"] = True

        return result

    def use_feature(
        self,
        user_id: UUID,
        feature: FeatureName,
        amount: int = 1,
        force: bool = False
    ) -> Dict:
        """
        Attempt to use a feature (checks limit and records)

        Args:
            user_id: User ID
            feature: Feature to use
            amount: Amount to use
            force: Skip limit check (for admin)

        Returns:
            Result with success status
        """
        if not force:
            check = self.check_can_use_feature(user_id, feature, amount)
            if not check["allowed"]:
                return {
                    "success": False,
                    **check,
                }

        # Record usage
        self.record_usage(user_id, feature, amount)

        return {
            "success": True,
            "feature": feature.value,
            "amount": amount,
            "recorded_at": datetime.utcnow().isoformat(),
        }

    def get_usage_summary(self, user_id: UUID) -> UserUsageSummary:
        """
        Get complete usage summary for user

        Returns summary of all feature usage and limits.
        """
        tier = self.get_user_tier(user_id)
        tier_limits = self.tier_service.get_tier_limits(tier)

        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1)
        else:
            period_end = datetime(now.year, now.month + 1, 1)

        usage = {}
        limits = {}

        for feature in FeatureName:
            limit_config = tier_limits.get(feature)
            if limit_config:
                period = limit_config.period
                usage[feature.value] = self.get_period_usage(user_id, feature, period)
                limits[feature.value] = limit_config.limit

        return UserUsageSummary(
            user_id=user_id,
            tier=tier,
            period_start=period_start,
            period_end=period_end,
            usage=usage,
            limits=limits,
        )

    def get_feature_status(self, user_id: UUID, feature: FeatureName) -> Dict:
        """Get detailed status for a specific feature"""
        tier = self.get_user_tier(user_id)
        limit_config = self.tier_service.get_feature_limit(tier, feature)

        if not limit_config:
            return {
                "feature": feature.value,
                "available": False,
                "reason": "Not available for your tier",
            }

        current_usage = self.get_period_usage(user_id, feature, limit_config.period)

        if limit_config.limit == -1:
            return {
                "feature": feature.value,
                "available": True,
                "unlimited": True,
                "usage": current_usage,
            }

        remaining = limit_config.limit - current_usage
        percentage = (current_usage / limit_config.limit) * 100 if limit_config.limit > 0 else 0

        return {
            "feature": feature.value,
            "available": remaining > 0,
            "unlimited": False,
            "usage": current_usage,
            "limit": limit_config.limit,
            "remaining": max(0, remaining),
            "percentage_used": round(percentage, 1),
            "period": limit_config.period,
            "near_limit": percentage >= limit_config.soft_limit_percent,
            "at_limit": remaining <= 0,
        }

    def get_all_feature_status(self, user_id: UUID) -> Dict[str, Dict]:
        """Get status for all features"""
        return {
            feature.value: self.get_feature_status(user_id, feature)
            for feature in FeatureName
        }

    def reset_period_usage(self, user_id: UUID, feature: FeatureName):
        """Reset usage for a feature (for testing or admin)"""
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        self._usage_records = [
            r for r in self._usage_records
            if not (
                r.user_id == user_id
                and r.feature == feature
                and r.timestamp >= period_start
            )
        ]
