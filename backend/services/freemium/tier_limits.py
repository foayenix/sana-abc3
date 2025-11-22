"""
Tier Limits Service
===================
Defines and enforces tier-based feature limits.
"""

import logging
from typing import Dict, Optional
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SubscriptionTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    SANA_PLUS = "sana_plus"  # Client tier (£9.99/month)
    BASIC = "basic"  # Practitioner basic (£19/month)
    PROFESSIONAL = "professional"  # Practitioner pro (£29/month)
    PREMIUM = "premium"  # Practitioner premium (£49/month)
    ENTERPRISE = "enterprise"  # Custom


class FeatureName(str, Enum):
    """Features that can be limited"""
    # AI Features
    AI_GENERATIONS = "ai_generations"
    VOICE_TRANSCRIPTION_MINUTES = "voice_transcription_minutes"

    # Scanner Features
    PRODUCT_SCANS = "product_scans"

    # Practice Features
    CLIENT_RECORDS = "client_records"
    BOOKINGS = "bookings"
    MONTHLY_SESSIONS = "monthly_sessions"

    # Communication
    MESSAGES = "messages"

    # Storage
    FILE_STORAGE_MB = "file_storage_mb"


class TierLimit(BaseModel):
    """Limit configuration for a feature"""
    feature: FeatureName
    limit: int  # -1 for unlimited
    period: str = "monthly"  # "monthly", "daily", "total"
    soft_limit_percent: int = 80  # When to show warning


