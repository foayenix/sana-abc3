"""
Prescription Service
====================
Handles practitioner prescriptions that clients can purchase.
"""

import logging
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PrescriptionStatus(str, Enum):
    ACTIVE = "active"
    PURCHASED = "purchased"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PrescribedItem(BaseModel):
    """Single item in a prescription"""
    product_id: UUID
    product_name: str
    dosage: str
    frequency: str  # "twice daily", "as needed"
    duration: str  # "4 weeks", "ongoing"
    quantity: int = 1
    notes: Optional[str] = None


class Prescription(BaseModel):
    """Prescription from practitioner to client"""
    id: UUID = Field(default_factory=uuid4)
    practitioner_id: UUID
    client_id: UUID

    # Items
    items: List[PrescribedItem]

    # Details
    diagnosis: Optional[str] = None
    notes: Optional[str] = None

    # Status
    status: PrescriptionStatus = PrescriptionStatus.ACTIVE
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))

    # Purchase info
    order_id: Optional[UUID] = None
    purchased_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PrescriptionService:
    """
    Prescription Service

    Manages the prescription workflow:
    1. Practitioner creates prescription for client
    2. Client receives notification
    3. Client can purchase prescribed products
    4. Practitioner earns commission on purchases
    """

    def __init__(self, product_service=None):
        from .products import MarketplaceProductService
        self.product_service = product_service or MarketplaceProductService()
        self._prescriptions: Dict[UUID, Prescription] = {}

    def create_prescription(
        self,
        practitioner_id: UUID,
        client_id: UUID,
        items: List[Dict],
        diagnosis: Optional[str] = None,
        notes: Optional[str] = None,
        expires_days: int = 90,
    ) -> Prescription:
        """
        Create a new prescription

        Args:
            practitioner_id: Practitioner creating the prescription
            client_id: Client receiving the prescription
            items: List of product items with dosage instructions
            diagnosis: Optional diagnosis
            notes: Additional notes
            expires_days: Days until prescription expires

        Returns:
            Created prescription
        """
        prescribed_items = []

        for item_data in items:
            product_id = item_data.get("product_id")
            if isinstance(product_id, str):
                product_id = UUID(product_id)

            product = self.product_service.get_product(product_id)
            if not product:
                raise ValueError(f"Product not found: {product_id}")

            prescribed_items.append(PrescribedItem(
                product_id=product_id,
                product_name=product.name,
                dosage=item_data.get("dosage", "As directed"),
                frequency=item_data.get("frequency", "As directed"),
                duration=item_data.get("duration", "As needed"),
                quantity=item_data.get("quantity", 1),
                notes=item_data.get("notes"),
            ))

        prescription = Prescription(
            practitioner_id=practitioner_id,
            client_id=client_id,
            items=prescribed_items,
            diagnosis=diagnosis,
            notes=notes,
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
        )

        self._prescriptions[prescription.id] = prescription
        return prescription

    def get_prescription(self, prescription_id: UUID) -> Optional[Prescription]:
        """Get prescription by ID"""
        return self._prescriptions.get(prescription_id)

    def get_client_prescriptions(
        self,
        client_id: UUID,
        active_only: bool = True
    ) -> List[Prescription]:
        """Get all prescriptions for a client"""
        prescriptions = [
            p for p in self._prescriptions.values()
            if p.client_id == client_id
        ]

        if active_only:
            now = datetime.utcnow()
            prescriptions = [
                p for p in prescriptions
                if p.status == PrescriptionStatus.ACTIVE and p.expires_at > now
            ]

        return sorted(prescriptions, key=lambda p: p.created_at, reverse=True)

    def get_practitioner_prescriptions(
        self,
        practitioner_id: UUID
    ) -> List[Prescription]:
        """Get all prescriptions created by a practitioner"""
        return [
            p for p in self._prescriptions.values()
            if p.practitioner_id == practitioner_id
        ]

    def purchase_prescription(
        self,
        prescription_id: UUID,
        shipping_address: Optional[Dict] = None
    ) -> Dict:
        """
        Purchase all items in a prescription

        Args:
            prescription_id: Prescription to purchase
            shipping_address: Shipping address

        Returns:
            Order details
        """
        prescription = self.get_prescription(prescription_id)

        if not prescription:
            raise ValueError("Prescription not found")

        if prescription.status != PrescriptionStatus.ACTIVE:
            raise ValueError("Prescription is not active")

        if prescription.expires_at < datetime.utcnow():
            prescription.status = PrescriptionStatus.EXPIRED
            raise ValueError("Prescription has expired")

        # Add all items to cart
        cart = self.product_service.get_or_create_cart(prescription.client_id)
        cart.prescription_id = prescription_id

        for item in prescription.items:
            self.product_service.add_to_cart(
                user_id=prescription.client_id,
                product_id=item.product_id,
                quantity=item.quantity,
            )

        # Create order with practitioner commission
        order = self.product_service.create_order(
            user_id=prescription.client_id,
            practitioner_id=prescription.practitioner_id,
            prescription_id=prescription_id,
            shipping_address=shipping_address,
        )

        # Update prescription status
        prescription.status = PrescriptionStatus.PURCHASED
        prescription.order_id = order.id
        prescription.purchased_at = datetime.utcnow()

        return {
            "prescription_id": str(prescription.id),
            "order_id": str(order.id),
            "total": float(order.total),
            "practitioner_commission": float(order.practitioner_commission),
            "status": "success",
        }

    def cancel_prescription(self, prescription_id: UUID) -> Prescription:
        """Cancel a prescription"""
        prescription = self.get_prescription(prescription_id)

        if not prescription:
            raise ValueError("Prescription not found")

        if prescription.status == PrescriptionStatus.PURCHASED:
            raise ValueError("Cannot cancel purchased prescription")

        prescription.status = PrescriptionStatus.CANCELLED
        return prescription

    def get_prescription_purchase_url(self, prescription_id: UUID) -> str:
        """Get shareable purchase URL for prescription"""
        return f"/marketplace/prescriptions/{prescription_id}/purchase"
