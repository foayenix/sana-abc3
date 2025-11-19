"""Stripe payment service for session bookings."""

import stripe
from typing import Optional
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payments."""

    @staticmethod
    async def create_customer(email: str, name: str, metadata: dict = None) -> str:
        """Create a Stripe customer."""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {},
        )
        return customer.id

    @staticmethod
    async def create_payment_intent(
        amount: int,  # in cents
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: dict = None,
    ) -> dict:
        """Create a payment intent for session booking."""
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True},
        )
        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status,
        }

    @staticmethod
    async def confirm_payment(payment_intent_id: str) -> dict:
        """Retrieve payment intent status."""
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "id": intent.id,
            "status": intent.status,
            "amount": intent.amount,
        }

    @staticmethod
    async def create_refund(
        payment_intent_id: str,
        amount: Optional[int] = None,  # None for full refund
        reason: str = "requested_by_customer",
    ) -> dict:
        """Create a refund for a payment."""
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=amount,
            reason=reason,
        )
        return {
            "id": refund.id,
            "status": refund.status,
            "amount": refund.amount,
        }

    @staticmethod
    async def create_connected_account(
        email: str,
        country: str = "US",
    ) -> str:
        """Create a connected account for practitioner payouts."""
        account = stripe.Account.create(
            type="express",
            country=country,
            email=email,
            capabilities={
                "transfers": {"requested": True},
            },
        )
        return account.id

    @staticmethod
    async def create_account_link(
        account_id: str,
        refresh_url: str,
        return_url: str,
    ) -> str:
        """Create account link for onboarding."""
        link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )
        return link.url

    @staticmethod
    async def create_transfer(
        amount: int,
        destination_account_id: str,
        metadata: dict = None,
    ) -> dict:
        """Transfer funds to connected account (practitioner payout)."""
        transfer = stripe.Transfer.create(
            amount=amount,
            currency="usd",
            destination=destination_account_id,
            metadata=metadata or {},
        )
        return {
            "id": transfer.id,
            "amount": transfer.amount,
            "status": "pending",
        }

    @staticmethod
    async def get_balance() -> dict:
        """Get platform balance."""
        balance = stripe.Balance.retrieve()
        return {
            "available": balance.available[0].amount if balance.available else 0,
            "pending": balance.pending[0].amount if balance.pending else 0,
        }

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
        """Construct webhook event from payload."""
        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )


stripe_service = StripeService()
