"""
Stripe payment service for SANA Platform.
"""

from typing import Dict, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentType(str, Enum):
    """Types of payments."""
    BOOKING = "booking"
    SUBSCRIPTION = "subscription"
    TIP = "tip"
    PRODUCT = "product"


class Payment(BaseModel):
    """A payment record."""
    id: UUID
    stripe_payment_intent_id: Optional[str] = None

    # Parties
    client_id: UUID
    practitioner_id: Optional[UUID] = None

    # Details
    amount: float  # In smallest currency unit (pence)
    currency: str = "gbp"
    payment_type: PaymentType
    description: str

    # Related entities
    booking_id: Optional[UUID] = None
    subscription_id: Optional[UUID] = None

    # Status
    status: PaymentStatus = PaymentStatus.PENDING

    # Fees
    platform_fee: float = 0.0
    stripe_fee: float = 0.0
    practitioner_payout: float = 0.0

    # Timestamps
    created_at: datetime
    completed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = {}


class StripePaymentService:
    """
    Handles Stripe payments for bookings and subscriptions.

    Features:
    - Payment intents
    - Refunds
    - Platform fees
    - Connect payouts
    """

    # Platform fee percentage (SANA takes 10%)
    PLATFORM_FEE_PERCENT = 0.10

    def __init__(self):
        self.payments: Dict[UUID, Payment] = {}
        self.customer_ids: Dict[UUID, str] = {}  # user_id -> stripe_customer_id
        self.connect_accounts: Dict[UUID, str] = {}  # practitioner_id -> stripe_account_id
        logger.info("StripePaymentService initialized")

    def create_payment_intent(
        self,
        client_id: UUID,
        amount: float,
        currency: str = "gbp",
        payment_type: PaymentType = PaymentType.BOOKING,
        description: str = "",
        practitioner_id: Optional[UUID] = None,
        booking_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent for client checkout.

        Args:
            client_id: Client making payment
            amount: Amount in pounds (will convert to pence)
            currency: Currency code
            payment_type: Type of payment
            description: Payment description
            practitioner_id: Receiving practitioner
            booking_id: Associated booking
            metadata: Additional metadata

        Returns:
            Payment intent details with client_secret
        """
        now = datetime.utcnow()

        # Convert to smallest unit
        amount_pence = int(amount * 100)

        # Calculate fees
        platform_fee = amount * self.PLATFORM_FEE_PERCENT
        stripe_fee = (amount * 0.029) + 0.30  # Stripe's typical fee
        practitioner_payout = amount - platform_fee - stripe_fee

        # Create payment record
        payment = Payment(
            id=uuid4(),
            stripe_payment_intent_id=f"pi_{uuid4().hex[:24]}",  # Simulated
            client_id=client_id,
            practitioner_id=practitioner_id,
            amount=amount,
            currency=currency,
            payment_type=payment_type,
            description=description,
            booking_id=booking_id,
            status=PaymentStatus.PENDING,
            platform_fee=platform_fee,
            stripe_fee=stripe_fee,
            practitioner_payout=practitioner_payout,
            created_at=now,
            metadata=metadata or {}
        )

        self.payments[payment.id] = payment

        logger.info(f"Created payment intent {payment.id} for {amount} {currency}")

        return {
            "payment_id": str(payment.id),
            "client_secret": f"cs_{uuid4().hex}",  # Simulated
            "amount": amount,
            "amount_pence": amount_pence,
            "currency": currency,
            "platform_fee": platform_fee,
            "practitioner_receives": practitioner_payout
        }

    def confirm_payment(
        self,
        payment_id: UUID,
        payment_method_id: str
    ) -> Payment:
        """
        Confirm a payment (simulate Stripe webhook).

        In production, this would be called by Stripe webhook.
        """
        if payment_id not in self.payments:
            raise ValueError("Payment not found")

        payment = self.payments[payment_id]
        payment.status = PaymentStatus.SUCCEEDED
        payment.completed_at = datetime.utcnow()

        logger.info(f"Payment {payment_id} confirmed")

        return payment

    def refund_payment(
        self,
        payment_id: UUID,
        amount: Optional[float] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Refund a payment (full or partial).

        Args:
            payment_id: Payment to refund
            amount: Refund amount (None for full refund)
            reason: Refund reason

        Returns:
            Refund details
        """
        if payment_id not in self.payments:
            raise ValueError("Payment not found")

        payment = self.payments[payment_id]

        if payment.status != PaymentStatus.SUCCEEDED:
            raise ValueError("Can only refund succeeded payments")

        refund_amount = amount if amount else payment.amount
        payment.status = PaymentStatus.REFUNDED
        payment.refunded_at = datetime.utcnow()

        logger.info(f"Refunded {refund_amount} for payment {payment_id}")

        return {
            "payment_id": str(payment_id),
            "refund_id": f"re_{uuid4().hex[:24]}",
            "amount_refunded": refund_amount,
            "reason": reason
        }

    def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """Get a payment by ID."""
        return self.payments.get(payment_id)

    def get_client_payments(
        self,
        client_id: UUID,
        status: Optional[PaymentStatus] = None
    ) -> list[Payment]:
        """Get all payments for a client."""
        payments = [
            p for p in self.payments.values()
            if p.client_id == client_id
        ]

        if status:
            payments = [p for p in payments if p.status == status]

        return sorted(payments, key=lambda x: x.created_at, reverse=True)

    def get_practitioner_payments(
        self,
        practitioner_id: UUID,
        status: Optional[PaymentStatus] = None
    ) -> list[Payment]:
        """Get all payments for a practitioner."""
        payments = [
            p for p in self.payments.values()
            if p.practitioner_id == practitioner_id
        ]

        if status:
            payments = [p for p in payments if p.status == status]

        return sorted(payments, key=lambda x: x.created_at, reverse=True)

    def get_practitioner_earnings(
        self,
        practitioner_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get earnings summary for a practitioner."""
        payments = [
            p for p in self.payments.values()
            if p.practitioner_id == practitioner_id
            and p.status == PaymentStatus.SUCCEEDED
        ]

        if start_date:
            payments = [p for p in payments if p.completed_at >= start_date]

        if end_date:
            payments = [p for p in payments if p.completed_at <= end_date]

        total_gross = sum(p.amount for p in payments)
        total_fees = sum(p.platform_fee + p.stripe_fee for p in payments)
        total_net = sum(p.practitioner_payout for p in payments)

        return {
            "practitioner_id": str(practitioner_id),
            "total_transactions": len(payments),
            "gross_earnings": total_gross,
            "total_fees": total_fees,
            "net_earnings": total_net,
            "currency": "gbp"
        }

    def create_connect_account(self, practitioner_id: UUID, email: str) -> Dict[str, Any]:
        """
        Create Stripe Connect account for practitioner.

        Returns onboarding link.
        """
        account_id = f"acct_{uuid4().hex[:16]}"
        self.connect_accounts[practitioner_id] = account_id

        logger.info(f"Created Connect account for practitioner {practitioner_id}")

        return {
            "account_id": account_id,
            "onboarding_url": f"https://connect.stripe.com/setup/{account_id}",
            "status": "pending"
        }

    def get_connect_account_status(self, practitioner_id: UUID) -> Dict[str, Any]:
        """Get Stripe Connect account status."""
        if practitioner_id not in self.connect_accounts:
            return {"status": "not_created"}

        return {
            "account_id": self.connect_accounts[practitioner_id],
            "status": "active",
            "payouts_enabled": True,
            "charges_enabled": True
        }

    def create_customer(self, user_id: UUID, email: str) -> str:
        """Create Stripe customer for a user."""
        customer_id = f"cus_{uuid4().hex[:14]}"
        self.customer_ids[user_id] = customer_id

        logger.info(f"Created Stripe customer for user {user_id}")

        return customer_id

    def get_payment_methods(self, user_id: UUID) -> list[Dict[str, Any]]:
        """Get saved payment methods for a user."""
        # Simulated payment methods
        if user_id in self.customer_ids:
            return [
                {
                    "id": f"pm_{uuid4().hex[:24]}",
                    "type": "card",
                    "card": {
                        "brand": "visa",
                        "last4": "4242",
                        "exp_month": 12,
                        "exp_year": 2025
                    },
                    "is_default": True
                }
            ]
        return []