# Tier configurations
TIER_LIMITS: Dict[SubscriptionTier, Dict[FeatureName, TierLimit]] = {
    SubscriptionTier.FREE: {
        FeatureName.AI_GENERATIONS: TierLimit(feature=FeatureName.AI_GENERATIONS, limit=100),
        FeatureName.VOICE_TRANSCRIPTION_MINUTES: TierLimit(feature=FeatureName.VOICE_TRANSCRIPTION_MINUTES, limit=30),
        FeatureName.PRODUCT_SCANS: TierLimit(feature=FeatureName.PRODUCT_SCANS, limit=5),
        FeatureName.CLIENT_RECORDS: TierLimit(feature=FeatureName.CLIENT_RECORDS, limit=25, period="total"),
        FeatureName.BOOKINGS: TierLimit(feature=FeatureName.BOOKINGS, limit=20),
        FeatureName.MONTHLY_SESSIONS: TierLimit(feature=FeatureName.MONTHLY_SESSIONS, limit=20),
        FeatureName.MESSAGES: TierLimit(feature=FeatureName.MESSAGES, limit=100),
        FeatureName.FILE_STORAGE_MB: TierLimit(feature=FeatureName.FILE_STORAGE_MB, limit=100, period="total"),
    },
    SubscriptionTier.SANA_PLUS: {
        FeatureName.AI_GENERATIONS: TierLimit(feature=FeatureName.AI_GENERATIONS, limit=-1),
        FeatureName.VOICE_TRANSCRIPTION_MINUTES: TierLimit(feature=FeatureName.VOICE_TRANSCRIPTION_MINUTES, limit=-1),
        FeatureName.PRODUCT_SCANS: TierLimit(feature=FeatureName.PRODUCT_SCANS, limit=-1),
        FeatureName.CLIENT_RECORDS: TierLimit(feature=FeatureName.CLIENT_RECORDS, limit=-1, period="total"),
        FeatureName.BOOKINGS: TierLimit(feature=FeatureName.BOOKINGS, limit=-1),
        FeatureName.MONTHLY_SESSIONS: TierLimit(feature=FeatureName.MONTHLY_SESSIONS, limit=-1),
        FeatureName.MESSAGES: TierLimit(feature=FeatureName.MESSAGES, limit=-1),
        FeatureName.FILE_STORAGE_MB: TierLimit(feature=FeatureName.FILE_STORAGE_MB, limit=1000, period="total"),
    },
    SubscriptionTier.BASIC: {
        FeatureName.AI_GENERATIONS: TierLimit(feature=FeatureName.AI_GENERATIONS, limit=500),
        FeatureName.VOICE_TRANSCRIPTION_MINUTES: TierLimit(feature=FeatureName.VOICE_TRANSCRIPTION_MINUTES, limit=120),
        FeatureName.PRODUCT_SCANS: TierLimit(feature=FeatureName.PRODUCT_SCANS, limit=-1),
        FeatureName.CLIENT_RECORDS: TierLimit(feature=FeatureName.CLIENT_RECORDS, limit=100, period="total"),
        FeatureName.BOOKINGS: TierLimit(feature=FeatureName.BOOKINGS, limit=-1),
        FeatureName.MONTHLY_SESSIONS: TierLimit(feature=FeatureName.MONTHLY_SESSIONS, limit=100),
        FeatureName.MESSAGES: TierLimit(feature=FeatureName.MESSAGES, limit=-1),
        FeatureName.FILE_STORAGE_MB: TierLimit(feature=FeatureName.FILE_STORAGE_MB, limit=500, period="total"),
    },
    SubscriptionTier.PROFESSIONAL: {
        FeatureName.AI_GENERATIONS: TierLimit(feature=FeatureName.AI_GENERATIONS, limit=-1),
        FeatureName.VOICE_TRANSCRIPTION_MINUTES: TierLimit(feature=FeatureName.VOICE_TRANSCRIPTION_MINUTES, limit=-1),
        FeatureName.PRODUCT_SCANS: TierLimit(feature=FeatureName.PRODUCT_SCANS, limit=-1),
        FeatureName.CLIENT_RECORDS: TierLimit(feature=FeatureName.CLIENT_RECORDS, limit=-1, period="total"),
        FeatureName.BOOKINGS: TierLimit(feature=FeatureName.BOOKINGS, limit=-1),
        FeatureName.MONTHLY_SESSIONS: TierLimit(feature=FeatureName.MONTHLY_SESSIONS, limit=-1),
        FeatureName.MESSAGES: TierLimit(feature=FeatureName.MESSAGES, limit=-1),
        FeatureName.FILE_STORAGE_MB: TierLimit(feature=FeatureName.FILE_STORAGE_MB, limit=2000, period="total"),
    },
    SubscriptionTier.PREMIUM: {
        FeatureName.AI_GENERATIONS: TierLimit(feature=FeatureName.AI_GENERATIONS, limit=-1),
        FeatureName.VOICE_TRANSCRIPTION_MINUTES: TierLimit(feature=FeatureName.VOICE_TRANSCRIPTION_MINUTES, limit=-1),
        FeatureName.PRODUCT_SCANS: TierLimit(feature=FeatureName.PRODUCT_SCANS, limit=-1),
        FeatureName.CLIENT_RECORDS: TierLimit(feature=FeatureName.CLIENT_RECORDS, limit=-1, period="total"),
        FeatureName.BOOKINGS: TierLimit(feature=FeatureName.BOOKINGS, limit=-1),
        FeatureName.MONTHLY_SESSIONS: TierLimit(feature=FeatureName.MONTHLY_SESSIONS, limit=-1),
        FeatureName.MESSAGES: TierLimit(feature=FeatureName.MESSAGES, limit=-1),
        FeatureName.FILE_STORAGE_MB: TierLimit(feature=FeatureName.FILE_STORAGE_MB, limit=10000, period="total"),
    },
    SubscriptionTier.ENTERPRISE: {
        FeatureName.AI_GENERATIONS: TierLimit(feature=FeatureName.AI_GENERATIONS, limit=-1),
        FeatureName.VOICE_TRANSCRIPTION_MINUTES: TierLimit(feature=FeatureName.VOICE_TRANSCRIPTION_MINUTES, limit=-1),
        FeatureName.PRODUCT_SCANS: TierLimit(feature=FeatureName.PRODUCT_SCANS, limit=-1),
        FeatureName.CLIENT_RECORDS: TierLimit(feature=FeatureName.CLIENT_RECORDS, limit=-1, period="total"),
        FeatureName.BOOKINGS: TierLimit(feature=FeatureName.BOOKINGS, limit=-1),
        FeatureName.MONTHLY_SESSIONS: TierLimit(feature=FeatureName.MONTHLY_SESSIONS, limit=-1),
        FeatureName.MESSAGES: TierLimit(feature=FeatureName.MESSAGES, limit=-1),
        FeatureName.FILE_STORAGE_MB: TierLimit(feature=FeatureName.FILE_STORAGE_MB, limit=-1, period="total"),
    },
}


