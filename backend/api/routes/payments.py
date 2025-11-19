"""
Payment API routes for SANA Platform.

Endpoints for payments, subscriptions, and payouts.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.payments.stripe_service import StripePaymentService, PaymentType, PaymentStatus
from services.payments.subscriptions import SubscriptionService, SubscriptionTier, BillingPeriod
from services.payments.payouts import PayoutService, PayoutSchedule

router = APIRouter()

# Initialize services
payment_service = StripePaymentService()
subscription_service = SubscriptionService()
payout_service = PayoutService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreatePaymentRequest(BaseModel):
    """Create a payment intent."""
    client_id: UUID
    amount: float
    currency: str = "gbp"
    payment_type: str = "booking"
    description: str = ""
    practitioner_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None


class ConfirmPaymentRequest(BaseModel):
    """Confirm a payment."""
    payment_method_id: str


class RefundRequest(BaseModel):
    """Request a refund."""
    amount: Optional[float] = None
    reason: str = ""


class CreateSubscriptionRequest(BaseModel):
    """Create a subscription."""
    user_id: UUID
    tier: str
    billing_period: str = "monthly"
    trial_days: int = 14


class CreateConnectAccountRequest(BaseModel):
    """Create Stripe Connect account."""
    practitioner_id: UUID
    email: str


class SetPayoutScheduleRequest(BaseModel):
    """Set payout schedule."""
    schedule: str  # daily, weekly, monthly, manual


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/create-intent")
async def create_payment_intent(request: CreatePaymentRequest):
    """Create a payment intent for checkout."""
    try:
        payment_type = PaymentType(request.payment_type)
    except ValueError:
        payment_type = PaymentType.BOOKING

    result = payment_service.create_payment_intent(
        client_id=request.client_id,
        amount=request.amount,
        currency=request.currency,
        payment_type=payment_type,
        description=request.description,
        practitioner_id=request.practitioner_id,
        booking_id=request.booking_id
    )

    return result


@router.post("/{payment_id}/confirm")
async def confirm_payment(payment_id: UUID, request: ConfirmPaymentRequest):
    """Confirm a payment."""
    try:
        payment = payment_service.confirm_payment(
            payment_id,
            request.payment_method_id
        )

        # Add to practitioner balance
        if payment.practitioner_id:
            payout_service.add_to_balance(
                payment.practitioner_id,
                payment.practitioner_payout,
                payment.id
            )

        return {
            "payment_id": str(payment.id),
            "status": payment.status.value,
            "completed_at": payment.completed_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/refund")
async def refund_payment(payment_id: UUID, request: RefundRequest):
    """Refund a payment."""
    try:
        result = payment_service.refund_payment(
            payment_id,
            request.amount,
            request.reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}")
async def get_payment(payment_id: UUID):
    """Get payment details."""
    payment = payment_service.get_payment(payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {
        "id": str(payment.id),
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status.value,
        "payment_type": payment.payment_type.value,
        "created_at": payment.created_at.isoformat(),
        "completed_at": payment.completed_at.isoformat() if payment.completed_at else None
    }


@router.get("/client/{client_id}")
async def get_client_payments(client_id: UUID, status: Optional[str] = None):
    """Get all payments for a client."""
    payment_status = PaymentStatus(status) if status else None
    payments = payment_service.get_client_payments(client_id, payment_status)

    return {
        "count": len(payments),
        "payments": [
            {
                "id": str(p.id),
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status.value,
                "payment_type": p.payment_type.value,
                "created_at": p.created_at.isoformat()
            }
            for p in payments
        ]
    }


@router.get("/practitioner/{practitioner_id}/earnings")
async def get_practitioner_earnings(
    practitioner_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get earnings summary for a practitioner."""
    return payment_service.get_practitioner_earnings(
        practitioner_id,
        start_date,
        end_date
    )


# ============================================================================
# SUBSCRIPTION ENDPOINTS
# ============================================================================

@router.post("/subscriptions")
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a new subscription."""
    try:
        tier = SubscriptionTier(request.tier)
        period = BillingPeriod(request.billing_period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid tier or period: {e}")

    subscription = subscription_service.create_subscription(
        user_id=request.user_id,
        tier=tier,
        billing_period=period,
        trial_days=request.trial_days
    )

    return {
        "id": str(subscription.id),
        "tier": subscription.tier.value,
        "status": subscription.status.value,
        "price": subscription.price,
        "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
        "period_end": subscription.current_period_end.isoformat()
    }


@router.get("/subscriptions/user/{user_id}")
async def get_user_subscription(user_id: UUID):
    """Get user's active subscription."""
    subscription = subscription_service.get_user_subscription(user_id)

    if not subscription:
        return {"tier": "free", "status": "none"}

    return {
        "id": str(subscription.id),
        "tier": subscription.tier.value,
        "status": subscription.status.value,
        "price": subscription.price,
        "billing_period": subscription.billing_period.value,
        "period_end": subscription.current_period_end.isoformat()
    }


