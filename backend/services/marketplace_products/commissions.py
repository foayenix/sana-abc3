"""
Commission Service
==================
Tracks practitioner commissions from product sales.
"""

import logging
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CommissionStatus(str, Enum):
    PENDING = "pending"  # Order placed, not yet paid
    CONFIRMED = "confirmed"  # Order paid, commission confirmed
    PAID = "paid"  # Commission paid out to practitioner
    CANCELLED = "cancelled"  # Order cancelled, commission void


class Commission(BaseModel):
    """Practitioner commission record"""
    id: UUID = Field(default_factory=uuid4)
    practitioner_id: UUID
    order_id: UUID
    client_id: UUID

    # Amounts
    order_total: Decimal
    commission_rate: Decimal  # Percentage (15.0 = 15%)
    commission_amount: Decimal

    # Status
    status: CommissionStatus = CommissionStatus.PENDING

    # Payout info
    payout_id: Optional[UUID] = None
    paid_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None


class Payout(BaseModel):
    """Commission payout to practitioner"""
    id: UUID = Field(default_factory=uuid4)
    practitioner_id: UUID

    # Amounts
    amount: Decimal
    currency: str = "GBP"
    commission_count: int = 0  # Number of commissions included

    # Payment info
    stripe_transfer_id: Optional[str] = None
    stripe_payout_id: Optional[str] = None

    # Status
    status: str = "pending"  # pending, processing, completed, failed

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class CommissionService:
    """
    Commission Service

    Manages practitioner commissions:
    - Track commissions from product sales
    - Calculate earnings summaries
    - Process commission payouts
    """

    DEFAULT_COMMISSION_RATE = Decimal("15.0")  # 15% default

    def __init__(self):
        self._commissions: Dict[UUID, Commission] = {}
        self._payouts: Dict[UUID, Payout] = {}

    def create_commission(
        self,
        practitioner_id: UUID,
        order_id: UUID,
        client_id: UUID,
        order_total: Decimal,
        commission_rate: Optional[Decimal] = None,
    ) -> Commission:
        """
        Create a commission record for a sale

        Args:
            practitioner_id: Practitioner earning commission
            order_id: Associated order
            client_id: Client who made purchase
            order_total: Total order amount
            commission_rate: Commission percentage (default 15%)

        Returns:
            Created commission
        """
        rate = commission_rate or self.DEFAULT_COMMISSION_RATE
        amount = order_total * (rate / 100)

        commission = Commission(
            practitioner_id=practitioner_id,
            order_id=order_id,
            client_id=client_id,
            order_total=order_total,
            commission_rate=rate,
            commission_amount=amount,
        )

        self._commissions[commission.id] = commission
        return commission

    def confirm_commission(self, commission_id: UUID) -> Commission:
        """Confirm commission after order is paid"""
        commission = self._commissions.get(commission_id)
        if not commission:
            raise ValueError("Commission not found")

        commission.status = CommissionStatus.CONFIRMED
        commission.confirmed_at = datetime.utcnow()
        return commission

    def cancel_commission(self, commission_id: UUID) -> Commission:
        """Cancel commission (order cancelled/refunded)"""
        commission = self._commissions.get(commission_id)
        if not commission:
            raise ValueError("Commission not found")

        if commission.status == CommissionStatus.PAID:
            raise ValueError("Cannot cancel paid commission")

        commission.status = CommissionStatus.CANCELLED
        return commission

    def get_practitioner_commissions(
        self,
        practitioner_id: UUID,
        status: Optional[CommissionStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Commission]:
        """Get commissions for a practitioner"""
        commissions = [
            c for c in self._commissions.values()
            if c.practitioner_id == practitioner_id
        ]

        if status:
            commissions = [c for c in commissions if c.status == status]

        if from_date:
            commissions = [c for c in commissions if c.created_at >= from_date]

        if to_date:
            commissions = [c for c in commissions if c.created_at <= to_date]

        return sorted(commissions, key=lambda c: c.created_at, reverse=True)

    def get_commission_summary(self, practitioner_id: UUID) -> Dict:
        """Get commission summary for a practitioner"""
        commissions = self.get_practitioner_commissions(practitioner_id)

        total_earned = sum(
            c.commission_amount for c in commissions
            if c.status in [CommissionStatus.CONFIRMED, CommissionStatus.PAID]
        )

        pending = sum(
            c.commission_amount for c in commissions
            if c.status == CommissionStatus.PENDING
        )

        available_for_payout = sum(
            c.commission_amount for c in commissions
            if c.status == CommissionStatus.CONFIRMED
        )

        paid_out = sum(
            c.commission_amount for c in commissions
            if c.status == CommissionStatus.PAID
        )

        # This month's earnings
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        this_month = sum(
            c.commission_amount for c in commissions
            if c.created_at >= month_start and c.status in [
                CommissionStatus.CONFIRMED, CommissionStatus.PAID
            ]
        )

        return {
            "total_earned": float(total_earned),
            "pending": float(pending),
            "available_for_payout": float(available_for_payout),
            "paid_out": float(paid_out),
            "this_month": float(this_month),
            "total_orders": len([
                c for c in commissions
                if c.status != CommissionStatus.CANCELLED
            ]),
            "currency": "GBP",
        }

    def get_monthly_breakdown(
        self,
        practitioner_id: UUID,
        months: int = 6
    ) -> List[Dict]:
        """Get monthly commission breakdown"""
        commissions = self.get_practitioner_commissions(practitioner_id)

        breakdown = []
        now = datetime.utcnow()

        for i in range(months):
            # Calculate month boundaries
            month_offset = now.month - i - 1
            year_offset = 0
            while month_offset < 0:
                month_offset += 12
                year_offset -= 1

            month = month_offset + 1
            year = now.year + year_offset

            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)

            month_commissions = [
                c for c in commissions
                if month_start <= c.created_at < month_end
                and c.status != CommissionStatus.CANCELLED
            ]

            total = sum(c.commission_amount for c in month_commissions)

            breakdown.append({
                "month": month_start.strftime("%B %Y"),
                "total": float(total),
                "order_count": len(month_commissions),
            })

        return breakdown

    def create_payout(self, practitioner_id: UUID) -> Payout:
        """
        Create a payout for confirmed commissions

        Args:
            practitioner_id: Practitioner to pay out

        Returns:
            Created payout
        """
        # Get unpaid confirmed commissions
        commissions = self.get_practitioner_commissions(
            practitioner_id,
            status=CommissionStatus.CONFIRMED,
        )

        if not commissions:
            raise ValueError("No commissions available for payout")

        total_amount = sum(c.commission_amount for c in commissions)

        payout = Payout(
            practitioner_id=practitioner_id,
            amount=total_amount,
            commission_count=len(commissions),
        )

        # Mark commissions as paid
        for commission in commissions:
            commission.status = CommissionStatus.PAID
            commission.payout_id = payout.id
            commission.paid_at = datetime.utcnow()

        self._payouts[payout.id] = payout
        return payout

    def get_practitioner_payouts(self, practitioner_id: UUID) -> List[Payout]:
        """Get all payouts for a practitioner"""
        return [
            p for p in self._payouts.values()
            if p.practitioner_id == practitioner_id
        ]

    def complete_payout(
        self,
        payout_id: UUID,
        stripe_transfer_id: Optional[str] = None
    ) -> Payout:
        """Mark payout as completed"""
        payout = self._payouts.get(payout_id)
        if not payout:
            raise ValueError("Payout not found")

        payout.status = "completed"
        payout.stripe_transfer_id = stripe_transfer_id
        payout.completed_at = datetime.utcnow()

        return payout
