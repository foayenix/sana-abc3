"""
Practice Management API routes for SANA Platform.

Endpoints for scheduling, client management, sessions, and bookings.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime, date, time, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.practice.scheduling import SchedulingService
from services.practice.clients import ClientManagementService
from services.practice.sessions import SessionService
from services.practice.booking import BookingService, BookingStatus

router = APIRouter()

# Initialize services
scheduling_service = SchedulingService()
client_service = ClientManagementService()
session_service = SessionService()
booking_service = BookingService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class SetAvailabilityRequest(BaseModel):
    """Set recurring availability."""
    practitioner_id: UUID
    availability: List[Dict]  # [{day_of_week, start_time, end_time}]


class BlockTimeRequest(BaseModel):
    """Block time off."""
    practitioner_id: UUID
    block_date: date
    reason: str = ""


class AddClientRequest(BaseModel):
    """Add a client."""
    practitioner_id: UUID
    client_id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    presenting_concerns: Optional[List[str]] = None
    goals: Optional[List[str]] = None


class CreateSessionRequest(BaseModel):
    """Create a session note."""
    practitioner_id: UUID
    client_id: UUID
    session_date: datetime
    duration_minutes: int = 60
    session_type: str = "follow_up"
    booking_id: Optional[UUID] = None


class UpdateSOAPRequest(BaseModel):
    """Update SOAP notes."""
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None


class CreateBookingRequest(BaseModel):
    """Create a booking."""
    client_id: UUID
    practitioner_id: UUID
    scheduled_date: date
    start_time: str  # HH:MM
    duration_minutes: int = 60
    session_type: str = "follow_up"
    service_name: str
    price: float
    notes: str = ""


class RescheduleRequest(BaseModel):
    """Reschedule a booking."""
    new_date: date
    new_start_time: str  # HH:MM


# ============================================================================
# SCHEDULING ENDPOINTS
# ============================================================================

@router.post("/scheduling/availability")
async def set_availability(request: SetAvailabilityRequest):
    """Set recurring weekly availability for a practitioner."""
    availability = scheduling_service.set_recurring_availability(
        request.practitioner_id,
        request.availability
    )

    return {
        "message": f"Set {len(availability)} recurring time slots",
        "availability": [
            {
                "id": str(a.id),
                "day_of_week": a.day_of_week,
                "start_time": a.start_time.isoformat(),
                "end_time": a.end_time.isoformat()
            }
            for a in availability
        ]
    }


@router.get("/scheduling/available-slots/{practitioner_id}")
async def get_available_slots(
    practitioner_id: UUID,
    start_date: date,
    end_date: date,
    duration_minutes: int = 60
):
    """Get available time slots for booking."""
    slots = scheduling_service.get_available_slots(
        practitioner_id,
        start_date,
        end_date,
        duration_minutes
    )

    return {
        "practitioner_id": str(practitioner_id),
        "slot_count": len(slots),
        "slots": [
            {
                "id": str(s.id),
                "date": s.date.isoformat(),
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat()
            }
            for s in slots
        ]
    }


@router.post("/scheduling/block")
async def block_time(request: BlockTimeRequest):
    """Block a date for a practitioner."""
    success = scheduling_service.block_time(
        request.practitioner_id,
        request.block_date,
        reason=request.reason
    )

    return {
        "success": success,
        "blocked_date": request.block_date.isoformat()
    }


@router.get("/scheduling/calendar/{practitioner_id}")
async def get_calendar(practitioner_id: UUID, month: int, year: int):
    """Get calendar view for a practitioner."""
    calendar = scheduling_service.get_practitioner_calendar(
        practitioner_id,
        month,
        year
    )

    return {
        "practitioner_id": str(practitioner_id),
        "month": month,
        "year": year,
        "calendar": calendar
    }


# ============================================================================
# CLIENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/clients/add")
async def add_client(request: AddClientRequest):
    """Add a client to practitioner's roster."""
    client = client_service.add_client(
        practitioner_id=request.practitioner_id,
        client_id=request.client_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
        presenting_concerns=request.presenting_concerns,
        goals=request.goals
    )

    return {
        "id": str(client.id),
        "name": client.name,
        "email": client.email,
        "status": client.status
    }