@router.post("/subscriptions/{subscription_id}/upgrade")
async def upgrade_subscription(subscription_id: UUID, new_tier: str):
    """Upgrade subscription tier."""
    try:
        tier = SubscriptionTier(new_tier)
        subscription = subscription_service.upgrade_subscription(subscription_id, tier)

        return {
            "id": str(subscription.id),
            "tier": subscription.tier.value,
            "price": subscription.price,
            "message": f"Upgraded to {tier.value}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: UUID, immediate: bool = False):
    """Cancel subscription."""
    try:
        subscription = subscription_service.cancel_subscription(
            subscription_id,
            immediate
        )

        return {
            "id": str(subscription.id),
            "status": subscription.status.value,
            "cancelled_at": subscription.cancelled_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions/pricing")
async def get_pricing():
    """Get all subscription pricing."""
    return subscription_service.get_pricing()


@router.get("/subscriptions/stats/{user_id}")
async def get_subscription_stats(user_id: UUID):
    """Get subscription stats and usage."""
    return subscription_service.get_subscription_stats(user_id)


@router.get("/subscriptions/feature/{user_id}/{feature}")
async def check_feature_access(user_id: UUID, feature: str):
    """Check if user has access to a feature."""
    return subscription_service.check_feature_access(user_id, feature)


# ============================================================================
# PAYOUT ENDPOINTS
# ============================================================================

@router.get("/payouts/balance/{practitioner_id}")
async def get_balance(practitioner_id: UUID):
    """Get practitioner's current balance."""
    return payout_service.get_balance(practitioner_id)


@router.post("/payouts/initiate/{practitioner_id}")
async def initiate_payout(practitioner_id: UUID, amount: Optional[float] = None):
    """Initiate a payout to practitioner."""
    try:
        payout = payout_service.initiate_payout(practitioner_id, amount)

        return {
            "id": str(payout.id),
            "amount": payout.amount,
            "status": payout.status.value,
            "arrival_date": payout.arrival_date.isoformat() if payout.arrival_date else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payouts/{practitioner_id}")
async def get_practitioner_payouts(
    practitioner_id: UUID,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get payout history for practitioner."""
    from services.payments.payouts import PayoutStatus as PS

    payout_status = PS(status) if status else None
    payouts = payout_service.get_practitioner_payouts(
        practitioner_id,
        payout_status,
        limit
    )

    return {
        "count": len(payouts),
        "payouts": [
            {
                "id": str(p.id),
                "amount": p.amount,
                "status": p.status.value,
                "initiated_at": p.initiated_at.isoformat(),
                "arrival_date": p.arrival_date.isoformat() if p.arrival_date else None
            }
            for p in payouts
        ]
    }


@router.post("/payouts/schedule/{practitioner_id}")
async def set_payout_schedule(practitioner_id: UUID, request: SetPayoutScheduleRequest):
    """Set automatic payout schedule."""
    try:
        schedule = PayoutSchedule(request.schedule)
        return payout_service.set_payout_schedule(practitioner_id, schedule)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid schedule")


@router.get("/payouts/summary/{practitioner_id}")
async def get_payout_summary(
    practitioner_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get payout summary for practitioner."""
    return payout_service.get_payout_summary(
        practitioner_id,
        start_date,
        end_date
    )


# ============================================================================
# STRIPE CONNECT ENDPOINTS
# ============================================================================

@router.post("/connect/account")
async def create_connect_account(request: CreateConnectAccountRequest):
    """Create Stripe Connect account for practitioner."""
    return payment_service.create_connect_account(
        request.practitioner_id,
        request.email
    )


@router.get("/connect/status/{practitioner_id}")
async def get_connect_status(practitioner_id: UUID):
    """Get Stripe Connect account status."""
    return payment_service.get_connect_account_status(practitioner_id)


@router.get("/payment-methods/{user_id}")
async def get_payment_methods(user_id: UUID):
    """Get saved payment methods for user."""
    return payment_service.get_payment_methods(user_id)
