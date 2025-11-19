"""
Widget API routes for SANA Platform.

Endpoints for widget configuration and public booking.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.widget.config import WidgetConfigService, WidgetStyle, WidgetTheme
from services.widget.public_api import WidgetPublicAPI

router = APIRouter()

# Initialize services
config_service = WidgetConfigService()
public_api = WidgetPublicAPI()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreateWidgetRequest(BaseModel):
    """Create a widget."""
    practitioner_id: UUID
    slug: Optional[str] = None
    services: Optional[List[Dict]] = None


class UpdateWidgetRequest(BaseModel):
    """Update widget settings."""
    style: Optional[str] = None
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    border_radius: Optional[int] = None
    show_sana_branding: Optional[bool] = None
    custom_logo_url: Optional[str] = None
    custom_header: Optional[str] = None
    custom_footer: Optional[str] = None
    show_profile: Optional[bool] = None
    show_bio: Optional[bool] = None
    show_credentials: Optional[bool] = None
    show_reviews: Optional[bool] = None
    show_sana_index: Optional[bool] = None
    show_prices: Optional[bool] = None
    booking_window_days: Optional[int] = None
    min_notice_hours: Optional[int] = None
    buffer_minutes: Optional[int] = None
    require_payment: Optional[bool] = None
    allow_telehealth: Optional[bool] = None
    confirmation_message: Optional[str] = None
    is_active: Optional[bool] = None


class AddServiceRequest(BaseModel):
    """Add a service to widget."""
    name: str
    description: str
    duration_minutes: int
    price: float
    currency: str = "GBP"


class CreateBookingRequest(BaseModel):
    """Create a booking through widget."""
    service_id: UUID
    service_name: str
    start_time: datetime
    duration_minutes: int
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    is_telehealth: bool = False
    amount: float = 0.0
    currency: str = "GBP"
    client_notes: Optional[str] = None


class RescheduleRequest(BaseModel):
    """Reschedule a booking."""
    new_start_time: datetime


# ============================================================================
# WIDGET CONFIGURATION ENDPOINTS (Authenticated)
# ============================================================================

@router.post("/config")
async def create_widget(request: CreateWidgetRequest):
    """Create a new widget for a practitioner."""
    widget = config_service.create_widget(
        practitioner_id=request.practitioner_id,
        slug=request.slug,
        services=request.services
    )

    return {
        "id": str(widget.id),
        "widget_key": widget.widget_key,
        "slug": widget.slug,
        "practitioner_id": str(widget.practitioner_id)
    }


@router.get("/config/{widget_id}")
async def get_widget_config(widget_id: UUID):
    """Get widget configuration."""
    widget = config_service.get_widget(widget_id)

    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    return {
        "id": str(widget.id),
        "practitioner_id": str(widget.practitioner_id),
        "widget_key": widget.widget_key,
        "slug": widget.slug,
        "style": widget.style.value,
        "theme": widget.theme.value,
        "primary_color": widget.primary_color,
        "secondary_color": widget.secondary_color,
        "show_sana_branding": widget.show_sana_branding,
        "booking_window_days": widget.booking_window_days,
        "min_notice_hours": widget.min_notice_hours,
        "require_payment": widget.require_payment,
        "services": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "duration_minutes": s.duration_minutes,
                "price": s.price,
                "currency": s.currency
            }
            for s in widget.services
        ],
        "is_active": widget.is_active
    }


@router.get("/config/practitioner/{practitioner_id}")
async def get_practitioner_widget(practitioner_id: UUID):
    """Get widget for a practitioner."""
    widget = config_service.get_practitioner_widget(practitioner_id)

    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    return {
        "id": str(widget.id),
        "widget_key": widget.widget_key,
        "slug": widget.slug
    }


@router.put("/config/{widget_id}")
async def update_widget(widget_id: UUID, request: UpdateWidgetRequest):
    """Update widget configuration."""
    try:
        updates = {k: v for k, v in request.dict().items() if v is not None}
        widget = config_service.update_widget(widget_id, updates)

        return {
            "id": str(widget.id),
            "updated_at": widget.updated_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config/{widget_id}/services")
async def add_service(widget_id: UUID, request: AddServiceRequest):
    """Add a service to widget."""
    try:
        service = config_service.add_service(
            widget_id,
            request.name,
            request.description,
            request.duration_minutes,
            request.price,
            request.currency
        )

        return {
            "id": str(service.id),
            "name": service.name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/config/{widget_id}/services/{service_id}")
async def remove_service(widget_id: UUID, service_id: UUID):
    """Remove a service from widget."""
    success = config_service.remove_service(widget_id, service_id)

    if not success:
        raise HTTPException(status_code=404, detail="Widget or service not found")

    return {"message": "Service removed"}


@router.get("/config/{widget_id}/embed-code")
async def get_embed_code(widget_id: UUID, base_url: str = "https://sana.health"):
    """Get embed codes for the widget."""
    try:
        return config_service.generate_embed_code(widget_id, base_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/{widget_id}/links")
async def get_shareable_links(widget_id: UUID, base_url: str = "https://sana.health"):
    """Get shareable booking links."""
    try:
        return config_service.generate_shareable_link(widget_id, base_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config/{widget_id}/regenerate-key")
async def regenerate_widget_key(widget_id: UUID):
    """Regenerate widget key (invalidates old embeds)."""
    try:
        new_key = config_service.regenerate_widget_key(widget_id)
        return {"widget_key": new_key}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/{widget_id}/analytics")
async def get_widget_analytics(widget_id: UUID):
    """Get widget analytics."""
    analytics = config_service.get_analytics(widget_id)

    if not analytics:
        raise HTTPException(status_code=404, detail="Widget not found")

    return {
        "total_views": analytics.total_views,
        "unique_visitors": analytics.unique_visitors,
        "bookings_started": analytics.bookings_started,
        "bookings_completed": analytics.bookings_completed,
        "conversion_rate": analytics.conversion_rate,
        "top_referrers": analytics.top_referrers
    }


# ============================================================================
# PUBLIC WIDGET ENDPOINTS (No Authentication Required)
# ============================================================================

@router.get("/public/{widget_key}")
async def get_widget_data(widget_key: str, request: Request):
    """
    Get widget data for embedding.

    This is the main endpoint called by embedded widgets.
    """
    widget = config_service.get_widget_by_key(widget_key)

    if not widget or not widget.is_active:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Track view
    referrer = request.headers.get("referer", "direct")
    config_service.track_view(widget.id, referrer)

    # Get practitioner profile
    profile = public_api.get_practitioner_profile(widget.practitioner_id)

    # Get reviews if enabled
    reviews = []
    if widget.show_reviews:
        reviews = public_api.get_reviews(widget.practitioner_id)

    return {
        "widget": {
            "style": widget.style.value,
            "theme": widget.theme.value,
            "primary_color": widget.primary_color,
            "secondary_color": widget.secondary_color,
            "border_radius": widget.border_radius,
            "font_family": widget.font_family,
            "show_sana_branding": widget.show_sana_branding,
            "custom_logo_url": widget.custom_logo_url,
            "custom_header": widget.custom_header,
            "custom_footer": widget.custom_footer
        },
        "display": {
            "show_profile": widget.show_profile,
            "show_bio": widget.show_bio,
            "show_credentials": widget.show_credentials,
            "show_reviews": widget.show_reviews,
            "show_sana_index": widget.show_sana_index,
            "show_prices": widget.show_prices
        },
        "booking": {
            "booking_window_days": widget.booking_window_days,
            "min_notice_hours": widget.min_notice_hours,
            "require_payment": widget.require_payment,
            "allow_telehealth": widget.allow_telehealth,
            "confirmation_message": widget.confirmation_message
        },
        "practitioner": {
            "id": str(profile.id),
            "name": profile.name,
            "title": profile.title,
            "bio": profile.bio if widget.show_bio else None,
            "profile_image": profile.profile_image,
            "specialties": profile.specialties,
            "credentials": profile.credentials if widget.show_credentials else [],
            "city": profile.city,
            "sana_index": profile.sana_index if widget.show_sana_index else None,
            "average_rating": profile.average_rating,
            "total_reviews": profile.total_reviews,
            "offers_telehealth": profile.offers_telehealth
        },
        "services": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "duration_minutes": s.duration_minutes,
                "price": s.price if widget.show_prices else None,
                "currency": s.currency
            }
            for s in widget.services if s.is_active
        ],
        "reviews": reviews
    }


@router.get("/public/{widget_key}/availability")
async def get_availability(
    widget_key: str,
    service_id: UUID,
    start_date: date,
    end_date: date,
    telehealth_only: bool = False
):
    """Get available booking slots."""
    widget = config_service.get_widget_by_key(widget_key)

    if not widget or not widget.is_active:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Find service to get duration
    service = next(
        (s for s in widget.services if s.id == service_id),
        None
    )

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    slots = public_api.get_available_slots(
        practitioner_id=widget.practitioner_id,
        service_id=service_id,
        start_date=start_date,
        end_date=end_date,
        duration_minutes=service.duration_minutes,
        buffer_minutes=widget.buffer_minutes,
        min_notice_hours=widget.min_notice_hours,
        telehealth_only=telehealth_only
    )

    return {
        "service_id": str(service_id),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "slots": [
            {
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat(),
                "is_telehealth": s.is_telehealth
            }
            for s in slots
        ]
    }


@router.post("/public/{widget_key}/book")
async def create_booking(widget_key: str, request: CreateBookingRequest):
    """Create a booking through the widget."""
    widget = config_service.get_widget_by_key(widget_key)

    if not widget or not widget.is_active:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Track booking started
    config_service.track_booking_started(widget.id)

    # Validate slot is available
    is_available = public_api.validate_slot_available(
        widget.practitioner_id,
        request.start_time,
        request.duration_minutes
    )

    if not is_available:
        raise HTTPException(status_code=409, detail="Slot is no longer available")

    # Create booking
    booking = public_api.create_booking(
        widget_id=widget.id,
        practitioner_id=widget.practitioner_id,
        service_id=request.service_id,
        service_name=request.service_name,
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
        client_name=request.client_name,
        client_email=request.client_email,
        client_phone=request.client_phone,
        is_telehealth=request.is_telehealth,
        amount=request.amount,
        currency=request.currency,
        client_notes=request.client_notes
    )

    # Track booking completed
    config_service.track_booking_completed(widget.id)

    result = {
        "booking_id": str(booking.id),
        "confirmation_code": booking.confirmation_code,
        "status": booking.status,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "confirmation_message": widget.confirmation_message
    }

    # Include payment info if required
    if widget.require_payment and booking.amount > 0:
        payment = public_api.create_payment_intent(
            booking.id,
            booking.amount,
            booking.currency
        )
        result["payment"] = payment

    return result


@router.get("/public/booking/{confirmation_code}")
async def get_booking_by_code(confirmation_code: str):
    """Get booking by confirmation code."""
    booking = public_api.get_booking_by_code(confirmation_code)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {
        "booking_id": str(booking.id),
        "confirmation_code": booking.confirmation_code,
        "service_name": booking.service_name,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "duration_minutes": booking.duration_minutes,
        "is_telehealth": booking.is_telehealth,
        "status": booking.status,
        "client_name": booking.client_name,
        "client_email": booking.client_email
    }


@router.post("/public/booking/{booking_id}/cancel")
async def cancel_booking(booking_id: UUID, reason: str = ""):
    """Cancel a booking."""
    success = public_api.cancel_booking(booking_id, reason)

    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"message": "Booking cancelled"}


@router.post("/public/booking/{booking_id}/reschedule")
async def reschedule_booking(booking_id: UUID, request: RescheduleRequest):
    """Reschedule a booking."""
    booking = public_api.reschedule_booking(booking_id, request.new_start_time)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {
        "booking_id": str(booking.id),
        "new_start_time": booking.start_time.isoformat(),
        "new_end_time": booking.end_time.isoformat()
    }


@router.post("/public/booking/{booking_id}/confirm-payment")
async def confirm_booking_payment(booking_id: UUID):
    """Confirm payment for a booking."""
    success = public_api.confirm_payment(booking_id)

    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"payment_status": "paid"}


# ============================================================================
# BOOKING SYNC ENDPOINTS (For Platform Integration)
# ============================================================================

@router.get("/bookings/practitioner/{practitioner_id}")
async def get_practitioner_widget_bookings(
    practitioner_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Get all widget bookings for a practitioner.

    Used to sync widget bookings with the main SANA platform.
    """
    bookings = public_api.get_practitioner_bookings(
        practitioner_id,
        start_date,
        end_date
    )

    return {
        "count": len(bookings),
        "bookings": [
            {
                "id": str(b.id),
                "confirmation_code": b.confirmation_code,
                "service_name": b.service_name,
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "client_name": b.client_name,
                "client_email": b.client_email,
                "client_phone": b.client_phone,
                "is_telehealth": b.is_telehealth,
                "amount": b.amount,
                "currency": b.currency,
                "payment_status": b.payment_status,
                "status": b.status,
                "created_at": b.created_at.isoformat()
            }
            for b in bookings
        ]
    }


