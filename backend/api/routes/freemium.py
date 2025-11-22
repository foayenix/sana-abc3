"""
Freemium API Routes
===================
API endpoints for usage tracking, limits, and upgrade prompts.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from services.freemium import (
    UsageTrackingService,
    TierLimitService,
    UpgradePromptService,
)
from services.freemium.tier_limits import SubscriptionTier, FeatureName

router = APIRouter()

# Initialize services
usage_service = UsageTrackingService()
tier_service = TierLimitService()
upgrade_service = UpgradePromptService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class TrackUsageRequest(BaseModel):
    feature: str
    amount: int = Field(default=1, ge=1)


class SetTierRequest(BaseModel):
    tier: str


# ============================================================================
# USAGE ENDPOINTS
# ============================================================================

@router.get("/usage/{user_id}", summary="Get usage summary")
async def get_usage_summary(user_id: UUID):
    """
    Get complete usage summary for a user.

    Returns current usage for all features and limits.
    """
    summary = usage_service.get_usage_summary(user_id)

    return {
        "user_id": str(summary.user_id),
        "tier": summary.tier.value,
        "period": {
            "start": summary.period_start.isoformat(),
            "end": summary.period_end.isoformat(),
        },
        "usage": summary.usage,
        "limits": {
            k: "unlimited" if v == -1 else v
            for k, v in summary.limits.items()
        },
    }


@router.get("/usage/{user_id}/feature/{feature}", summary="Get feature usage")
async def get_feature_usage(user_id: UUID, feature: str):
    """
    Get detailed usage for a specific feature.

    Returns current usage, limit, and status.
    """
    try:
        feature_enum = FeatureName(feature)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")

    status = usage_service.get_feature_status(user_id, feature_enum)
    return status


@router.post("/usage/{user_id}/track", summary="Track feature usage")
async def track_usage(user_id: UUID, request: TrackUsageRequest):
    """
    Record feature usage for a user.

    Will fail if usage would exceed limit.
    """
    try:
        feature_enum = FeatureName(request.feature)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {request.feature}")

    result = usage_service.use_feature(user_id, feature_enum, request.amount)

    if not result["success"]:
        raise HTTPException(
            status_code=429,
            detail={
                "message": result.get("reason", "Usage limit exceeded"),
                "limit": result.get("limit"),
                "usage": result.get("current_usage"),
                "upgrade_required": result.get("upgrade_required", True),
            }
        )

    return result


@router.get("/usage/{user_id}/check/{feature}", summary="Check if can use feature")
async def check_feature_usage(
    user_id: UUID,
    feature: str,
    amount: int = Query(default=1, ge=1)
):
    """
    Check if user can use a feature without recording usage.

    Useful for pre-validation before expensive operations.
    """
    try:
        feature_enum = FeatureName(feature)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")

    result = usage_service.check_can_use_feature(user_id, feature_enum, amount)
    return result


# ============================================================================
# LIMITS ENDPOINTS
# ============================================================================

@router.get("/limits", summary="Get all tier limits")
async def get_all_limits():
    """Get limits for all tiers (for comparison pages)"""
    return tier_service.get_tier_comparison()


@router.get("/limits/{tier}", summary="Get tier limits")
async def get_tier_limits(tier: str):
    """Get limits for a specific tier"""
    try:
        tier_enum = SubscriptionTier(tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

    limits = tier_service.get_tier_limits(tier_enum)

    return {
        "tier": tier,
        "limits": {
            feature.value: {
                "limit": "unlimited" if limit.limit == -1 else limit.limit,
                "period": limit.period,
            }
            for feature, limit in limits.items()
        }
    }


@router.get("/limits/feature/{feature}", summary="Get feature limits by tier")
async def get_feature_limits(feature: str):
    """Get limits for a specific feature across all tiers"""
    try:
        feature_enum = FeatureName(feature)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")

    result = {}
    for tier in SubscriptionTier:
        limit = tier_service.get_feature_limit(tier, feature_enum)
        if limit:
            result[tier.value] = {
                "limit": "unlimited" if limit.limit == -1 else limit.limit,
                "period": limit.period,
            }

    return {
        "feature": feature,
        "limits_by_tier": result,
    }


# ============================================================================
# UPGRADE ENDPOINTS
# ============================================================================

@router.get("/upgrade-prompt/{user_id}", summary="Get upgrade prompt")
async def get_upgrade_prompt(
    user_id: UUID,
    context: str = Query(default="general"),
    feature: Optional[str] = None,
):
    """
    Get contextual upgrade prompt for a user.

    Contexts:
    - general: Generic upgrade prompt
    - limit_reached: When user hits a limit
    - near_limit: When approaching limit
    - feature_locked: When accessing locked feature
    """
    feature_enum = None
    if feature:
        try:
            feature_enum = FeatureName(feature)
        except ValueError:
            pass

    prompt = upgrade_service.get_upgrade_prompt(user_id, context, feature_enum)

    if not prompt:
        return {"show_prompt": False}

    return prompt


@router.get("/upgrade-benefits/{user_id}", summary="Get upgrade benefits")
async def get_upgrade_benefits(
    user_id: UUID,
    target_tier: str = Query(..., description="Tier to upgrade to"),
):
    """Get benefits of upgrading to a specific tier"""
    current_tier = usage_service.get_user_tier(user_id)

    try:
        target_tier_enum = SubscriptionTier(target_tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {target_tier}")

    benefits = tier_service.get_upgrade_benefits(current_tier, target_tier_enum)
    return benefits


@router.get("/pricing", summary="Get pricing information")
async def get_pricing():
    """Get pricing for all tiers"""
    return upgrade_service.get_tier_comparison()


@router.get("/warning/{user_id}/{feature}", summary="Get limit warning")
async def get_limit_warning(user_id: UUID, feature: str):
    """
    Get warning if user is near or at limit.

    Returns warning details or null if not near limit.
    """
    try:
        feature_enum = FeatureName(feature)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")

    warning = upgrade_service.get_limit_warning(user_id, feature_enum)
    return warning or {"warning": None}


# ============================================================================
# TIER MANAGEMENT (Admin)
# ============================================================================

@router.post("/tier/{user_id}", summary="Set user tier (admin)")
async def set_user_tier(user_id: UUID, request: SetTierRequest):
    """Set user's subscription tier (admin endpoint)"""
    try:
        tier_enum = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}")

    usage_service.set_user_tier(user_id, tier_enum)

    return {
        "success": True,
        "user_id": str(user_id),
        "tier": tier_enum.value,
    }


@router.get("/tier/{user_id}", summary="Get user tier")
async def get_user_tier(user_id: UUID):
    """Get user's current tier"""
    tier = usage_service.get_user_tier(user_id)
    return {
        "user_id": str(user_id),
        "tier": tier.value,
    }


# ============================================================================
# INFO ENDPOINTS
# ============================================================================

@router.get("/features", summary="List all features")
async def list_features():
    """Get list of all tracked features"""
    return {
        "features": [
            {
                "name": f.value,
                "display_name": f.value.replace("_", " ").title(),
            }
            for f in FeatureName
        ]
    }


@router.get("/tiers", summary="List all tiers")
async def list_tiers():
    """Get list of all subscription tiers"""
    from services.freemium.upgrade_prompts import TIER_PRICING

    return {
        "tiers": [
            {
                "name": t.value,
                "display_name": t.value.replace("_", " ").title(),
                "price": TIER_PRICING.get(t, {}).get("price"),
                "description": TIER_PRICING.get(t, {}).get("description"),
            }
            for t in SubscriptionTier
        ]
    }