class TierLimitService:
    """
    Tier Limit Service

    Manages feature limits based on subscription tier.
    """

    def __init__(self):
        self.tier_limits = TIER_LIMITS

    def get_tier_limits(self, tier: SubscriptionTier) -> Dict[FeatureName, TierLimit]:
        """Get all limits for a tier"""
        return self.tier_limits.get(tier, self.tier_limits[SubscriptionTier.FREE])

    def get_feature_limit(
        self,
        tier: SubscriptionTier,
        feature: FeatureName
    ) -> TierLimit:
        """Get limit for a specific feature"""
        tier_limits = self.get_tier_limits(tier)
        return tier_limits.get(feature)

    def is_unlimited(self, tier: SubscriptionTier, feature: FeatureName) -> bool:
        """Check if feature is unlimited for tier"""
        limit = self.get_feature_limit(tier, feature)
        return limit and limit.limit == -1

    def get_limit_value(self, tier: SubscriptionTier, feature: FeatureName) -> int:
        """Get the numeric limit value"""
        limit = self.get_feature_limit(tier, feature)
        return limit.limit if limit else 0

    def get_soft_limit_threshold(
        self,
        tier: SubscriptionTier,
        feature: FeatureName
    ) -> Optional[int]:
        """Get threshold for showing warning"""
        limit = self.get_feature_limit(tier, feature)
        if not limit or limit.limit == -1:
            return None
        return int(limit.limit * (limit.soft_limit_percent / 100))

    def check_limit(
        self,
        tier: SubscriptionTier,
        feature: FeatureName,
        current_usage: int
    ) -> Dict:
        """
        Check if usage is within limits

        Returns:
            Dict with limit status and details
        """
        limit = self.get_feature_limit(tier, feature)

        if not limit:
            return {
                "allowed": False,
                "reason": "Feature not available",
            }

        # Unlimited
        if limit.limit == -1:
            return {
                "allowed": True,
                "unlimited": True,
                "usage": current_usage,
            }

        # Check if at or over limit
        at_limit = current_usage >= limit.limit
        near_limit = current_usage >= (limit.limit * limit.soft_limit_percent / 100)

        return {
            "allowed": not at_limit,
            "unlimited": False,
            "usage": current_usage,
            "limit": limit.limit,
            "remaining": max(0, limit.limit - current_usage),
            "percentage_used": min(100, (current_usage / limit.limit) * 100) if limit.limit > 0 else 0,
            "near_limit": near_limit,
            "at_limit": at_limit,
            "period": limit.period,
        }

    def get_tier_comparison(self) -> Dict:
        """Get comparison of all tiers for upgrade pages"""
        comparison = {}

        for tier in SubscriptionTier:
            tier_data = {
                "name": tier.value.replace("_", " ").title(),
                "features": {},
            }

            for feature in FeatureName:
                limit = self.get_feature_limit(tier, feature)
                if limit:
                    tier_data["features"][feature.value] = {
                        "limit": "Unlimited" if limit.limit == -1 else limit.limit,
                        "period": limit.period,
                    }

            comparison[tier.value] = tier_data

        return comparison

    def get_upgrade_benefits(
        self,
        current_tier: SubscriptionTier,
        target_tier: SubscriptionTier
    ) -> Dict:
        """Get benefits of upgrading to a higher tier"""
        current_limits = self.get_tier_limits(current_tier)
        target_limits = self.get_tier_limits(target_tier)

        benefits = []

        for feature in FeatureName:
            current = current_limits.get(feature)
            target = target_limits.get(feature)

            if not current or not target:
                continue

            if target.limit == -1 and current.limit != -1:
                benefits.append({
                    "feature": feature.value,
                    "improvement": f"Unlimited {feature.value.replace('_', ' ')}",
                })
            elif target.limit > current.limit and current.limit != -1:
                increase = target.limit - current.limit
                benefits.append({
                    "feature": feature.value,
                    "improvement": f"+{increase} {feature.value.replace('_', ' ')}",
                    "new_limit": target.limit,
                })

        return {
            "from_tier": current_tier.value,
            "to_tier": target_tier.value,
            "benefits": benefits,
        }
