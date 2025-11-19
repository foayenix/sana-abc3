"""
Scheduling service for practitioner availability management.
"""

from typing import List, Dict, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class TimeSlot(BaseModel):
    """A single availability time slot."""
    id: UUID
    practitioner_id: UUID
    date: date
    start_time: time
    end_time: time
    is_available: bool = True
    is_blocked: bool = False
    booking_id: Optional[UUID] = None


class RecurringAvailability(BaseModel):
    """Recurring weekly availability pattern."""
    id: UUID
    practitioner_id: UUID
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    is_active: bool = True


class SchedulingService:
    """
    Manages practitioner scheduling and availability.

    Features:
    - Set recurring weekly availability
    - Block specific dates/times
    - Find available slots for booking
    - Handle time zones
    """

    def __init__(self):
        # In-memory storage (would be database in production)
        self.recurring_availability: Dict[UUID, List[RecurringAvailability]] = {}
        self.time_slots: Dict[UUID, TimeSlot] = {}
        self.blocked_dates: Dict[UUID, List[date]] = {}

        logger.info("SchedulingService initialized")

    def set_recurring_availability(
        self,
        practitioner_id: UUID,
        availability: List[Dict]
    ) -> List[RecurringAvailability]:
        """
        Set recurring weekly availability for a practitioner.

        Args:
            practitioner_id: Practitioner UUID
            availability: List of {day_of_week, start_time, end_time}

        Returns:
            List of created RecurringAvailability objects
        """
        created = []

        for slot in availability:
            recurring = RecurringAvailability(
                id=uuid4(),
                practitioner_id=practitioner_id,
                day_of_week=slot["day_of_week"],
                start_time=time.fromisoformat(slot["start_time"]) if isinstance(slot["start_time"], str) else slot["start_time"],
                end_time=time.fromisoformat(slot["end_time"]) if isinstance(slot["end_time"], str) else slot["end_time"]
            )
            created.append(recurring)

        self.recurring_availability[practitioner_id] = created
        logger.info(f"Set {len(created)} recurring slots for practitioner {practitioner_id}")

        return created

    def get_available_slots(
        self,
        practitioner_id: UUID,
        start_date: date,
        end_date: date,
        duration_minutes: int = 60
    ) -> List[TimeSlot]:
        """
        Get available time slots for a practitioner within date range.

        Args:
            practitioner_id: Practitioner UUID
            start_date: Start of range
            end_date: End of range
            duration_minutes: Required slot duration

        Returns:
            List of available TimeSlots
        """
        available_slots = []

        # Get recurring availability
        recurring = self.recurring_availability.get(practitioner_id, [])
        if not recurring:
            return []

        # Get blocked dates
        blocked = self.blocked_dates.get(practitioner_id, [])

        # Generate slots for each day in range
        current_date = start_date
        while current_date <= end_date:
            # Skip blocked dates
            if current_date in blocked:
                current_date += timedelta(days=1)
                continue

            # Find recurring slots for this day of week
            day_of_week = current_date.weekday()
            day_recurring = [r for r in recurring if r.day_of_week == day_of_week and r.is_active]

            for r in day_recurring:
                # Generate slots at duration_minutes intervals
                current_time = datetime.combine(current_date, r.start_time)
                end_time = datetime.combine(current_date, r.end_time)

                while current_time + timedelta(minutes=duration_minutes) <= end_time:
                    slot_end = current_time + timedelta(minutes=duration_minutes)

                    # Check if slot is already booked
                    is_booked = self._is_slot_booked(
                        practitioner_id,
                        current_date,
                        current_time.time(),
                        slot_end.time()
                    )

                    if not is_booked:
                        slot = TimeSlot(
                            id=uuid4(),
                            practitioner_id=practitioner_id,
                            date=current_date,
                            start_time=current_time.time(),
                            end_time=slot_end.time()
                        )
                        available_slots.append(slot)

                    current_time += timedelta(minutes=duration_minutes)

            current_date += timedelta(days=1)

        return available_slots

    def block_time(
        self,
        practitioner_id: UUID,
        block_date: date,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        reason: str = ""
    ) -> bool:
        """
        Block a specific date or time range.

        Args:
            practitioner_id: Practitioner UUID
            block_date: Date to block
            start_time: Optional start time (if None, blocks whole day)
            end_time: Optional end time
            reason: Reason for blocking

        Returns:
            True if blocked successfully
        """
        if practitioner_id not in self.blocked_dates:
            self.blocked_dates[practitioner_id] = []

        # For simplicity, blocking whole days
        if block_date not in self.blocked_dates[practitioner_id]:
            self.blocked_dates[practitioner_id].append(block_date)

        logger.info(f"Blocked {block_date} for practitioner {practitioner_id}: {reason}")
        return True

    def book_slot(
        self,
        practitioner_id: UUID,
        slot_date: date,
        start_time: time,
        end_time: time,
        booking_id: UUID
    ) -> Optional[TimeSlot]:
        """
        Book a specific time slot.

        Args:
            practitioner_id: Practitioner UUID
            slot_date: Date of slot
            start_time: Start time
            end_time: End time
            booking_id: Associated booking UUID

        Returns:
            Booked TimeSlot or None if not available
        """
        # Verify slot is available
        if self._is_slot_booked(practitioner_id, slot_date, start_time, end_time):
            return None

        slot = TimeSlot(
            id=uuid4(),
            practitioner_id=practitioner_id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time,
            is_available=False,
            booking_id=booking_id
        )

        self.time_slots[slot.id] = slot
        logger.info(f"Booked slot {slot.id} for booking {booking_id}")

        return slot

    def cancel_slot(self, slot_id: UUID) -> bool:
        """Cancel a booked slot."""
        if slot_id in self.time_slots:
            slot = self.time_slots[slot_id]
            slot.is_available = True
            slot.booking_id = None
            return True
        return False

    def _is_slot_booked(
        self,
        practitioner_id: UUID,
        slot_date: date,
        start_time: time,
        end_time: time
    ) -> bool:
        """Check if a time slot is already booked."""
        for slot in self.time_slots.values():
            if (slot.practitioner_id == practitioner_id and
                slot.date == slot_date and
                not slot.is_available):
                # Check for overlap
                if (start_time < slot.end_time and end_time > slot.start_time):
                    return True
        return False

    def get_practitioner_calendar(
        self,
        practitioner_id: UUID,
        month: int,
        year: int
    ) -> Dict:
        """
        Get calendar view for a practitioner.

        Returns dict with dates and their status (available, blocked, booked).
        """
        from calendar import monthrange

        _, num_days = monthrange(year, month)
        calendar_data = {}

        for day in range(1, num_days + 1):
            current_date = date(year, month, day)

            # Check if blocked
            blocked = self.blocked_dates.get(practitioner_id, [])
            if current_date in blocked:
                status = "blocked"
            else:
                # Check recurring availability
                recurring = self.recurring_availability.get(practitioner_id, [])
                has_availability = any(
                    r.day_of_week == current_date.weekday() and r.is_active
                    for r in recurring
                )

                if has_availability:
                    # Check if any slots booked
                    booked_slots = [
                        s for s in self.time_slots.values()
                        if s.practitioner_id == practitioner_id and s.date == current_date and not s.is_available
                    ]

                    if booked_slots:
                        status = "partial"
                    else:
                        status = "available"
                else:
                    status = "unavailable"

            calendar_data[current_date.isoformat()] = status

        return calendar_data
