"""
Payout service for practitioner earnings.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PayoutStatus(str, Enum):
    """Payout status."""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PayoutSchedule(str, Enum):
    """Payout schedule options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"


class Payout(BaseModel):
    """A payout to practitioner."""
    id: UUID
    practitioner_id: UUID
    stripe_payout_id: Optional[str] = None

    # Amount
    amount: float
    currency: str = "gbp"

    # Status
    status: PayoutStatus = PayoutStatus.PENDING

    # Details
    payment_ids: List[UUID] = []  # Payments included
    description: str = ""

    # Timestamps
    initiated_at: datetime
    arrival_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Bank details (masked)
    bank_account_last4: Optional[str] = None


class PayoutService:
    """
    Manages payouts to practitioners.

    Features:
    - Scheduled payouts
    - Instant payouts
    - Payout history
    - Balance tracking
    """

    def __init__(self):
        self.payouts: Dict[UUID, Payout] = {}
        self.balances: Dict[UUID, float] = {}  # practitioner_id -> available balance
        self.payout_schedules: Dict[UUID, PayoutSchedule] = {}
        logger.info("PayoutService initialized")

    def add_to_balance(
        self,
        practitioner_id: UUID,
        amount: float,
        payment_id: UUID
    ) -> float:
        """Add funds to practitioner's available balance."""
        if practitioner_id not in self.balances:
            self.balances[practitioner_id] = 0

        self.balances[practitioner_id] += amount

        logger.info(
            f"Added {amount} to balance for practitioner {practitioner_id}"
        )

        return self.balances[practitioner_id]

    def get_balance(self, practitioner_id: UUID) -> Dict[str, Any]:
        """Get practitioner's current balance."""
        available = self.balances.get(practitioner_id, 0)

        # Get pending payouts
        pending = sum(
            p.amount for p in self.payouts.values()
            if p.practitioner_id == practitioner_id
            and p.status in [PayoutStatus.PENDING, PayoutStatus.IN_TRANSIT]
        )

        return {
            "available": available,
            "pending": pending,
            "currency": "gbp"
        }

    def initiate_payout(
        self,
        practitioner_id: UUID,
        amount: Optional[float] = None
    ) -> Payout:
        """
        Initiate a payout to practitioner.

        Args:
            practitioner_id: Practitioner ID
            amount: Amount to payout (None for full balance)

        Returns:
            Created payout
        """
        balance = self.balances.get(practitioner_id, 0)
        payout_amount = amount if amount else balance

        if payout_amount <= 0:
            raise ValueError("No funds available for payout")

        if payout_amount > balance:
            raise ValueError("Insufficient balance")

        # Deduct from balance
        self.balances[practitioner_id] -= payout_amount

        # Create payout
        payout = Payout(
            id=uuid4(),
            practitioner_id=practitioner_id,
            stripe_payout_id=f"po_{uuid4().hex[:24]}",
            amount=payout_amount,
            status=PayoutStatus.PENDING,
            initiated_at=datetime.utcnow(),
            arrival_date=datetime.utcnow() + timedelta(days=2)  # T+2
        )

        self.payouts[payout.id] = payout

        logger.info(
            f"Initiated payout of {payout_amount} for practitioner {practitioner_id}"
        )

        return payout

    def get_payout(self, payout_id: UUID) -> Optional[Payout]:
        """Get payout by ID."""
        return self.payouts.get(payout_id)

    def get_practitioner_payouts(
        self,
        practitioner_id: UUID,
        status: Optional[PayoutStatus] = None,
        limit: int = 50
    ) -> List[Payout]:
        """Get payout history for a practitioner."""
        payouts = [
            p for p in self.payouts.values()
            if p.practitioner_id == practitioner_id
        ]

        if status:
            payouts = [p for p in payouts if p.status == status]

        # Sort by date
        payouts.sort(key=lambda x: x.initiated_at, reverse=True)

        return payouts[:limit]

    def set_payout_schedule(
        self,
        practitioner_id: UUID,
        schedule: PayoutSchedule
    ) -> Dict[str, Any]:
        """Set automatic payout schedule for practitioner."""
        self.payout_schedules[practitioner_id] = schedule

        logger.info(
            f"Set payout schedule to {schedule.value} for practitioner {practitioner_id}"
        )

        return {
            "practitioner_id": str(practitioner_id),
            "schedule": schedule.value,
            "message": f"Payouts will occur {schedule.value}"
        }

    def get_payout_schedule(self, practitioner_id: UUID) -> PayoutSchedule:
        """Get payout schedule for practitioner."""
        return self.payout_schedules.get(practitioner_id, PayoutSchedule.WEEKLY)

    def process_scheduled_payouts(self) -> List[Payout]:
        """
        Process all scheduled payouts.

        Should be called by cron job.
        """
        processed = []

        for practitioner_id, schedule in self.payout_schedules.items():
            if schedule == PayoutSchedule.MANUAL:
                continue

            balance = self.balances.get(practitioner_id, 0)

            if balance > 0:
                try:
                    payout = self.initiate_payout(practitioner_id)
                    processed.append(payout)
                except Exception as e:
                    logger.error(
                        f"Failed to process payout for {practitioner_id}: {e}"
                    )

        return processed

    def complete_payout(self, payout_id: UUID) -> Payout:
        """Mark payout as completed (simulates Stripe webhook)."""
        if payout_id not in self.payouts:
            raise ValueError("Payout not found")

        payout = self.payouts[payout_id]
        payout.status = PayoutStatus.PAID
        payout.completed_at = datetime.utcnow()

        logger.info(f"Payout {payout_id} completed")

        return payout

    def get_payout_summary(
        self,
        practitioner_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get payout summary for a practitioner."""
        payouts = [
            p for p in self.payouts.values()
            if p.practitioner_id == practitioner_id
            and p.status == PayoutStatus.PAID
        ]

        if start_date:
            payouts = [p for p in payouts if p.completed_at >= start_date]

        if end_date:
            payouts = [p for p in payouts if p.completed_at <= end_date]

        total_paid = sum(p.amount for p in payouts)

        return {
            "practitioner_id": str(practitioner_id),
            "total_payouts": len(payouts),
            "total_paid": total_paid,
            "currency": "gbp",
            "current_balance": self.balances.get(practitioner_id, 0)
        }