@router.get("/clients/{practitioner_id}")
async def get_clients(
    practitioner_id: UUID,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all clients for a practitioner."""
    clients = client_service.get_practitioner_clients(
        practitioner_id,
        status=status,
        search=search
    )

    return {
        "count": len(clients),
        "clients": [
            {
                "id": str(c.id),
                "client_id": str(c.client_id),
                "name": c.name,
                "email": c.email,
                "status": c.status,
                "total_sessions": c.total_sessions,
                "last_session": c.last_session_date.isoformat() if c.last_session_date else None
            }
            for c in clients
        ]
    }


@router.get("/clients/stats/{practitioner_id}")
async def get_client_stats(practitioner_id: UUID):
    """Get client statistics for a practitioner."""
    return client_service.get_client_stats(practitioner_id)


@router.put("/clients/{client_record_id}")
async def update_client(client_record_id: UUID, updates: Dict):
    """Update client information."""
    client = client_service.update_client(client_record_id, updates)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {"message": "Client updated", "id": str(client.id)}


# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@router.post("/sessions/create")
async def create_session(request: CreateSessionRequest):
    """Create a new session note."""
    session = session_service.create_session(
        practitioner_id=request.practitioner_id,
        client_id=request.client_id,
        session_date=request.session_date,
        duration_minutes=request.duration_minutes,
        session_type=request.session_type,
        booking_id=request.booking_id
    )

    return {
        "id": str(session.id),
        "session_date": session.session_date.isoformat(),
        "session_type": session.session_type
    }


@router.put("/sessions/{session_id}/soap")
async def update_soap_notes(session_id: UUID, request: UpdateSOAPRequest):
    """Update SOAP notes for a session."""
    session = session_service.update_soap_notes(
        session_id,
        subjective=request.subjective,
        objective=request.objective,
        assessment=request.assessment,
        plan=request.plan
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": str(session.id),
        "soap": {
            "subjective": session.soap_note.subjective,
            "objective": session.soap_note.objective,
            "assessment": session.soap_note.assessment,
            "plan": session.soap_note.plan
        }
    }


@router.post("/sessions/{session_id}/treatments")
async def add_treatments(
    session_id: UUID,
    treatments: List[str] = None,
    herbs: List[str] = None,
    supplements: List[str] = None
):
    """Add treatments to a session."""
    session = session_service.add_treatments(
        session_id,
        treatments=treatments,
        herbs=herbs,
        supplements=supplements
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": str(session.id),
        "treatments": session.treatments_applied,
        "herbs": session.herbs_prescribed,
        "supplements": session.supplements_prescribed
    }


@router.post("/sessions/{session_id}/complete")
async def complete_session(session_id: UUID):
    """Mark a session as complete."""
    success = session_service.complete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session completed", "id": str(session_id)}


@router.get("/sessions/history/{practitioner_id}/{client_id}")
async def get_client_sessions(practitioner_id: UUID, client_id: UUID, limit: int = 10):
    """Get session history for a client."""
    sessions = session_service.get_client_sessions(
        practitioner_id,
        client_id,
        limit
    )

    return {
        "count": len(sessions),
        "sessions": [
            {
                "id": str(s.id),
                "date": s.session_date.isoformat(),
                "type": s.session_type,
                "duration": s.duration_minutes,
                "is_complete": s.is_complete
            }
            for s in sessions
        ]
    }


@router.get("/sessions/stats/{practitioner_id}")
async def get_session_stats(practitioner_id: UUID):
    """Get session statistics for a practitioner."""
    return session_service.get_practitioner_stats(practitioner_id)


# ============================================================================
# BOOKING ENDPOINTS
# ============================================================================

@router.post("/bookings/create")
async def create_booking(request: CreateBookingRequest):
    """Create a new booking."""
    start_time = time.fromisoformat(request.start_time)

    booking = booking_service.create_booking(
        client_id=request.client_id,
        practitioner_id=request.practitioner_id,
        scheduled_date=request.scheduled_date,
        start_time=start_time,
        duration_minutes=request.duration_minutes,
        session_type=request.session_type,
        service_name=request.service_name,
        price=request.price,
        notes=request.notes
    )

    return {
        "id": str(booking.id),
        "scheduled_date": booking.scheduled_date.isoformat(),
        "start_time": booking.start_time.isoformat(),
        "status": booking.status.value
    }


@router.post("/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: UUID):
    """Confirm a pending booking."""
    booking = booking_service.confirm_booking(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or already processed")

    return {
        "id": str(booking.id),
        "status": booking.status.value,
        "confirmed_at": booking.confirmed_at.isoformat()
    }


@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: UUID, reason: str = ""):
    """Cancel a booking."""
    booking, fee = booking_service.cancel_booking(booking_id, reason)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {
        "id": str(booking.id),
        "status": booking.status.value,
        "cancellation_fee": fee
    }


@router.post("/bookings/{booking_id}/reschedule")
async def reschedule_booking(booking_id: UUID, request: RescheduleRequest):
    """Reschedule a booking."""
    new_time = time.fromisoformat(request.new_start_time)
    booking = booking_service.reschedule_booking(
        booking_id,
        request.new_date,
        new_time
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {
        "id": str(booking.id),
        "new_date": booking.scheduled_date.isoformat(),
        "new_time": booking.start_time.isoformat(),
        "status": booking.status.value
    }


@router.post("/bookings/{booking_id}/complete")
async def complete_booking(booking_id: UUID, session_note_id: Optional[UUID] = None):
    """Mark a booking as completed."""
    booking = booking_service.complete_booking(booking_id, session_note_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"id": str(booking.id), "status": booking.status.value}


@router.get("/bookings/client/{client_id}")
async def get_client_bookings(client_id: UUID, upcoming_only: bool = False):
    """Get all bookings for a client."""
    bookings = booking_service.get_client_bookings(client_id, upcoming_only=upcoming_only)

    return {
        "count": len(bookings),
        "bookings": [
            {
                "id": str(b.id),
                "date": b.scheduled_date.isoformat(),
                "time": b.start_time.isoformat(),
                "service": b.service_name,
                "status": b.status.value
            }
            for b in bookings
        ]
    }


@router.get("/bookings/practitioner/{practitioner_id}")
async def get_practitioner_bookings(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get all bookings for a practitioner."""
    bookings = booking_service.get_practitioner_bookings(
        practitioner_id,
        start_date,
        end_date
    )

    return {
        "count": len(bookings),
        "bookings": [
            {
                "id": str(b.id),
                "client_id": str(b.client_id),
                "date": b.scheduled_date.isoformat(),
                "time": b.start_time.isoformat(),
                "duration": b.duration_minutes,
                "service": b.service_name,
                "status": b.status.value,
                "price": b.price
            }
            for b in bookings
        ]
    }


@router.get("/bookings/today/{practitioner_id}")
async def get_todays_bookings(practitioner_id: UUID):
    """Get today's bookings for a practitioner."""
    bookings = booking_service.get_todays_bookings(practitioner_id)

    return {
        "date": date.today().isoformat(),
        "count": len(bookings),
        "bookings": [
            {
                "id": str(b.id),
                "client_id": str(b.client_id),
                "time": b.start_time.isoformat(),
                "service": b.service_name,
                "status": b.status.value
            }
            for b in bookings
        ]
    }


@router.get("/bookings/stats/{practitioner_id}")
async def get_booking_stats(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get booking statistics for a practitioner."""
    return booking_service.get_practitioner_stats(
        practitioner_id,
        start_date,
        end_date
    )


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@router.get("/test-setup")
async def test_practice_management():
    """Set up test data for practice management."""
    practitioner_id = uuid4()
    client_id = uuid4()

    # Set availability (Mon-Fri 9am-5pm)
    availability = [
        {"day_of_week": i, "start_time": "09:00", "end_time": "17:00"}
        for i in range(5)
    ]
    scheduling_service.set_recurring_availability(practitioner_id, availability)

    # Add test client
    client = client_service.add_client(
        practitioner_id=practitioner_id,
        client_id=client_id,
        name="Test Client",
        email="test@example.com",
        presenting_concerns=["Stress", "Sleep issues"],
        goals=["Improve sleep quality", "Reduce anxiety"]
    )

    # Get available slots
    tomorrow = date.today() + timedelta(days=1)
    next_week = tomorrow + timedelta(days=7)
    slots = scheduling_service.get_available_slots(
        practitioner_id,
        tomorrow,
        next_week
    )

    return {
        "practitioner_id": str(practitioner_id),
        "client_id": str(client_id),
        "client_record_id": str(client.id),
        "available_slots": len(slots),
        "message": "Test data created. Use these IDs for testing other endpoints."
    }
