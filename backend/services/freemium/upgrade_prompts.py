"""
Upgrade Prompts Service
=======================
Generates contextual upgrade prompts and CTAs.
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from .tier_limits import SubscriptionTier, FeatureName, TierLimitService
from .usage_tracking import UsageTrackingService

logger = logging.getLogger(__name__)


# Pricing configuration
TIER_PRICING = {
    SubscriptionTier.FREE: {
        "price": 0,
        "currency": "GBP",
        "period": "month",
        "name": "Free",
        "description": "Get started with basic features",
    },
    SubscriptionTier.SANA_PLUS: {
        "price": 999,  # £9.99
        "currency": "GBP",
        "period": "month",
        "name": "SANA Plus",
        "description": "Unlimited scanning and premium features for clients",
    },
    SubscriptionTier.BASIC: {
        "price": 1900,  # £19
        "currency": "GBP",
        "period": "month",
        "name": "Basic",
        "description": "Essential tools for starting practitioners",
    },
    SubscriptionTier.PROFESSIONAL: {
        "price": 2900,  # £29
        "currency": "GBP",
        "period": "month",
        "name": "Professional",
        "description": "Full toolkit for growing practices",
    },
    SubscriptionTier.PREMIUM: {
        "price": 4900,  # £49
        "currency": "GBP",
        "period": "month",
        "name": "Premium",
        "description": "Advanced features for established practices",
    },
    SubscriptionTier.ENTERPRISE: {
        "price": None,  # Custom
        "currency": "GBP",
        "period": "month",
        "name": "Enterprise",
        "description": "Custom solutions for large organizations",
    },
}


class UpgradePromptService:
    """
    Upgrade Prompt Service

    Generates contextual upgrade prompts:
    - When approaching limits
    - When hitting limits
    - Feature-specific CTAs
    - Personalized recommendations
    """

    def __init__(self):
        self.tier_service = TierLimitService()
        self.usage_service = UsageTrackingService()

    def get_upgrade_prompt(
        self,
        user_id: UUID,
        context: str = "general",
        feature: Optional[FeatureName] = None
    ) -> Optional[Dict]:
        """
        Get contextual upgrade prompt

        Args:
            user_id: User ID
            context: Where the prompt will be shown
            feature: Specific feature that triggered the prompt

        Returns:
            Upgrade prompt data or None if not applicable
        """
        current_tier = self.usage_service.get_user_tier(user_id)

        # Don't show to premium/enterprise users
        if current_tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]:
            return None

        # Determine recommended tier
        recommended_tier = self._get_recommended_tier(user_id, current_tier)

        if not recommended_tier or recommended_tier == current_tier:
            return None

        # Get benefits
        benefits = self.tier_service.get_upgrade_benefits(current_tier, recommended_tier)

        # Get pricing
        pricing = TIER_PRICING.get(recommended_tier, {})

        # Generate prompt based on context
        prompt = self._generate_prompt(context, feature, current_tier, recommended_tier)

        return {
            "show_prompt": True,
            "current_tier": current_tier.value,
            "recommended_tier": recommended_tier.value,
            "prompt": prompt,
            "benefits": benefits["benefits"],
            "pricing": {
                "price": pricing.get("price"),
                "currency": pricing.get("currency"),
                "period": pricing.get("period"),
                "formatted": self._format_price(pricing),
            },
            "cta_text": self._get_cta_text(context),
            "cta_url": f"/upgrade?to={recommended_tier.value}",
        }

    def _get_recommended_tier(
        self,
        user_id: UUID,
        current_tier: SubscriptionTier
    ) -> Optional[SubscriptionTier]:
        """Determine recommended tier based on usage patterns"""
        tier_order = [
            SubscriptionTier.FREE,
            SubscriptionTier.SANA_PLUS,
            SubscriptionTier.BASIC,
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.PREMIUM,
        ]

        try:
            current_index = tier_order.index(current_tier)
        except ValueError:
            return None

        # Simple logic: recommend next tier
        if current_index < len(tier_order) - 1:
            return tier_order[current_index + 1]

        return None

    def _generate_prompt(
        self,
        context: str,
        feature: Optional[FeatureName],
        current_tier: SubscriptionTier,
        recommended_tier: SubscriptionTier
    ) -> Dict:
        """Generate prompt content based on context"""
        prompts = {
            "limit_reached": {
                "title": "You've reached your limit",
                "message": f"Upgrade to {TIER_PRICING[recommended_tier]['name']} for unlimited access",
                "urgency": "high",
            },
            "near_limit": {
                "title": "Running low on usage",
                "message": f"You're approaching your limit. Consider upgrading for more.",
                "urgency": "medium",
            },
            "feature_locked": {
                "title": "Premium Feature",
                "message": f"This feature is available with {TIER_PRICING[recommended_tier]['name']}",
                "urgency": "medium",
            },
            "general": {
                "title": "Unlock more features",
                "message": f"Get more from SANA with {TIER_PRICING[recommended_tier]['name']}",
                "urgency": "low",
            },
        }

        return prompts.get(context, prompts["general"])

    def _get_cta_text(self, context: str) -> str:
        """Get call-to-action text"""
        ctas = {
            "limit_reached": "Upgrade Now",
            "near_limit": "See Plans",
            "feature_locked": "Unlock Feature",
            "general": "View Plans",
        }
        return ctas.get(context, "View Plans")

    def _format_price(self, pricing: Dict) -> str:
        """Format price for display"""
        if pricing.get("price") is None:
            return "Custom pricing"

        price = pricing["price"] / 100  # Convert from pence
        currency = pricing.get("currency", "GBP")
        period = pricing.get("period", "month")

        symbol = "£" if currency == "GBP" else "$"
        return f"{symbol}{price:.2f}/{period}"

    def get_limit_warning(
        self,
        user_id: UUID,
        feature: FeatureName
    ) -> Optional[Dict]:
        """
        Get warning when approaching limit

        Returns warning info if near limit, None otherwise.
        """
        status = self.usage_service.get_feature_status(user_id, feature)

        if status.get("unlimited") or not status.get("near_limit"):
            return None

        if status.get("at_limit"):
            return {
                "type": "limit_reached",
                "feature": feature.value,
                "message": f"You've reached your {feature.value.replace('_', ' ')} limit",
                "remaining": 0,
                "upgrade_prompt": self.get_upgrade_prompt(user_id, "limit_reached", feature),
            }

        return {
            "type": "near_limit",
            "feature": feature.value,
            "message": f"You're at {status['percentage_used']:.0f}% of your {feature.value.replace('_', ' ')} limit",
            "remaining": status.get("remaining", 0),
            "upgrade_prompt": self.get_upgrade_prompt(user_id, "near_limit", feature),
        }

    def get_tier_comparison(self) -> Dict:
        """Get full tier comparison for pricing page"""
        comparison = self.tier_service.get_tier_comparison()

        # Add pricing info
        for tier_name, tier_data in comparison.items():
            try:
                tier_enum = SubscriptionTier(tier_name)
                pricing = TIER_PRICING.get(tier_enum, {})
                tier_data["pricing"] = {
                    "price": pricing.get("price"),
                    "currency": pricing.get("currency", "GBP"),
                    "period": pricing.get("period", "month"),
                    "formatted": self._format_price(pricing),
                }
                tier_data["description"] = pricing.get("description", "")
            except ValueError:
                pass

        return comparison

    def get_feature_gate_message(
        self,
        feature: FeatureName,
        required_tier: SubscriptionTier
    ) -> Dict:
        """Get message for gated feature"""
        pricing = TIER_PRICING.get(required_tier, {})

        return {
            "feature": feature.value,
            "required_tier": required_tier.value,
            "message": f"This feature requires {pricing.get('name', required_tier.value)}",
            "pricing": {
                "price": pricing.get("price"),
                "formatted": self._format_price(pricing),
            },
            "cta_text": "Unlock Feature",
            "cta_url": f"/upgrade?to={required_tier.value}&feature={feature.value}",
        }
