"""
Booking service for appointment management.
"""

from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BookingStatus(str, Enum):
    """Booking status types."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class Booking(BaseModel):
    """An appointment booking."""
    id: UUID
    client_id: UUID
    practitioner_id: UUID

    # Schedule
    scheduled_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    timezone: str = "Europe/London"

    # Details
    session_type: str  # initial, follow_up, telehealth
    service_name: str
    notes: str = ""

    # Pricing
    price: float
    currency: str = "GBP"
    deposit_required: bool = False
    deposit_amount: float = 0.0

    # Status
    status: BookingStatus = BookingStatus.PENDING
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: str = ""

    # Reminders
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None

    # Associated records
    payment_id: Optional[UUID] = None
    session_note_id: Optional[UUID] = None

    # Metadata
    created_at: datetime
    updated_at: datetime


class BookingService:
    """
    Manages booking lifecycle.

    Features:
    - Create and manage bookings
    - Confirmation workflow
    - Cancellation and rescheduling
    - Reminder scheduling
    """

    # Cancellation policies
    FREE_CANCELLATION_HOURS = 24
    LATE_CANCELLATION_FEE_PERCENT = 50

    def __init__(self):
        self.bookings: Dict[UUID, Booking] = {}
        logger.info("BookingService initialized")

    def create_booking(
        self,
        client_id: UUID,
        practitioner_id: UUID,
        scheduled_date: date,
        start_time: time,
        duration_minutes: int,
        session_type: str,
        service_name: str,
        price: float,
        notes: str = "",
        timezone: str = "Europe/London"
    ) -> Booking:
        """
        Create a new booking.

        Args:
            client_id: Client UUID
            practitioner_id: Practitioner UUID
            scheduled_date: Date of appointment
            start_time: Start time
            duration_minutes: Duration in minutes
            session_type: Type of session
            service_name: Name of service
            price: Price in currency
            notes: Client notes
            timezone: Timezone

        Returns:
            Created Booking
        """
        now = datetime.utcnow()
        end_time = (
            datetime.combine(scheduled_date, start_time) +
            timedelta(minutes=duration_minutes)
        ).time()

        booking = Booking(
            id=uuid4(),
            client_id=client_id,
            practitioner_id=practitioner_id,
            scheduled_date=scheduled_date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            timezone=timezone,
            session_type=session_type,
            service_name=service_name,
            notes=notes,
            price=price,
            created_at=now,
            updated_at=now
        )

        self.bookings[booking.id] = booking
        logger.info(f"Created booking {booking.id}")

        return booking

    def confirm_booking(self, booking_id: UUID) -> Optional[Booking]:
        """Confirm a pending booking."""
        if booking_id not in self.bookings:
            return None

        booking = self.bookings[booking_id]
        if booking.status != BookingStatus.PENDING:
            return None

        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()

        logger.info(f"Confirmed booking {booking_id}")
        return booking

    def cancel_booking(
        self,
        booking_id: UUID,
        reason: str = "",
        cancelled_by: str = "client"
    ) -> tuple[Optional[Booking], float]:
        """
        Cancel a booking.

        Returns:
            Tuple of (Booking, cancellation_fee)
        """
        if booking_id not in self.bookings:
            return None, 0.0

        booking = self.bookings[booking_id]

        # Calculate cancellation fee
        appointment_datetime = datetime.combine(
            booking.scheduled_date,
            booking.start_time
        )
        hours_until = (appointment_datetime - datetime.utcnow()).total_seconds() / 3600

        if hours_until < self.FREE_CANCELLATION_HOURS:
            cancellation_fee = booking.price * self.LATE_CANCELLATION_FEE_PERCENT / 100
        else:
            cancellation_fee = 0.0

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = f"[{cancelled_by}] {reason}"
        booking.updated_at = datetime.utcnow()

        logger.info(f"Cancelled booking {booking_id}, fee: {cancellation_fee}")
        return booking, cancellation_fee

    def reschedule_booking(
        self,
        booking_id: UUID,
        new_date: date,
        new_start_time: time
    ) -> Optional[Booking]:
        """Reschedule a booking to a new date/time."""
        if booking_id not in self.bookings:
            return None

        booking = self.bookings[booking_id]

        # Calculate new end time
        new_end_time = (
            datetime.combine(new_date, new_start_time) +
            timedelta(minutes=booking.duration_minutes)
        ).time()

        booking.scheduled_date = new_date
        booking.start_time = new_start_time
        booking.end_time = new_end_time
        booking.status = BookingStatus.RESCHEDULED
        booking.updated_at = datetime.utcnow()

        logger.info(f"Rescheduled booking {booking_id} to {new_date} {new_start_time}")
        return booking

    def complete_booking(
        self,
        booking_id: UUID,
        session_note_id: Optional[UUID] = None
    ) -> Optional[Booking]:
        """Mark a booking as completed."""
        if booking_id not in self.bookings:
            return None

        booking = self.bookings[booking_id]
        booking.status = BookingStatus.COMPLETED
        booking.session_note_id = session_note_id
        booking.updated_at = datetime.utcnow()

        return booking

    def mark_no_show(self, booking_id: UUID) -> Optional[Booking]:
        """Mark a booking as no-show."""
        if booking_id not in self.bookings:
            return None

        booking = self.bookings[booking_id]
        booking.status = BookingStatus.NO_SHOW
        booking.updated_at = datetime.utcnow()

        return booking

    def get_booking(self, booking_id: UUID) -> Optional[Booking]:
        """Get a specific booking."""
        return self.bookings.get(booking_id)

    def get_client_bookings(
        self,
        client_id: UUID,
        status: Optional[BookingStatus] = None,
        upcoming_only: bool = False
    ) -> List[Booking]:
        """Get all bookings for a client."""
        bookings = [
            b for b in self.bookings.values()
            if b.client_id == client_id
        ]

        if status:
            bookings = [b for b in bookings if b.status == status]

        if upcoming_only:
            now = datetime.utcnow()
            bookings = [
                b for b in bookings
                if datetime.combine(b.scheduled_date, b.start_time) > now
            ]

        return sorted(bookings, key=lambda x: (x.scheduled_date, x.start_time))

    def get_practitioner_bookings(
        self,
        practitioner_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """Get all bookings for a practitioner."""
        bookings = [
            b for b in self.bookings.values()
            if b.practitioner_id == practitioner_id
        ]

        if start_date:
            bookings = [b for b in bookings if b.scheduled_date >= start_date]

        if end_date:
            bookings = [b for b in bookings if b.scheduled_date <= end_date]

        if status:
            bookings = [b for b in bookings if b.status == status]

        return sorted(bookings, key=lambda x: (x.scheduled_date, x.start_time))

    def get_todays_bookings(self, practitioner_id: UUID) -> List[Booking]:
        """Get today's bookings for a practitioner."""
        today = date.today()
        return self.get_practitioner_bookings(
            practitioner_id,
            start_date=today,
            end_date=today
        )

    def get_bookings_needing_reminder(self) -> List[Booking]:
        """Get bookings that need reminders sent."""
        tomorrow = date.today() + timedelta(days=1)

        return [
            b for b in self.bookings.values()
            if (b.scheduled_date == tomorrow and
                not b.reminder_sent and
                b.status == BookingStatus.CONFIRMED)
        ]

    def mark_reminder_sent(self, booking_id: UUID) -> bool:
        """Mark that a reminder was sent for a booking."""
        if booking_id not in self.bookings:
            return False

        booking = self.bookings[booking_id]
        booking.reminder_sent = True
        booking.reminder_sent_at = datetime.utcnow()
        return True

    def get_practitioner_stats(
        self,
        practitioner_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """Get booking statistics for a practitioner."""
        bookings = self.get_practitioner_bookings(
            practitioner_id,
            start_date,
            end_date
        )

        total = len(bookings)
        completed = len([b for b in bookings if b.status == BookingStatus.COMPLETED])
        cancelled = len([b for b in bookings if b.status == BookingStatus.CANCELLED])
        no_shows = len([b for b in bookings if b.status == BookingStatus.NO_SHOW])

        total_revenue = sum(
            b.price for b in bookings
            if b.status == BookingStatus.COMPLETED
        )

        return {
            "total_bookings": total,
            "completed": completed,
            "cancelled": cancelled,
            "no_shows": no_shows,
            "completion_rate": completed / total * 100 if total else 0,
            "cancellation_rate": cancelled / total * 100 if total else 0,
            "no_show_rate": no_shows / total * 100 if total else 0,
            "total_revenue": total_revenue
        }
