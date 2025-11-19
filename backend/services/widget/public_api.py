"""
Public API for widget booking functionality.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class PublicPractitionerProfile(BaseModel):
    """Public-facing practitioner profile."""
    id: UUID
    name: str
    title: str
    bio: str
    profile_image: Optional[str] = None
    specialties: List[str] = []
    credentials: List[Dict[str, str]] = []
    city: str
    sana_index: float = 0.0
    average_rating: float = 0.0
    total_reviews: int = 0
    offers_telehealth: bool = False


class AvailableSlot(BaseModel):
    """An available booking slot."""
    start_time: datetime
    end_time: datetime
    is_telehealth: bool = False


class PublicBooking(BaseModel):
    """A booking made through the widget."""
    id: UUID
    practitioner_id: UUID
    widget_id: UUID

    # Client info
    client_name: str
    client_email: str
    client_phone: Optional[str] = None

    # Booking details
    service_id: UUID
    service_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    is_telehealth: bool = False

    # Payment
    amount: float
    currency: str = "GBP"
    payment_status: str = "pending"
    payment_intent_id: Optional[str] = None

    # Notes
    client_notes: Optional[str] = None

    # Status
    status: str = "confirmed"
    confirmation_code: str

    # Timestamps
    created_at: datetime


class WidgetPublicAPI:
    """
    Public API for widget booking without authentication.

    Provides:
    - Practitioner profile fetch
    - Availability checking
    - Booking creation
    - Booking confirmation
    """

    def __init__(self):
        self.bookings: Dict[UUID, PublicBooking] = {}
        self.bookings_by_code: Dict[str, UUID] = {}
        # Mock practitioner data - in production would fetch from database
        self._mock_profiles: Dict[UUID, PublicPractitionerProfile] = {}
        self._mock_availability: Dict[UUID, List[Dict]] = {}
        logger.info("WidgetPublicAPI initialized")

    def get_practitioner_profile(
        self,
        practitioner_id: UUID,
        include_reviews: bool = True
    ) -> Optional[PublicPractitionerProfile]:
        """Get public practitioner profile for widget display."""
        # In production, fetch from database
        if practitioner_id in self._mock_profiles:
            return self._mock_profiles[practitioner_id]

        # Return mock data for demo
        return PublicPractitionerProfile(
            id=practitioner_id,
            name="Dr. Sarah Chen",
            title="Licensed Acupuncturist",
            bio="Experienced practitioner specializing in pain management and stress relief. Over 10 years of clinical experience.",
            specialties=["Acupuncture", "Traditional Chinese Medicine"],
            credentials=[
                {"type": "License", "name": "Licensed Acupuncturist", "issuer": "BAAB"},
                {"type": "Certification", "name": "TCM Practitioner", "issuer": "ATCM"}
            ],
            city="London",
            sana_index=85.0,
            average_rating=4.8,
            total_reviews=47,
            offers_telehealth=True
        )

    def get_available_slots(
        self,
        practitioner_id: UUID,
        service_id: UUID,
        start_date: date,
        end_date: date,
        duration_minutes: int = 60,
        buffer_minutes: int = 15,
        min_notice_hours: int = 24,
        telehealth_only: bool = False
    ) -> List[AvailableSlot]:
        """
        Get available booking slots.

        Args:
            practitioner_id: Practitioner UUID
            service_id: Service UUID
            start_date: Start of date range
            end_date: End of date range
            duration_minutes: Service duration
            buffer_minutes: Buffer between appointments
            min_notice_hours: Minimum booking notice
            telehealth_only: Only show telehealth slots

        Returns:
            List of available slots
        """
        slots = []
        now = datetime.utcnow()
        min_start = now + timedelta(hours=min_notice_hours)

        current = start_date
        while current <= end_date:
            # Skip if before minimum notice
            if datetime.combine(current, time(9, 0)) < min_start:
                current += timedelta(days=1)
                continue

            # Skip weekends (simplified)
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue

            # Generate slots for business hours (9 AM - 5 PM)
            for hour in range(9, 17):
                slot_start = datetime.combine(current, time(hour, 0))

                # Skip if before minimum notice
                if slot_start < min_start:
                    continue

                slot_end = slot_start + timedelta(minutes=duration_minutes)

                # Check if slot fits in business hours
                if slot_end.hour > 17:
                    continue

                # In production, check against existing bookings
                # For demo, mark some slots as unavailable
                if hour in [12, 13]:  # Lunch break
                    continue

                slots.append(AvailableSlot(
                    start_time=slot_start,
                    end_time=slot_end,
                    is_telehealth=hour % 2 == 0  # Alternate for demo
                ))

            current += timedelta(days=1)

        if telehealth_only:
            slots = [s for s in slots if s.is_telehealth]

        return slots

    def create_booking(
        self,
        widget_id: UUID,
        practitioner_id: UUID,
        service_id: UUID,
        service_name: str,
        start_time: datetime,
        duration_minutes: int,
        client_name: str,
        client_email: str,
        client_phone: Optional[str] = None,
        is_telehealth: bool = False,
        amount: float = 0.0,
        currency: str = "GBP",
        client_notes: Optional[str] = None
    ) -> PublicBooking:
        """
        Create a booking through the widget.

        Args:
            widget_id: Widget UUID
            practitioner_id: Practitioner UUID
            service_id: Service UUID
            service_name: Name of service
            start_time: Appointment start time
            duration_minutes: Duration in minutes
            client_name: Client's name
            client_email: Client's email
            client_phone: Client's phone (optional)
            is_telehealth: Is telehealth appointment
            amount: Payment amount
            currency: Currency code
            client_notes: Client notes

        Returns:
            Created booking
        """
        # Generate confirmation code
        confirmation_code = self._generate_confirmation_code()

        booking = PublicBooking(
            id=uuid4(),
            practitioner_id=practitioner_id,
            widget_id=widget_id,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            service_id=service_id,
            service_name=service_name,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=duration_minutes),
            duration_minutes=duration_minutes,
            is_telehealth=is_telehealth,
            amount=amount,
            currency=currency,
            client_notes=client_notes,
            confirmation_code=confirmation_code,
            created_at=datetime.utcnow()
        )

        self.bookings[booking.id] = booking
        self.bookings_by_code[confirmation_code] = booking.id

        logger.info(f"Created booking {booking.id} via widget {widget_id}")

        return booking

    def _generate_confirmation_code(self) -> str:
        """Generate a human-readable confirmation code."""
        import random
        import string

        # Format: SANA-XXXX-XXXX
        chars = string.ascii_uppercase + string.digits
        part1 = ''.join(random.choices(chars, k=4))
        part2 = ''.join(random.choices(chars, k=4))

        return f"SANA-{part1}-{part2}"

    def get_booking(self, booking_id: UUID) -> Optional[PublicBooking]:
        """Get booking by ID."""
        return self.bookings.get(booking_id)

    def get_booking_by_code(self, confirmation_code: str) -> Optional[PublicBooking]:
        """Get booking by confirmation code."""
        booking_id = self.bookings_by_code.get(confirmation_code)
        if booking_id:
            return self.bookings.get(booking_id)
        return None

    def cancel_booking(
        self,
        booking_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a booking."""
        if booking_id not in self.bookings:
            return False

        booking = self.bookings[booking_id]
        booking.status = "cancelled"

        logger.info(f"Cancelled booking {booking_id}: {reason}")

        return True

    def reschedule_booking(
        self,
        booking_id: UUID,
        new_start_time: datetime
    ) -> Optional[PublicBooking]:
        """Reschedule a booking."""
        if booking_id not in self.bookings:
            return None

        booking = self.bookings[booking_id]
        booking.start_time = new_start_time
        booking.end_time = new_start_time + timedelta(minutes=booking.duration_minutes)

        logger.info(f"Rescheduled booking {booking_id} to {new_start_time}")

        return booking

    def get_practitioner_bookings(
        self,
        practitioner_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[PublicBooking]:
        """Get all bookings for a practitioner (for sync)."""
        bookings = [
            b for b in self.bookings.values()
            if b.practitioner_id == practitioner_id
        ]

        if start_date:
            bookings = [
                b for b in bookings
                if b.start_time.date() >= start_date
            ]

        if end_date:
            bookings = [
                b for b in bookings
                if b.start_time.date() <= end_date
            ]

        return sorted(bookings, key=lambda x: x.start_time)

    def create_payment_intent(
        self,
        booking_id: UUID,
        amount: float,
        currency: str = "gbp"
    ) -> Dict[str, Any]:
        """Create payment intent for booking."""
        if booking_id not in self.bookings:
            raise ValueError("Booking not found")

        booking = self.bookings[booking_id]

        # Generate mock payment intent
        payment_intent_id = f"pi_widget_{uuid4().hex[:24]}"
        booking.payment_intent_id = payment_intent_id

        return {
            "payment_intent_id": payment_intent_id,
            "client_secret": f"cs_{uuid4().hex}",
            "amount": int(amount * 100),  # Convert to pence
            "currency": currency
        }

    def confirm_payment(self, booking_id: UUID) -> bool:
        """Confirm payment for a booking."""
        if booking_id not in self.bookings:
            return False

        booking = self.bookings[booking_id]
        booking.payment_status = "paid"

        return True

    def get_reviews(
        self,
        practitioner_id: UUID,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent reviews for widget display."""
        # Mock reviews for demo
        return [
            {
                "rating": 5,
                "title": "Excellent treatment",
                "content": "Dr. Chen was incredibly professional and the treatment was very effective.",
                "author_initial": "J",
                "date": (datetime.utcnow() - timedelta(days=5)).isoformat()
            },
            {
                "rating": 5,
                "title": "Highly recommend",
                "content": "I've been seeing Dr. Chen for 3 months and my chronic pain has significantly improved.",
                "author_initial": "M",
                "date": (datetime.utcnow() - timedelta(days=12)).isoformat()
            },
            {
                "rating": 4,
                "title": "Very helpful",
                "content": "Great experience overall. The clinic is clean and welcoming.",
                "author_initial": "S",
                "date": (datetime.utcnow() - timedelta(days=20)).isoformat()
            }
        ][:limit]

    def validate_slot_available(
        self,
        practitioner_id: UUID,
        start_time: datetime,
        duration_minutes: int
    ) -> bool:
        """Check if a specific slot is still available."""
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Check against existing bookings
        for booking in self.bookings.values():
            if booking.practitioner_id != practitioner_id:
                continue
            if booking.status == "cancelled":
                continue

            # Check for overlap
            if start_time < booking.end_time and end_time > booking.start_time:
                return False

        return True