# ============================================================================
# SHAREABLE PAGE ENDPOINT
# ============================================================================

@router.get("/book/{slug}")
async def get_booking_page_data(slug: str):
    """
    Get data for shareable booking page.

    This endpoint is used by the SANA booking page at /book/{slug}.
    """
    widget = config_service.get_widget_by_slug(slug)

    if not widget or not widget.is_active:
        raise HTTPException(status_code=404, detail="Booking page not found")

    # Track view
    config_service.track_view(widget.id)

    # Get full data using public endpoint logic
    profile = public_api.get_practitioner_profile(widget.practitioner_id)
    reviews = public_api.get_reviews(widget.practitioner_id) if widget.show_reviews else []

    return {
        "widget_key": widget.widget_key,
        "practitioner": {
            "id": str(profile.id),
            "name": profile.name,
            "title": profile.title,
            "bio": profile.bio,
            "profile_image": profile.profile_image,
            "specialties": profile.specialties,
            "credentials": profile.credentials,
            "city": profile.city,
            "sana_index": profile.sana_index,
            "average_rating": profile.average_rating,
            "total_reviews": profile.total_reviews
        },
        "services": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "duration_minutes": s.duration_minutes,
                "price": s.price,
                "currency": s.currency
            }
            for s in widget.services if s.is_active
        ],
        "settings": {
            "booking_window_days": widget.booking_window_days,
            "min_notice_hours": widget.min_notice_hours,
            "require_payment": widget.require_payment,
            "allow_telehealth": widget.allow_telehealth
        },
        "branding": {
            "primary_color": widget.primary_color,
            "secondary_color": widget.secondary_color,
            "custom_logo_url": widget.custom_logo_url
        },
        "reviews": reviews
    }
